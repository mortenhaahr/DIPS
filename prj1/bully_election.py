from asyncio.windows_events import NULL
from enum import Enum
import queue
import threading
import time
import random
import bully_election_classes

# from mpi4py import MPI

#node_ids = range(MPI.COMM_WORLD.size)
#highest_id = max(node_ids)
#comm = MPI.COMM_WORLD


ID_array = bully_election_classes.ProcessID()
election_timer = None

recv_queue = []

election_count = 0
broadcast_count = 0
ok_count = 0
total_count = 0

def Construct_msg(sender, type, data = None):
    return bully_election_classes.Message(sender=sender,type=type,data=data)

def Coordinate(comm): 
    global broadcast_count
    for rank in range(comm.size):
        if rank != comm.rank:
            comm.send(Construct_msg(comm.rank, bully_election_classes.Type.COORDINATOR,ID_array.getID(comm.rank)), rank)
            broadcast_count += 1
    print(f"Done broadcasting leader on node {comm.rank}.")

def HoldElection():
    global election_count
    my_id = ID_array.getID(comm.rank)
    global election_timer
    election_timer = bully_election_classes.myTimer(1,Coordinate)

    for other_rank, id in enumerate(ID_array.ID_array):
        if id > my_id:
            comm.send(Construct_msg(comm.rank, bully_election_classes.Type.ELECTION), other_rank)
            election_count += 1

def Recieve_Handle(Message):
    if bully_election_classes.Massage.type == bully_election_classes.Type.Election:
        global ok_count
        comm.send(Construct_msg(comm.rank, bully_election_classes.Type.OK),Message.sender)
        ok_count += 1
        HoldElection()
    elif Message.type == bully_election_classes.Type.OK:
        global election_timer
        election_timer.kill()
    elif Message.type == bully_election_classes.Type.COORDINATOR:
        print(f"Node: {ID_array.getID(comm.rank)} acknowledge {ID_array.getID(Message.sender)} as leader")
        global election_count,broadcast_count, ok_count
        msg_count = election_count + broadcast_count + ok_count
        comm.send(Construct_msg(comm.rank,bully_election_classes.Type.MSG_COUNT,msg_count),Message.sender)
    elif Message.type == bully_election_classes.Type.MSG_COUNT:
        global total_count
        print(f"Node: {ID_array.getID(comm.rank)} counted {ID_array.getID(Message.data)} from {ID_array.getID(Message.sender)}")
        total_count += Message.data
        print(f"Node: {ID_array.getID(comm.rank)} counted {total_count} in total")


def receive():
    my_id = ID_array.getID(comm.rank)
    print(f"Node {my_id} ready to recv.")
    while(True):
        data = comm.recv()
        recv_queue.append(data)

def dispatch():
    while(True):
        try:
            next = recv_queue.pop(0)
        except IndexError:
            time.sleep(1)
            continue
        Recieve_Handle(next)

def main():
    if ID_array.getLowestID() == ID_array.getID(comm.rank):
        HoldElection()

    recv_t = threading.Thread(target=receive)
    recv_t.start()
    dispatch()

if __name__ == "__main__":
    main()

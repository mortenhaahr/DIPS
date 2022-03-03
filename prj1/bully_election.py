#!/bin/python3

import threading
import time
import bully_election_classes

from mpi4py import MPI

comm = MPI.COMM_WORLD

ID_array = bully_election_classes.ProcessID(comm)
election_timer = None

recv_queue = []

election_count = 0
broadcast_count = 0
ok_count = 0
total_count = 0

def Construct_msg(sender, type, data = None):
    return bully_election_classes.Message(sender=sender,type=type,data=data)

def Coordinate(): 
    global broadcast_count
    global total_count
    global ok_count
    global election_count

    for rank in range(comm.size):
        if rank != comm.rank:
            comm.send(Construct_msg(comm.rank, bully_election_classes.Type.COORDINATOR,ID_array.getID(comm.rank)), rank)
            broadcast_count += 1
            
    print(f"Done broadcasting leader on node {comm.rank}.")
    total_count += broadcast_count + ok_count + election_count

election_has_been_held = False

def HoldElection():
    global election_timer
    global election_has_been_held

    # early out
    if (election_has_been_held): 
        return

    election_has_been_held = True

    my_id = ID_array.getID(comm.rank)
    
    election_timer = bully_election_classes.myTimer(5,Coordinate)

    for other_rank, id in enumerate(ID_array.ID_array):
        if id > my_id:
            global election_count
            comm.send(Construct_msg(comm.rank, bully_election_classes.Type.ELECTION), other_rank)
            election_count += 1



def Recieve_Handle(Message):
    global ok_count

    if Message.type == bully_election_classes.Type.ELECTION:
        comm.send(Construct_msg(comm.rank, bully_election_classes.Type.OK),Message.sender)
        ok_count += 1
        HoldElection()
    elif Message.type == bully_election_classes.Type.OK:
        global election_timer
        election_timer.kill()
    elif Message.type == bully_election_classes.Type.COORDINATOR:
        global election_count
        global broadcast_count
        print(f"Node: {ID_array.getID(comm.rank)} acknowledge {ID_array.getID(Message.sender)} as leader")
        msg_count = election_count + broadcast_count + ok_count
        comm.send(Construct_msg(comm.rank,bully_election_classes.Type.MSG_COUNT,msg_count),Message.sender)
    elif Message.type == bully_election_classes.Type.MSG_COUNT:
        global total_count
        print(f"Node: {ID_array.getID(comm.rank)} counted {Message.data} from {ID_array.getID(Message.sender)}")
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
        
        print(f"Node: {ID_array.getID(comm.rank)} got {next}")
        Recieve_Handle(next)

def main():
    
    recv_t = threading.Thread(target=receive)
    recv_t.start()
    
    print(f"Lowest ID: {ID_array.getLowestID()}. My ID: {ID_array.getID(comm.rank)} My Rank: {comm.rank}")

    if ID_array.getLowestID() == ID_array.getID(comm.rank):
        HoldElection()

    dispatch()

if __name__ == "__main__":
    main()

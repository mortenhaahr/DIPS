import threading
import time
import bully_election_classes
from mpi4py import MPI

comm = MPI.COMM_WORLD


ID_array = bully_election_classes.ProcessID(comm)
election_timer = None
max_id = 0

recv_queue = []

election_count = 0
broadcast_count = 0
ok_count = 0
total_count = 0

def Construct_msg(sender, type, data = None):
    return bully_election_classes.Message(sender=sender,type=type,data=data)

def Coordinate(): 
    global broadcast_count, total_count
    for rank in range(comm.size):
        if rank != comm.rank:
            comm.send(Construct_msg(comm.rank, bully_election_classes.Type.COORDINATOR, max_id), rank)
            broadcast_count += 1
    print(f"Done broadcasting leader on node {comm.rank}.")
    total_count += broadcast_count + ok_count + election_count


def HoldElection():
    global election_count, max_id, election_timer
    my_id = ID_array.getID(comm.rank)
    max_id = my_id 
    election_timer = bully_election_classes.myTimer(2,Coordinate)

    for other_rank, id in enumerate(ID_array.ID_array):
        if id > my_id:
            comm.send(Construct_msg(comm.rank, bully_election_classes.Type.ELECTION), other_rank)
            election_count += 1

def Recieve_Handle(Message):
    global election_count,broadcast_count, ok_count, total_count, max_id
    if Message.type == bully_election_classes.Type.ELECTION:
        comm.send(Construct_msg(comm.rank, bully_election_classes.Type.OK, ID_array.getID(comm.rank)),Message.sender)
        ok_count += 1
    elif Message.type == bully_election_classes.Type.OK:
        if Message.data > max_id:
            max_id = Message.data
    elif Message.type == bully_election_classes.Type.COORDINATOR:
        print(f"Node: {ID_array.getID(comm.rank)} acknowledge {Message.data} as leader")
        msg_count = election_count + broadcast_count + ok_count
        comm.send(Construct_msg(comm.rank,bully_election_classes.Type.MSG_COUNT,msg_count),Message.sender)
    elif Message.type == bully_election_classes.Type.MSG_COUNT:
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

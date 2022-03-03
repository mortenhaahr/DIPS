from asyncio.windows_events import NULL
from enum import Enum
import queue
import threading
import time
import random
# from mpi4py import MPI

#node_ids = range(MPI.COMM_WORLD.size)
#highest_id = max(node_ids)
#comm = MPI.COMM_WORLD

seed = 42
ID_array = ProcessID()
election_timer = None

recv_queue = []

election_count = 0
broadcast_count = 0
ok_count = 0
total_count = 0

class Message():
    def __init__(self, sender, type, data = None):
        self.sender = sender
        self.type = type
        self.data = data
        

    def __repr__(self):
        return str({"Sender": self.sender, "type": self.type, "data": self.data})

class Type(Enum):
    ELECTION = 0
    OK = 1
    COORDINATOR = 2
    MSG_COUNT = 3

def Construct_msg(sender, type, data = None):
    return Message(sender=sender,type=type,data=data)

class myTimer():
    def __init__(self,seconds,func):
        self.T = threading.Timer(seconds, func)
        self.T.start()

    def kill(self):
        self.T.cancel()

class ProcessID():
    def __init__(self):
        random.seed(seed)
        #self.ID_array = random.sample(range(1,comm.size+20),comm.size)
        self.ID_array = random.sample(range(1,8+20),8)

    def getID(self, rank):
        return self.ID_array[rank]

    def getLowestID(self):
        return min(self.ID_array)

    def __repr__(self):
        return str({"ID_array": self.ID_array})
    

def Coordinate(comm): 
    global broadcast_count
    for rank in range(comm.size):
        if rank != comm.rank:
            comm.send(Construct_msg(comm.rank, Type.COORDINATOR,ID_array.getID(comm.rank)), rank)
            broadcast_count += 1
    print(f"Done broadcasting leader on node {comm.rank}.")

def HoldElection():
    global election_count
    my_id = ID_array.getID(comm.rank)
    global election_timer
    election_timer = myTimer(1,Coordinate)

    for other_rank, id in enumerate(ID_array.ID_array):
        if id > my_id:
            comm.send(Construct_msg(comm.rank, Type.ELECTION), other_rank)
            election_count += 1

def Recieve_Handle(Message):
    if Massage.type == Type.Election:
        global ok_count
        comm.send(Construct_msg(comm.rank, Type.OK),Message.sender)
        ok_count += 1
        HoldElection()
    elif Message.type == Type.OK:
        global election_timer
        election_timer.kill()
    elif Message.type == Type.COORDINATOR:
        print(f"Node: {ID_array.getID(comm.rank)} acknowledge {ID_array.getID(Message.sender)} as leader")
        global election_count,broadcast_count, ok_count
        msg_count = election_count + broadcast_count + ok_count
        comm.send(Construct_msg(comm.rank,Type.MSG_COUNT,msg_count),Message.sender)
    elif Message.type == Type.MSG_COUNT:
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

from enum import Enum
import threading
import time
# from mpi4py import MPI

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
    def __init__(self,seconds):
        self.T = threading.Timer(seconds, Coordinate)
        self.T.start()

    def kill(self):
        self.T.cancel()

def Coordinate(): 
    print("Coordinateing")


mt = myTimer(2)        
time.sleep(5)
mt.kill()


mt2 = myTimer(2)        
time.sleep(1)
mt2.kill()

# max_rank = MPI.COMM_WORLD.size - 1
# comm = MPI.COMM_WORLD



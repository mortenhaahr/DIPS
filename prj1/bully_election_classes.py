from enum import Enum
import threading
import random

seed = 42

class Message():
    def __init__(self, sender, type, data = None):
        self.sender = sender
        self.type = type
        self.data = data
        

    def __repr__(self):
        return str({"Sender": self.sender, "type": self.type.name, "data": self.data})

class MsgType(Enum):
    ELECTION = 0
    OK = 1
    COORDINATOR = 2
    MSG_COUNT = 3

class Timer():
    def __init__(self,seconds,func):
        self.T = threading.Timer(seconds, func)
        self.T.start()

    def kill(self):
        self.T.cancel()

class SystemIDs():
    def __init__(self, comm):
        random.seed(seed)
        self.ID_array = random.sample(range(1,comm.size+20),comm.size)

    def get_id(self, rank):
        return self.ID_array[rank]

    def get_lowest_id(self):
        return min(self.ID_array)

    def __repr__(self):
        return str({"ID_array": self.ID_array})
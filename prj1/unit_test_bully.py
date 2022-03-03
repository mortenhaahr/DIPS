from concurrent.futures import thread
from telnetlib import EL
import unittest as unit
import bully_election 
from time import sleep

class mockCounter():
    def __init__(self):
        self.counter = 0

    def incrementCounter(self):
        self.counter += 1

    def getCounter(self):
        return self.counter

class Testing(unit.TestCase):
    def entry(self):
        global seed, ID_array, election_timer,recv_queue,election_count,broadcast_count,ok_count,total_count
        seed = 42
        ID_array = bully_election.ProcessID()
        election_timer = None

        recv_queue = []

        election_count = 0
        broadcast_count = 0
        ok_count = 0
        total_count = 0

    def test_Message(self):
        uut = bully_election.Message(42,bully_election.Type.OK)
        self.assertEqual(uut.sender, 42)
        self.assertEqual(uut.type,bully_election.Type.OK)

    def test_timer(self):
        mc = mockCounter()
        self.assertEqual(mc.getCounter(),0) #Assert that counter is zero
        uut = bully_election.myTimer(1,mc.incrementCounter)
        self.assertEqual(mc.getCounter(),0)
        sleep(0.9)
        self.assertEqual(mc.getCounter(),0)
        sleep(0.2)
        self.assertEqual(mc.getCounter(),1)

    def test_timerKill(self):
        mc = mockCounter()
        uut = bully_election.myTimer(1,mc.incrementCounter)
        self.assertEqual(mc.getCounter(),0)
        uut.kill()
        sleep(1.1)
        self.assertEqual(mc.getCounter(),0)

    def test_Coordinate(self):
        self.entry()
        init_count = broadcast_count
        


    



if __name__ == '__main__':
    unit.main()


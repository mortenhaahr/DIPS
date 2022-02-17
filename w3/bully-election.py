#!/bin/python3 
from mpi4py import MPI
import time
import threading

queue = []
election_done = False

node_ids = range(MPI.COMM_WORLD.size)
highest_id = max(node_ids)
comm = MPI.COMM_WORLD
election_count = 0
ack_count = 0
broadcast_count = 0

E_type = "Election"
L_type = "Leader"
A_type = "Ack"

class Base():
    def __init__(self, rank, id):
        self.id = id
        self.rank = rank

class ElectionMsg(Base):
    def get_msg(self):
        return [E_type, self.rank, self.id]

class LeaderMsg(Base):
    def get_msg(self):
        return [L_type, self.rank, self.id]

class AckMsg(Base):
    def get_msg(self):
        return [A_type, self.rank, self.id]

def election():
    global election_count
    my_id = node_ids[comm.rank]
    highest_recv = -1
    for other_rank, id in enumerate(node_ids):
        if id > my_id:
            comm.send(ElectionMsg(comm.rank, my_id).get_msg(), other_rank)
            election_count += 1

def broadcast_leader():
    global broadcast_count
    my_id = node_ids[comm.rank]
    for rank in range(comm.size):
        if rank != comm.rank:
            comm.send(LeaderMsg(comm.rank, my_id).get_msg(), rank)
            broadcast_count += 1
    print(f"Done broadcasting leader on node {comm.rank}.")

def dispatch():
    global election_done, ack_count
    is_leader = True
    acks_received = []
    times_slept = 0
    my_id = node_ids[comm.rank]
    while(True):
        try:
            next = queue.pop(0)
        except IndexError:
            time.sleep(1)
            if election_done:
                times_slept += 1
                if times_slept == 5 and is_leader:
                    broadcast_leader()
                    return
            continue
        print(f"Node {comm.rank} received: {next}")
        if(next[0] == E_type):
            # Send ack and see if we are doing our own election
            comm.send(AckMsg(comm.rank, my_id).get_msg(), next[1])
            ack_count += 1
            if not election_done:
                election()
                election_done = True
        elif(next[0] == L_type):
            return
        elif(next[0] == A_type):
            is_leader = False


def receive():
    my_id = node_ids[comm.rank]
    print(f"Node {comm.rank} ready to recv.")
    while(True):
        data = comm.recv()
        queue.append(data)

def main():
    global election_count, ack_count, broadcast_count
    if comm.rank ==  0:
        election()
        global election_done
        election_done = True

    recv_t = threading.Thread(target=receive)
    recv_t.start()
    dispatch()
    recv_t.join(timeout=1.0)
    print(f"Node {comm.rank} done. Election count: {election_count}. Ack count {ack_count}. Broadcast count {broadcast_count}.")
    

if __name__ == "__main__":
    main()

#!/bin/python3 
from mpi4py import MPI
import numpy as np
import time

# Something is wrong. Our acknowledgement part is baad... To be fixed.

node_ids = range(MPI.COMM_WORLD.size)
highest_node = max(node_ids)

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

def election(comm):
    my_id = node_ids[comm.rank]
    highest_recv = -1
    for other_rank, id in enumerate(node_ids):
        if id > my_id:
            comm.send(ElectionMsg(comm.rank, my_id).get_msg(), other_rank)
            # print(f'on node {comm.rank} waiting for ack')
            # data = comm.recv(source=other_rank)
            # print(f'on node {comm.rank} we received: {data}')
            # if data[2] > highest_recv:
            #     highest_recv = data[2]
    if my_id == highest_node:
        broadcast_leader(comm)

def acknowledge(comm, dest_id):
    my_id = node_ids[comm.rank]
    comm.send(AckMsg(comm.rank, my_id).get_msg(), node_ids.index(dest_id))

def broadcast_leader(comm):
    my_id = node_ids[comm.rank]
    for rank in range(comm.size):
        comm.send(LeaderMsg(comm.rank, my_id).get_msg(), rank)
    print(f"Done broadcasting leader on node {comm.rank}.")
    while(True):
        data = comm.recv()
        comm.send(AckMsg(comm.rank, my_id).get_msg(), data[1])

def main():
    comm = MPI.COMM_WORLD
    rank = comm.rank
    size = comm.size
    shared = (rank+1)*5
    
    if rank == 0:
        election(comm)

    election_progress = False
    while(True):
        my_id = node_ids[comm.rank]
        print(f"Node {comm.rank} ready to recv")
        data = comm.recv()
        if(data[0] == E_type):
            #comm.send(AckMsg(comm.rank, my_id).get_msg(), data[1])
            print(f'on node {rank} we received: {data}')
            if(not election_progress):
                election(comm)
                election_progress = True
        elif(data[0] == L_type):
            print(f"Received leader broadcast on node {comm.rank}.")
            while(True):
                data = comm.recv()
                #comm.send(AckMsg(comm.rank, my_id).get_msg(), data[1])
        time.sleep(1)

if __name__ == "__main__":
    main()

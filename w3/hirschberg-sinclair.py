#!/bin/python3 
from mpi4py import MPI
import time
import threading

queue = []
election_done = False

# 100 unique random numbers. Only N first will be used, where N is MPI.COMM_WORLD.size
node_ids = [8001, 7224, 7424, 6760, 4431, 116, 1722, 4308, 3744, 7136, 5348, 6426, 4045, 6489, 7386, 5498, 2789, 7334, 4333, 8759, 8735, 9815, 2057, 9638, 2658, 924, 5571, 5462, 6801, 255, 7028, 5659, 7807, 4549, 8466, 3596, 9309, 9302, 7225, 6034, 7376, 4197, 8539, 2764, 9475, 9827, 5149, 9721, 926, 4039, 5238, 6943, 3795, 1192, 9028, 4409, 2557, 5663, 4913, 1376, 8557, 3758, 7948, 7251, 6074, 6566, 2007, 2214, 917, 9935, 956, 3305, 5286, 7764, 4753, 139, 2744, 6320, 4743, 6086, 62, 5801, 6242, 870, 2279, 2371, 4304, 8628, 3969, 2533, 2200, 7241, 3851, 1660, 6598, 2, 8318, 877, 5184, 9176]
max_rank = MPI.COMM_WORLD.size - 1
comm = MPI.COMM_WORLD
both_count = 0
pass_count = 0
echo_count = 0
leader_count = 0

B_type = "Both" # Send messages in both directions
P_type = "Pass" # Pass received message on
E_type = "Echo" # Send response message back
L_type = "Leader" # Broadcast leader

class Message():
    def __init__(self, type, rank, id, phase, hop = 1, dir = None):
        self.type = type
        self.id = id
        self.rank = rank
        self.phase = phase
        self.hop = hop
        self.dir = dir

    def __repr__(self):
        return str({"type": self.type, "id": self.id, "rank": self.rank, "phase": self.phase, "hop": self.hop, "dir": self.dir})

def election(phase):
    global both_count
    my_id = node_ids[comm.rank]
    left_rank = comm.rank - 1 if comm.rank != 0 else max_rank
    right_rank = comm.rank + 1 if comm.rank != max_rank else 0

    comm.send(Message(B_type, comm.rank, my_id, phase, dir="L"), left_rank)
    comm.send(Message(B_type, comm.rank, my_id, phase, dir="R"), right_rank)
    both_count += 2

def leader_broadcast():
    global broadcast_count, leader_count
    my_id = node_ids[comm.rank]
    left_rank = comm.rank - 1 if comm.rank != 0 else max_rank
    right_rank = comm.rank + 1 if comm.rank != max_rank else 0

    print(f"\nI AM THE LEADER: rank: {comm.rank}. id: {my_id}\n")

    comm.send(Message(L_type, comm.rank, my_id, phase=0, dir="L"), left_rank)
    comm.send(Message(L_type, comm.rank, my_id, phase=0, dir="R"), right_rank)
    leader_count += 2

def echo_or_pass(msg):
    global pass_count, echo_count
    my_id = node_ids[comm.rank]
    if my_id > msg.id:
        return
    if msg.hop == 2**msg.phase:
        dir = "L" if msg.dir == "R" else "R"
        comm.send(Message(E_type, comm.rank, msg.id, msg.phase, msg.hop - 1, dir), msg.rank)
        if msg.hop == 0:
            print(f"This is where we done goofed: {msg}")
        echo_count += 1
    else: # Pass message
        if msg.dir == "R":
            receiver_rank = comm.rank + 1 if comm.rank != max_rank else 0 # Right
        else:
            receiver_rank = comm.rank - 1 if comm.rank != 0 else max_rank # Left
        comm.send(Message(P_type, comm.rank, msg.id, msg.phase, msg.hop + 1, msg.dir), receiver_rank)
        pass_count += 1

def dispatch():
    global leader_count, echo_count
    my_id = node_ids[comm.rank]
    local_echo_counter = 0
    while(True):
        try:
            msg = queue.pop(0)
        except IndexError:
            time.sleep(0)
            continue
        print(f"Node {comm.rank} received: {msg}")
        type = msg.type
        if msg.id == my_id and type == P_type:
            leader_broadcast()
            return
        elif msg.id == my_id and type == E_type:
            local_echo_counter += 1
            if (local_echo_counter == 2):
                election(msg.phase + 1)
                local_echo_counter = 0
        elif type == B_type or type == P_type:
            echo_or_pass(msg)
        elif type == E_type:
            if msg.dir == "R":
                receiver_rank = comm.rank + 1 if comm.rank != max_rank else 0 # Right
            else:
                receiver_rank = comm.rank - 1 if comm.rank != 0 else max_rank # Left
            comm.send(Message(E_type, comm.rank, msg.id, msg.phase, msg.hop - 1, msg.dir), receiver_rank)
            if msg.hop == 0:
                print(f"This is where we done goofed in dispatch: {msg}")
            echo_count += 1
        elif type == L_type:
            if msg.dir == "R":
                receiver_rank = comm.rank + 1 if comm.rank != max_rank else 0 # Right
            else:
                receiver_rank = comm.rank - 1 if comm.rank != 0 else max_rank # Left
            comm.send(Message(L_type, comm.rank, msg.id, msg.phase, msg.hop + 1, msg.dir), receiver_rank)
            leader_count += 1
            if leader_count == 2:
                return


def receive():
    print(f"Node {comm.rank} ready to recv.")
    while(True):
        data = comm.recv()
        queue.append(data)

def main():
    election(0) # Every process starts election

    recv_t = threading.Thread(target=receive)
    recv_t.start()
    dispatch()
    recv_t.join(timeout=1.0)
    print(f"Node {comm.rank} done. {B_type} count: {both_count}. {P_type} count {pass_count}. {E_type} count {echo_count}. {L_type} count {leader_count}.")
    

if __name__ == "__main__":
    main()

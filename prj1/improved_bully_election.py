import threading
import time
from bully_election_classes import *
from mpi4py import MPI

comm = MPI.COMM_WORLD


system_ids = SystemIDs(comm)
election_timer = None
max_id = 0

receive_queue = []

election_count = 0
broadcast_count = 0
ok_count = 0
total_count = 0


def construct_msg(sender, type, data=None):
    return Message(sender=sender, type=type, data=data)


def coordinate():
    global broadcast_count, total_count
    for rank in range(comm.size):
        if rank != comm.rank:
            comm.send(construct_msg(
                comm.rank, MsgType.COORDINATOR, max_id), rank)
            broadcast_count += 1
    total_count += broadcast_count + ok_count + election_count


def hold_election():
    global election_count, max_id, election_timer
    my_id = system_ids.get_id(comm.rank)
    max_id = my_id
    election_timer = Timer(2, coordinate)

    for other_rank, id in enumerate(system_ids.ID_array):
        if id > my_id:
            comm.send(construct_msg(comm.rank, MsgType.ELECTION), other_rank)
            election_count += 1


def receive_handle(Message):
    global election_count, broadcast_count, ok_count, total_count, max_id
    if Message.type == MsgType.ELECTION:
        comm.send(construct_msg(comm.rank, MsgType.OK,
                  system_ids.get_id(comm.rank)), Message.sender)
        ok_count += 1
    elif Message.type == MsgType.OK:
        if Message.data > max_id:
            max_id = Message.data
    elif Message.type == MsgType.COORDINATOR:
        print(
            f"Node: {system_ids.get_id(comm.rank)} acknowledge {Message.data} as leader")
        msg_count = election_count + broadcast_count + ok_count
        comm.send(construct_msg(comm.rank, MsgType.MSG_COUNT,
                  msg_count), Message.sender)
    elif Message.type == MsgType.MSG_COUNT:
        print(
            f"Node: {system_ids.get_id(comm.rank)} counted {Message.data} from {system_ids.get_id(Message.sender)}")
        total_count += Message.data
        print(
            f"Node: {system_ids.get_id(comm.rank)} counted {total_count} in total")


def receive():
    my_id = system_ids.get_id(comm.rank)
    print(f"Node {my_id} ready to recv.")
    while(True):
        data = comm.recv()
        receive_queue.append(data)


def dispatch():
    while(True):
        try:
            next = receive_queue.pop(0)
        except IndexError:
            time.sleep(1)
            continue

        print(f"Node: {system_ids.get_id(comm.rank)} got {next}")
        receive_handle(next)


def main():
    recv_t = threading.Thread(target=receive)
    recv_t.start()

    print(
        f"Lowest ID: {system_ids.get_lowest_id()}. My ID: {system_ids.get_id(comm.rank)} My Rank: {comm.rank}")

    if system_ids.get_lowest_id() == system_ids.get_id(comm.rank):
        hold_election()

    dispatch()

if __name__ == "__main__":
    main()

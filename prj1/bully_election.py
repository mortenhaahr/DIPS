#!/bin/python3

import threading
import time
from bully_election_classes import *

from mpi4py import MPI

comm = MPI.COMM_WORLD

system_ids = SystemIDs(comm)
election_timer = None

receive_queue = []

election_count = 0
broadcast_count = 0
ok_count = 0
total_count = 0


def construct_msg(sender, type, data=None):
    return Message(sender=sender, type=type, data=data)


def coordinate():
    global broadcast_count
    global total_count
    global ok_count
    global election_count

    for rank in range(comm.size):
        if rank != comm.rank:
            comm.send(construct_msg(comm.rank, MsgType.COORDINATOR,
                      system_ids.get_id(comm.rank)), rank)
            broadcast_count += 1

    total_count += broadcast_count + ok_count + election_count


election_has_been_held = False


def hold_election():
    global election_timer
    global election_has_been_held

    # early out
    if (election_has_been_held):
        return

    election_has_been_held = True

    my_id = system_ids.get_id(comm.rank)

    election_timer = Timer(5, coordinate)

    for other_rank, id in enumerate(system_ids.ID_array):
        if id > my_id:
            global election_count
            comm.send(construct_msg(comm.rank, MsgType.ELECTION), other_rank)
            election_count += 1


def receive_handle(message):
    global ok_count

    if message.type == MsgType.ELECTION:
        comm.send(construct_msg(comm.rank, MsgType.OK), message.sender)
        ok_count += 1
        hold_election()
    elif message.type == MsgType.OK:
        global election_timer
        election_timer.kill() # We know it will be a `Timer` object, since we can only receive OK messages if we started an election.
    elif message.type == MsgType.COORDINATOR:
        global election_count
        global broadcast_count
        print(
            f"Node: {system_ids.get_id(comm.rank)} acknowledge {system_ids.get_id(message.sender)} as leader")
        msg_count = election_count + broadcast_count + ok_count
        comm.send(construct_msg(comm.rank, MsgType.MSG_COUNT,
                  msg_count), message.sender)
    elif message.type == MsgType.MSG_COUNT:
        global total_count
        print(
            f"Node: {system_ids.get_id(comm.rank)} counted {message.data} from {system_ids.get_id(message.sender)}")
        total_count += message.data
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

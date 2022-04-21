#!/usr/bin/env python3
from collections import namedtuple
import hashlib
import struct
import sys
import os.path
import maya
import datetime
import datetime as DT
import time

def SHA1_OF_A_B(a, b):
    return hashlib.sha1(a + b).hexdigest()


def init_block():
    
    if os.path.isfile('bhoc.bin'):
        print ("Blockchain file found with INITIAL block.")
        return
    else:
        print ("Blockchain file not found. Created INITIAL block.")

    #val = 14
    now = time.time()
    INITIAL = namedtuple('INITIAL', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])
    I = INITIAL(str.encode(""), now, str.encode(""), 0, str.encode("INITIAL"), 14)
    initial = struct.pack('20s d 16s I 11s I', *I)
    data = struct.pack('14s', str.encode("Initial block"))

    prev_hash = SHA1_OF_A_B(initial, data)

    newFileByteArray = bytearray(initial)
    newFile = open("bhoc.bin", "wb")
    newFile.write(newFileByteArray)

    newfile2 = open("initial_hash.txt", "w")
    newfile2.write(prev_hash)


def log_blocks():
    file_stats = os.stat("bhoc.bin")

    binary_file = open("bhoc.bin", 'rb')

    struct_arr = struct.unpack('20s d 16s I 11s I', binary_file.read(68))

    INITIAL = namedtuple('INITIAL', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])

    I = INITIAL._make(struct_arr)
    print("Case: 00000000-0000-0000-0000-000000000000")
    print("Item:", I.evidence_itemID)
    print("Action:", I.state.decode("utf-8") )
    print("Time:", DT.datetime.utcfromtimestamp(I.timestamp).isoformat() + "Z")


def add():
    if not os.path.isfile('bhoc.bin'):
        print("Please initialize the block chain using: ./bhoc init")
        return
    
    if (os.path.getsize("bhoc.bin") == 68):
        with open("initial_hash.txt") as f:
            initial_hash = f.readline().rstrip()
        now = time.time()
        append_block(initial_hash, now, sys.argv[3], sys.argv[5], "CHECKEDIN", 0)
        print("Case:", sys.argv[3])
        print("Added item:", sys.argv[5])
        print("  Status:", "CHECKEDIN")
        print("  Time of action:", DT.datetime.utcfromtimestamp(now).isoformat() + "Z")
        return
    if sys.argv.count("-i") > 1:
        return
    f = open('bhoc.bin', 'rb')
    limit = os.path.getsize("bhoc.bin") - 68
    f.seek(limit, 1)
    hash = hashlib.sha1(f.read()).hexdigest()
    f.close()
    now = time.time()
    append_block(hash, now, sys.argv[3], sys.argv[5], "CHECKEDIN", 0)
    
    print("Hello")
    print("Case:", sys.argv[3])
    print("Added item:", sys.argv[5])
    print("  Status:", "CHECKEDIN")
    print("  Time of action:", DT.datetime.utcfromtimestamp(now).isoformat() + "Z")

    print(os.path.getsize("bhoc.bin"))

def append_block(prev_hash, timestamp, case_id, evidence_itemID, state, data_length):
    BLOCK = namedtuple('BLOCK', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])
    B = BLOCK(str.encode(prev_hash), timestamp, str.encode(case_id), int(evidence_itemID), str.encode(state), 0)
    block = struct.pack('20s d 16s I 11s I', *B)
    
    newFileByteArray = bytearray(block)
    file = open("bhoc.bin", "ab")
    file.write(newFileByteArray)

    


def main():
    command = sys.argv[1]

    if (command == "init"):
        init_block()
    elif (command == "log"):
        log_blocks()
    elif (command == "add"):
        add()



if __name__ == "__main__":
    main()

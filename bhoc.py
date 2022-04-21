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

    prev_hash = hashlib.sha1(initial + data).hexdigest()

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


def main():
    command = sys.argv[1]

    if (command == "init"):
        init_block()
    elif (command == "log"):
        log_blocks()



if __name__ == "__main__":
    main()

#!/usr/bin/env python3
from collections import namedtuple
import hashlib
import struct
import sys
import os.path
import datetime
import datetime as DT
import time
import uuid

def SHA1_OF_A_B(a, b):
    return hashlib.sha1(a + b).hexdigest()


def init_block(check):
    #creating bhoc.bin
    if check != 1:
        if os.path.isfile('bhoc.bin'):
            print ("Blockchain file found with INITIAL block.")
            return
        else:
            print ("Blockchain file not found. Created INITIAL block.")

    #getting time in epoch to store into our block
    now = time.time()
    #named tuple for ease of data
    INITIAL = namedtuple('INITIAL', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])
    #we dont need to store any prev hash, caseid, evidenceID so we just leave it blank
    I = INITIAL(str.encode(""), now, str.encode(""), 0, str.encode("INITIAL"), 14)



    initial = struct.pack('20s d 16s I 11s I', *I)
    data = struct.pack('14s', str.encode("Initial block"))      #pack our data and header into bytes

    prev_hash = SHA1_OF_A_B(initial, data)                      #hashing them both using our sha1 function

    newFileByteArray = bytearray(initial)
    newFileByteArray2 = bytearray(data)
    newFile = open("bhoc.bin", "wb")                            #here, we just add the first initial block to our bhoc.bin file
    newFile.write(newFileByteArray)
    # in the future, do newFile.write(newFileByteArray + newFileByteArray2) to pack the data.
    
    newfile2 = open("initial_hash.txt", "w")                    #storing the first hash into a txt file to avoid unnesessary seaching
    newfile2.write(prev_hash)

def checkin():                                                  #same as checkout
    item_id = sys.argv[3]
    binary_file = open("bhoc.bin", 'rb')
    binary_file.read(68) #weird ass thing I did, bare with me

    f = open('bhoc.bin', 'rb') #reading by 68 bytes, will need to change this when you guys implement remove()
    
    block_list = []
    delim = 68
    while delim is not os.path.getsize("bhoc.bin"):
        f.seek(delim, 1)
        if delim == os.path.getsize("bhoc.bin"):
            break
        
        struct_arr = struct.unpack('20s d 16s I 11s I', binary_file.read(68))
        
        INITIAL = namedtuple('INITIAL', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])

        I = INITIAL._make(struct_arr) #to make it more readable, we make it into a named tuple

        block_list.append(I) #now we have all of our blocks in a list


        delim += 68
    
    f.close()
    change = 0
    flag = 0
    for index, tuple in enumerate(block_list):
        if int(item_id) == tuple.evidence_itemID and tuple.state.decode("utf-8").rstrip('\x00') == "CHECKEDIN": #to make sure its not already checked in
            #print("Hello")
            flag = 1
            change = index
    if flag != 0:
        print("Error: Cannot check in a checked in item. Must check it out first.")
        return
    EDIT_BLOCK = namedtuple('INITIAL', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])
    I = EDIT_BLOCK(block_list[change].prev_hash, block_list[change].timestamp, block_list[change].case_id, block_list[change].evidence_itemID, str.encode("CHECKEDIN"), 0)
    block_list[change] = I #editing this one block
    print("Case:", uuid.UUID(bytes=block_list[change].case_id))
    print("Checked out item:", item_id)
    print("Status:", block_list[change].state)

    f = open("bhoc.bin", 'w')
    f.truncate
    init_block(1)
    file = open("bhoc.bin", "ab") #clearing and adding all the blocks back into the file
    for i in block_list:
        print(i)
        block = struct.pack('20s d 16s I 11s I', *i)
        newFileByteArray = bytearray(block)
        file.write(newFileByteArray)



def checkout(): #same as checkin()
    item_id = sys.argv[3]
    binary_file = open("bhoc.bin", 'rb')
    binary_file.read(68)

    f = open('bhoc.bin', 'rb')
    
    block_list = []
    delim = 68
    while delim is not os.path.getsize("bhoc.bin"):
        f.seek(delim, 1)
        if delim == os.path.getsize("bhoc.bin"):
            break
        
        struct_arr = struct.unpack('20s d 16s I 11s I', binary_file.read(68))
        
        INITIAL = namedtuple('INITIAL', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])

        I = INITIAL._make(struct_arr)

        block_list.append(I)


        delim += 68
    
    f.close()
    change = 0
    flag = 0
    for index, tuple in enumerate(block_list):
        if int(item_id) == tuple.evidence_itemID and tuple.state.decode("utf-8").rstrip('\x00') == "CHECKEDIN":
            #print("Hello")
            flag = 1
            change = index
    if flag == 0:
        print("Error: Cannot check out a checked out item. Must check it in first.")
        return
    EDIT_BLOCK = namedtuple('INITIAL', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])
    I = EDIT_BLOCK(block_list[change].prev_hash, block_list[change].timestamp, block_list[change].case_id, block_list[change].evidence_itemID, str.encode("CHECKEDOUT"), 0)
    block_list[change] = I
    print("Case:", uuid.UUID(bytes=block_list[change].case_id))
    print("Checked out item:", item_id)
    print("Status:", block_list[change].state)

    f = open("bhoc.bin", 'w')
    f.truncate
    file = open("bhoc.bin", "ab")
    init_block(1)
    for i in block_list:
        block = struct.pack('20s d 16s I 11s I', *i)
        newFileByteArray = bytearray(block)
        file.write(newFileByteArray)



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
    if os.path.getsize("bhoc.bin") == 68:
        return
    delim = 68 #print initial block, change this so it prints all of it

    f = open('bhoc.bin', 'rb')
    

    while delim is not os.path.getsize("bhoc.bin"):
        f.seek(delim, 1)
        #print (delim)
        if delim == os.path.getsize("bhoc.bin"):
            return
        struct_arr = struct.unpack('20s d 16s I 11s I', binary_file.read(68)) #read by 68 bytes, will need to change it when you pack in the data, just ask me if you need help
        INITIAL = namedtuple('INITIAL', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])

        I = INITIAL._make(struct_arr)
        print("Case:", uuid.UUID(bytes=I.case_id))
        print("Item:", I.evidence_itemID)
        print("Action:", I.state.decode("utf-8") )
        print("Time:", DT.datetime.utcfromtimestamp(I.timestamp).isoformat() + "Z")

        delim += 68
    


def print_logs():
    print("Hello")


def add():
    if not os.path.isfile('bhoc.bin'):
        print("Please initialize the block chain using: ./bhoc init")
        return
    
    if (os.path.getsize("bhoc.bin") == 68): #change this to 82 for initial block since we're adding the data to the file
        if sys.argv.count("-i") > 1:
            multiple_adds() #perform multiple adds
            return
        
        with open("initial_hash.txt") as f:
            initial_hash = f.readline().rstrip()
        now = time.time()
        append_block(initial_hash, now, uuid.UUID(sys.argv[3]), sys.argv[5], "CHECKEDIN", 0) #add the block to the file
        print_add(uuid.UUID(sys.argv[3]), sys.argv[5], "CHECKEDIN",  DT.datetime.utcfromtimestamp(now).isoformat() + "Z") #print the added block
        return
    if sys.argv.count("-i") > 1:
        multiple_adds() #perform for multiple adds
        return
    f = open('bhoc.bin', 'rb')
    limit = os.path.getsize("bhoc.bin") - 68 #find another way to do this when you guys add remove
    f.seek(limit, 1)
    hash = hashlib.sha1(f.read()).hexdigest()
    f.close()
    now = time.time()
    append_block(hash, now, sys.argv[3], sys.argv[5], "CHECKEDIN", 0)
    print_add(uuid.UUID(sys.argv[3]), sys.argv[5], "CHECKEDIN", DT.datetime.utcfromtimestamp(now).isoformat() + "Z")

def append_block(prev_hash, timestamp, case_id, evidence_itemID, state, data_length):
    i = uuid.UUID(case_id)
    b = i.bytes
    
    BLOCK = namedtuple('BLOCK', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])
    B = BLOCK(str.encode(prev_hash), timestamp, b, int(evidence_itemID), str.encode(state), 0) #using uuid bytes
    block = struct.pack('20s d 16s I 11s I', *B)
    
    newFileByteArray = bytearray(block)
    file = open("bhoc.bin", "ab")
    file.write(newFileByteArray)

def print_add(case_id, item_id, state, timestamp): #printing the add
    print("Case:", case_id)
    print("Added item:", item_id)
    print("  Status:", state)
    print("  Time of action:", timestamp)

def multiple_adds():
    flag = 0
    itemlist = []
    for i in sys.argv:
        if (i == "-i"):
            flag = 1
        if (flag == 1):
            itemlist.append(i)
    itemlist = [value for value in itemlist if value != '-i']
    for i in itemlist:
        if (os.path.getsize("bhoc.bin") == 68): #change this to 82 to include the data
            with open("initial_hash.txt") as f:
                initial_hash = f.readline().rstrip()
            now = time.time()
            append_block(initial_hash, now, sys.argv[3], i, "CHECKEDIN", 0)
            print_add(sys.argv[3], i, "CHECKEDIN",  DT.datetime.utcfromtimestamp(now).isoformat() + "Z")
        else:
            f = open('bhoc.bin', 'rb')
            limit = os.path.getsize("bhoc.bin") - 68
            f.seek(limit, 1)
            hash = hashlib.sha1(f.read()).hexdigest()
            f.close()
            now = time.time()
            append_block(hash, now, sys.argv[3], i, "CHECKEDIN", 0)
            print_add(sys.argv[3], i, "CHECKEDIN", DT.datetime.utcfromtimestamp(now).isoformat() + "Z")
def main():
    command = sys.argv[1]

    if (command == "init"):
        init_block(0)
    elif (command == "log"):
        log_blocks()
    elif (command == "add"):
        add()
    elif (command == "checkout"):
        checkout()
    elif (command == "checkin"):
        checkin()



if __name__ == "__main__":
    main()

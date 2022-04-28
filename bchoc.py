#!/usr/bin/env python3
from collections import namedtuple
from ctypes import LittleEndianStructure
import hashlib
import struct
import sys
import os.path
import datetime
import datetime as DT
import time
import uuid
binary_path = os.getenv("BCHOC_FILE_PATH") or "chain.bin"
def SHA1_OF_A_B(a, b):
    return hashlib.sha1(a + b).hexdigest()

def remove():
    item_id = sys.argv[3]
    new_state = sys.argv[5]
    if len(sys.argv) > 6:
        data_entry = sys.argv[7]
    else:
        data_entry = ""

    delim = 0
    block_list = []
    data_list = []
    f = open(binary_path, 'rb')
    while delim is not os.path.getsize(binary_path):
        #f.seek(delim, 1)
        #print (delim)
        if delim == os.path.getsize(binary_path):
            break
        struct_arr = struct.unpack('20s d 16s I 11s I', f.read(68)) #read by 68 bytes, will need to change it when you pack in the data, just ask me if you need help
        INITIAL = namedtuple('INITIAL', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])

        I = INITIAL._make(struct_arr)
        block_list.append(I)

        datastring = str(I.data_length) + 's'
        
        data = struct.unpack(datastring, f.read(I.data_length))
        DATA = namedtuple('DATA', ['data'])
        D = DATA._make(data)
        data_list.append(D)

        delim += 68 + I.data_length
    
    f.close()
    change = 0
    flag = 0
    id_list = []
    index_list = []
    for index, tuple in enumerate(block_list):
        if int(item_id) == tuple.evidence_itemID:
            #print("Hello")
            flag = 1
            id_list.append(tuple)
            index_list.append(index)

    if flag == 0:
        sys.exit('Remove before add')

    EDIT_BLOCK = namedtuple('INITIAL', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])
    I = EDIT_BLOCK(id_list[-1].prev_hash, id_list[-1].timestamp, id_list[-1].case_id, id_list[-1].evidence_itemID, str.encode(new_state), len(data_entry.encode('utf-8')))
    block_list[change] = I
    print("Case:", uuid.UUID(bytes=id_list[last_index(id_list)].case_id))
    print("Removed item:", item_id)
    print("Status:", I.state.decode("utf-8"))
    print("Owner info:", data_entry)

    file = open(binary_path, "ab")
    
    block = struct.pack('20s d 16s I 11s I', *I)
    datastring = (str(I.data_length) + 's')
    data = struct.pack(datastring, str.encode(data_entry))
    newFileByteArray = bytearray(block)
    newFileByteArray2 = bytearray(data)
    file.write(newFileByteArray + newFileByteArray2)

def init_block(check):
    #creating bhoc.bin
    if check != 1:
        if os.path.isfile(binary_path):
            print ("Blockchain file found with INITIAL block.")
            return
        else:
            print ("Blockchain file not found. Created INITIAL block.")

    #getting time in epoch to store into our block
    now = time.time()
    #named tuple for ease of data
    INITIAL = namedtuple('INITIAL', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])
    #we dont need to store any prev hash, caseid, evidenceID so we just leave it blank
    I = INITIAL(str.encode(""), now, uuid.UUID("00000000-0000-0000-0000-000000000000").bytes_le, 0, str.encode("INITIAL"), 14)



    initial = struct.pack('20s d 16s I 11s I', *I)
    data = struct.pack('14s', str.encode("Initial block"))      #pack our data and header into bytes

    prev_hash = SHA1_OF_A_B(initial, data)                      #hashing them both using our sha1 function

    newFileByteArray = bytearray(initial)
    newFileByteArray2 = bytearray(data)
    newFile = open(binary_path, "wb")                            #here, we just add the first initial block to our bhoc.bin file
    newFile.write(newFileByteArray + newFileByteArray2)
    
    #newfile2 = open("initial_hash.txt", "w")                    #storing the first hash into a txt file to avoid unnesessary seaching
    #newfile2.write(prev_hash)

def checkin(): #same as checkin()
    item_id = sys.argv[3]
    delim = 0
    block_list = []
    data_list = []
    f = open(binary_path, 'rb')
    while delim is not os.path.getsize(binary_path):
        #f.seek(delim, 1)
        #print (delim)
        if delim == os.path.getsize(binary_path):
            break
        struct_arr = struct.unpack('20s d 16s I 11s I', f.read(68)) #read by 68 bytes, will need to change it when you pack in the data, just ask me if you need help
        INITIAL = namedtuple('INITIAL', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])

        I = INITIAL._make(struct_arr)
        block_list.append(I)

        datastring = str(I.data_length) + 's'
        
        data = struct.unpack(datastring, f.read(I.data_length))
        DATA = namedtuple('DATA', ['data'])
        D = DATA._make(data)
        data_list.append(D)

        delim += 68 + I.data_length
    
    f.close()
    change = 0
    flag = 0
    id_list = []
    index_list = []
    for index, tuple in enumerate(block_list):
        if int(item_id) == tuple.evidence_itemID:
            #print("Hello")
            #flag = 1
            id_list.append(tuple)
            index_list.append(index)
    if id_list[last_index(id_list)].state.decode("utf-8").rstrip('\x00') == "CHECKEDOUT":
        flag = 1
    if flag == 0:
        print("Error: Cannot check in a checked in item. Must check it out first.")
        return
    EDIT_BLOCK = namedtuple('INITIAL', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])
    I = EDIT_BLOCK(id_list[-1].prev_hash, id_list[-1].timestamp, id_list[-1].case_id, id_list[-1].evidence_itemID, str.encode("CHECKEDIN"), id_list[-1].data_length)
    block_list[change] = I
    print("Case:", uuid.UUID(bytes=id_list[last_index(id_list)].case_id))
    print("Checked out item:", item_id)
    print("Status:", I.state.decode("utf-8"))

    file = open(binary_path, "ab")
    
    block = struct.pack('20s d 16s I 11s I', *I)
    datastring = (str(I.data_length) + 's')
    data = struct.pack(datastring, *data_list[index_list[last_index(index_list)]])
    newFileByteArray = bytearray(block)
    newFileByteArray2 = bytearray(data)
    file.write(newFileByteArray + newFileByteArray2)


def checkout(): #same as checkin()
    item_id = sys.argv[3]
    delim = 0
    block_list = []
    data_list = []
    f = open(binary_path, 'rb')
    while delim is not os.path.getsize(binary_path):
        #f.seek(delim, 1)
        #print (delim)
        if delim == os.path.getsize(binary_path):
            break
        struct_arr = struct.unpack('20s d 16s I 11s I', f.read(68)) #read by 68 bytes, will need to change it when you pack in the data, just ask me if you need help
        INITIAL = namedtuple('INITIAL', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])

        I = INITIAL._make(struct_arr)
        block_list.append(I)

        datastring = str(I.data_length) + 's'
        
        data = struct.unpack(datastring, f.read(I.data_length))
        DATA = namedtuple('DATA', ['data'])
        D = DATA._make(data)
        data_list.append(D)

        delim += 68 + I.data_length
    
    f.close()
    change = 0
    flag = 0
    id_found = 0
    id_list = []
    index_list = []
    for index, tuple in enumerate(block_list):
        if int(item_id) == tuple.evidence_itemID:
            #print("Hello")
            #flag = 1
            id_found = 1
            id_list.append(tuple)
            index_list.append(index)
    
    if not id_found:
        exit(4)

    if id_list[last_index(id_list)].state.decode("utf-8").rstrip('\x00') == "CHECKEDIN":
        flag = 1
    if flag == 0:
        print("Error: Cannot check out a checked out item. Must check it in first.")
        return
    EDIT_BLOCK = namedtuple('INITIAL', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])
    I = EDIT_BLOCK(id_list[-1].prev_hash, id_list[-1].timestamp, id_list[-1].case_id, id_list[-1].evidence_itemID, str.encode("CHECKEDOUT"), 0)
    block_list[change] = I
    print("Case:", uuid.UUID(bytes=id_list[last_index(id_list)].case_id))
    print("Checked out item:", item_id)
    print("Status:", I.state.decode("utf-8"))

    file = open(binary_path, "ab")
    
    block = struct.pack('20s d 16s I 11s I', *I)
    datastring = (str(I.data_length) + 's')
    data = struct.pack(datastring, *data_list[index_list[last_index(index_list)]])
    newFileByteArray = bytearray(block)
    newFileByteArray2 = bytearray(data)
    file.write(newFileByteArray + newFileByteArray2)



def log_blocks():
    
    f = open(binary_path, 'rb')
    
    delim = 0
    while delim is not os.path.getsize(binary_path):
        #f.seek(delim, 1)
        #print (delim)
        if delim == os.path.getsize(binary_path):
            return
        struct_arr = struct.unpack('20s d 16s I 11s I', f.read(68)) #read by 68 bytes, will need to change it when you pack in the data, just ask me if you need help
        INITIAL = namedtuple('INITIAL', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])

        I = INITIAL._make(struct_arr)
        print("Case:", uuid.UUID(bytes=I.case_id))
        print("Item:", I.evidence_itemID)
        print("Action:", I.state.decode("utf-8") )
        print("Time:", DT.datetime.utcfromtimestamp(I.timestamp).isoformat() + "Z")
        if I.data_length > 0:
            f.read(I.data_length)
        
        delim += 68 + I.data_length
    


def print_logs():
    print("Hello")


def add():
    if not os.path.isfile(binary_path):
        init_block(0)
        #print("Please initialize the block chain using: ./bchoc init")
        return

    if sys.argv[1] != '-c':
        #print("must include case number")
        return
        
    if sys.argv.count("-i") > 1:
        multiple_adds() #perform for multiple adds
        return
    f = open(binary_path, 'rb')
    
    delim = 0
    block_list = []
    data_list = []
    while delim is not os.path.getsize(binary_path):
        #f.seek(delim, 1)
        #print (delim)
        if delim == os.path.getsize(binary_path):
            break
        struct_arr = struct.unpack('20s d 16s I 11s I', f.read(68)) #read by 68 bytes, will need to change it when you pack in the data, just ask me if you need help
        INITIAL = namedtuple('INITIAL', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])

        I = INITIAL._make(struct_arr)
        block_list.append(I)

        datastring = str(I.data_length) + 's'
        
        data = struct.unpack(datastring, f.read(I.data_length))
        
        data_list.append(data)

        delim += 68 + I.data_length
    
    now = time.time()
    header = struct.pack('20s d 16s I 11s I', *block_list[last_index(block_list)])
    datastring = str(block_list[-1].data_length) + 's'
    data = struct.pack(datastring, *data_list[last_index(data_list)])
    hash = 0
    append_block(hash, now, sys.argv[3], sys.argv[5], "CHECKEDIN", 0)
    print_add(uuid.UUID(sys.argv[3]), sys.argv[5], "CHECKEDIN", DT.datetime.utcfromtimestamp(now).isoformat() + "Z")

def append_block(prev_hash, timestamp, case_id, evidence_itemID, state, data_length):
    i = uuid.UUID(case_id)
    b = i.bytes_le
    print(type(prev_hash))
    BLOCK = namedtuple('BLOCK', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])
    B = BLOCK(prev_hash.to_bytes(20, 'little'), timestamp, b[::-1], int(evidence_itemID), str.encode(state), 0) #using uuid bytes
    block = struct.pack('20s d 16s I 11s I', *B)
    
    newFileByteArray = bytearray(block)
    file = open(binary_path, "ab")
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
        f = open(binary_path, 'rb')
    
        delim = 0
        block_list = []
        data_list = []
        while delim is not os.path.getsize(binary_path):
         #f.seek(delim, 1)
        #print (delim)
            if delim == os.path.getsize(binary_path):
                break
            struct_arr = struct.unpack('20s d 16s I 11s I', f.read(68)) #read by 68 bytes, will need to change it when you pack in the data, just ask me if you need help
            INITIAL = namedtuple('INITIAL', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])

            I = INITIAL._make(struct_arr)
            block_list.append(I)

            datastring = str(I.data_length) + 's'
        
            data = struct.unpack(datastring, f.read(I.data_length))
        
            data_list.append(data)

            delim += 68 + I.data_length
    
        now = time.time()
        header = struct.pack('20s d 16s I 11s I', *block_list[-1])
        datastring = str(block_list[-1].data_length) + 's'
        data = struct.pack(datastring, *data_list[last_index(data_list)])
        hash = 0
        append_block(hash, now, sys.argv[3], i, "CHECKEDIN", 0)
        print_add(uuid.UUID(sys.argv[3]), i, "CHECKEDIN", DT.datetime.utcfromtimestamp(now).isoformat() + "Z")
        f.close()
        
def main():
    command = sys.argv[1]

    if (command == "init"):
        if len(sys.argv) > 2:
            sys.exit('Too many parameters')
        init_block(0)
    elif (command == "log"):
        log_blocks()
    elif (command == "add"):
        add()
    elif (command == "checkout"):
        checkout()
    elif (command == "checkin"):
        checkin()
    elif (command == "remove"):
        print("hello")
        remove()

def last_index(input_list:list) -> int:
    return len(input_list) - 1

if __name__ == "__main__":
    main()
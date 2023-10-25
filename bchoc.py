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
from random import randrange
import itertools
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
    if len(data_entry.encode('utf-8')) > 0:
        I = EDIT_BLOCK(id_list[-1].prev_hash, id_list[-1].timestamp, id_list[-1].case_id, id_list[-1].evidence_itemID, str.encode(new_state), len(data_entry.encode('utf-8'))+1)
    else:
        I = EDIT_BLOCK(id_list[-1].prev_hash, id_list[-1].timestamp, id_list[-1].case_id, id_list[-1].evidence_itemID, str.encode(new_state), len(data_entry.encode('utf-8')))
    
    if id_list[last_index(id_list)].state.decode("utf-8").rstrip('\x00') == "CHECKEDOUT":
        sys.exit("Removed after checkout")
    
    if new_state == "RELEASED" and len(sys.argv) < 7:
        sys.exit("Released needs reason.")
    elif new_state == "CHECKEDIN" or new_state == "CHECKEDOUT" or new_state == "INITIAL":
        sys.exit("Not a valid reason.")
    block_list[change] = I
    print("Case:", uuid.UUID(bytes=id_list[last_index(id_list)].case_id))
    print("Removed item:", item_id)
    print("Status:", I.state.decode("utf-8"))
    print("Owner info:", data_entry)

    file = open(binary_path, "ab")
    
    block = struct.pack('20s d 16s I 11s I', *I)
    
    datastring = (str(I.data_length) + 's')
    if I.data_length > 0:
        data = struct.pack(datastring, str.encode(data_entry + '\x00'))
    else:
        data = struct.pack(datastring, str.encode(data_entry))
    print(data)
    print(block)
    newFileByteArray = bytearray(block)
    newFileByteArray2 = bytearray(data)
    file.write(newFileByteArray + newFileByteArray2)

def init_block(check):
    #creating bhoc.bin
    if check != 1:
        if os.path.isfile(binary_path):
            print ("Blockchain file found with INITIAL block.")
            f = open(binary_path, 'rb')
            try:
                struct_arr = struct.unpack('20s d 16s I 11s', f.read(63)) #read by 68 bytes, will need to change it when you pack in the data, just ask me if you need help
            except:
                sys.exit("Invalid file")
            INITIAL = namedtuple('INITIAL', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state'])
            I = INITIAL._make(struct_arr)
            if I.state.decode("utf-8").rstrip('\x00') != "INITIAL":
                sys.exit('Invalid file.')
            else:
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
    if os.path.getsize(binary_path) == 82:
        sys.exit("Checkin before add")
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
        sys.exit("Tried to check in already checked in item")
    EDIT_BLOCK = namedtuple('INITIAL', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])
    I = EDIT_BLOCK(id_list[-1].prev_hash, id_list[-1].timestamp, id_list[-1].case_id, id_list[-1].evidence_itemID, str.encode("CHECKEDIN"), id_list[-1].data_length)
    block_list[change] = I
    print("Case:", uuid.UUID(bytes=id_list[last_index(id_list)].case_id[::-1]))
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
    if os.path.getsize(binary_path) == 82:
        sys.exit("Checkout before add")


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
    if id_list[last_index(id_list)].state.decode("utf-8").rstrip('\x00') == "CHECKEDIN":
        flag = 1
    if flag == 0:
        sys.exit("Tried to check out already checked out item")
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
    block_list = []
    delim = 0
    while delim is not os.path.getsize(binary_path):
        #f.seek(delim, 1)
        #print (delim)
        if delim == os.path.getsize(binary_path):
            break
        struct_arr = struct.unpack('20s d 16s I 11s I', f.read(68)) #read by 68 bytes, will need to change it when you pack in the data, just ask me if you need help
        INITIAL = namedtuple('INITIAL', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])

        I = INITIAL._make(struct_arr)
        
        if I.data_length > 0:
            f.read(I.data_length)
        block_list.append(I)
        delim += 68 + I.data_length
    delim = 0
    if (sys.argv.count("-r") > 0):
        for i in reversed(block_list):
            print_logs(uuid.UUID(bytes=i.case_id[::-1]), i.evidence_itemID, 
            i.state.decode("utf-8").rstrip("\x00"),  DT.datetime.utcfromtimestamp(i.timestamp).isoformat() + "Z")
    elif sys.argv.count("-i") > 0 and sys.argv.count("--reverse") > 0:
        for i in reversed(block_list):
            if i.evidence_itemID == int(sys.argv[3]):
                print_logs(uuid.UUID(bytes=i.case_id[::-1]), i.evidence_itemID, 
                i.state.decode("utf-8").rstrip("\x00"),  DT.datetime.utcfromtimestamp(i.timestamp).isoformat() + "Z")
    elif sys.argv.count("-i") > 0 and sys.argv.count("-c") > 0:
        for i in block_list:
            if sys.argv[3] == str(uuid.UUID(bytes=i.case_id[::-1])) and i.evidence_itemID == int(sys.argv[5]):
                print_logs(uuid.UUID(bytes=i.case_id[::-1]), i.evidence_itemID, 
                i.state.decode("utf-8").rstrip("\x00"),  DT.datetime.utcfromtimestamp(i.timestamp).isoformat() + "Z")
    elif sys.argv.count("-c") > 0:
        for i in block_list:
            if sys.argv[3] == str(uuid.UUID(bytes=i.case_id[::-1])):
                print_logs(uuid.UUID(bytes=i.case_id[::-1]), i.evidence_itemID, 
                i.state.decode("utf-8").rstrip("\x00"),  DT.datetime.utcfromtimestamp(i.timestamp).isoformat() + "Z")
    elif sys.argv.count("-i") > 0:
        for i in block_list:
            if int(sys.argv[3]) == i.evidence_itemID:
                print_logs(uuid.UUID(bytes=i.case_id[::-1]), i.evidence_itemID, 
                i.state.decode("utf-8").rstrip("\x00"),  DT.datetime.utcfromtimestamp(i.timestamp).isoformat() + "Z")
    elif (sys.argv.count("-n") > 0):
        if int(sys.argv[3]) > len(block_list):
            for i in block_list:
                print_logs(uuid.UUID(bytes=i.case_id[::-1]), i.evidence_itemID, 
                i.state.decode("utf-8").rstrip("\x00"),  DT.datetime.utcfromtimestamp(i.timestamp).isoformat() + "Z")
        else:
            for i in range(int(sys.argv[3])):

                print_logs(uuid.UUID(bytes=block_list[i].case_id[::-1]), block_list[i].evidence_itemID, 
                block_list[i].state.decode("utf-8").rstrip("\x00"),  DT.datetime.utcfromtimestamp(block_list[i].timestamp).isoformat() + "Z")         
    else:
        #f.seek(delim, 1)
        #print (delim)
        for i in block_list:
            print_logs(uuid.UUID(bytes=i.case_id[::-1]), i.evidence_itemID, 
            i.state.decode("utf-8").rstrip("\x00"),  DT.datetime.utcfromtimestamp(i.timestamp).isoformat() + "Z")
        
    


def print_logs(case_id, evidence_id, state, time):
    print("Case:", case_id)
    print("Item:", evidence_id)
    print("Action:", state)
    print("Time:", time)
    print()


def add():
    if not os.path.isfile(binary_path):
        init_block(0)
        return

    if len(sys.argv) < 5:
        sys.exit("Too little args.")
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
    hash = SHA1_OF_A_B(header, data)
    print(hash)
    id_list = []
    for tuple in block_list:
        if int(sys.argv[5]) == tuple.evidence_itemID:
                #print("Hello")
                #flag = 1
            id_list.append(tuple)

    if len(id_list) > 0:
        if id_list[last_index(id_list)].state.decode("utf-8").rstrip('\x00') == "DISPOSED" or id_list[last_index(id_list)].state.decode("utf-8").rstrip('\x00') == "DESTROYED" or id_list[last_index(id_list)].state.decode("utf-8").rstrip('\x00') == "RELEASED" or id_list[last_index(id_list)].state.decode("utf-8").rstrip('\x00') == "CHECKEDIN":
            sys.exit("Tried to add removed block or duplicate ID.")


    append_block(hash, now, sys.argv[3], sys.argv[5], "CHECKEDIN", 0)
    print_add(uuid.UUID(sys.argv[3]), sys.argv[5], "CHECKEDIN", DT.datetime.utcfromtimestamp(now).isoformat() + "Z")

def append_block(prev_hash, timestamp, case_id, evidence_itemID, state, data_length):
    i = uuid.UUID(case_id)
    b = i.bytes[::-1]
    print(type(prev_hash))
    BLOCK = namedtuple('BLOCK', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])
    B = BLOCK(str.encode(prev_hash), timestamp, b, int(evidence_itemID), str.encode(state), 0) #using uuid bytes
    #print(B)
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
        hash = SHA1_OF_A_B(header, data)
        append_block(hash, now, sys.argv[3], i, "CHECKEDIN", 0)
        #print_add(uuid.UUID(sys.argv[3]), i, "CHECKEDIN", DT.datetime.utcfromtimestamp(now).isoformat() + "Z")
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
    elif (command == "clear"):
         f = open(binary_path, 'rb')
         os.remove(binary_path)
    elif(command == "verify"):
        verify()

def verify(): #same as checkin()

    delim = 0
    block_list = []

    f = open(binary_path, 'rb')
    while delim is not os.path.getsize(binary_path):
        #f.seek(delim, 1)
        #print (delim)
        if delim == os.path.getsize(binary_path):
            break
        try:
            struct_arr = struct.unpack('20s d 16s I 11s I', f.read(68)) #read by 68 bytes, will need to change it when you pack in the data, just ask me if you need help
        except:
            sys.exit("invalid file")
        BLOCK = namedtuple('Block', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length'])

        B = BLOCK._make(struct_arr)
        

        datastring = str(B.data_length) + 's'
        
        data = struct.unpack(datastring, f.read(B.data_length))
        DATA = namedtuple('DATA', ['data'])
        D = DATA._make(data)
        
        FULLBLOCK = namedtuple('Block', ['prev_hash', 'timestamp', 'case_id', 'evidence_itemID', 'state', 'data_length', 'data'])

        F = FULLBLOCK(B.prev_hash, B.timestamp, B.case_id, B.evidence_itemID, B.state, B.data_length, D.data)
        block_list.append(F)
        delim += 68 + B.data_length
    
    f.close()
    for a, b in pairwise(block_list):
        struct_arr = struct.pack('20s d 16s I 11s I', a.prev_hash, a.timestamp, a.case_id, a.evidence_itemID, a.state, a.data_length)
        datastring = str(a.data_length) + 's'
        data = struct.pack(datastring, a.data)
        print(bytes.fromhex(SHA1_OF_A_B(struct_arr, data)), b.prev_hash)
        if bytes.fromhex(SHA1_OF_A_B(struct_arr, data)) == b.prev_hash:
            print(bytes.fromhex(SHA1_OF_A_B(struct_arr, data)), b.prev_hash)
            sys.exit("hashes dont match XD")
        #print(b.prev_hash)

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

def last_index(input_list:list) -> int:
    return len(input_list) - 1

if __name__ == "__main__":
    main()

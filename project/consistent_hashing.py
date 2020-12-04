import hashlib
import bisect
from random import random
from collections import OrderedDict

ringSlots=2**32
hashring={}
num_vservers_per_pservers=2
vserver_to_pserver_map={}

def create_hashRing(servers):
    global hashring
    print("Creating Ring in consistent hashing")
    for each_server in servers:
        add_server_to_hashring(each_server)
    hashring=OrderedDict(sorted(hashring.items())) 
    print(f"Hashring:{hashring}")



def add_server_to_hashring(server):
    global hashring
    global vserver_to_pserver_map
    next_server=[]
    for i in range(num_vservers_per_pservers):
        vserver_name=server+str(i)
        vserver_to_pserver_map[vserver_name]=server
        vserver_index=get_hashvalue(vserver_name)
        hashring[vserver_index]= vserver_name
        hashring=OrderedDict(sorted(hashring.items())) 
        nextvalue=next_value(hashring,vserver_index)
        next_server.append(vserver_to_pserver_map[nextvalue])
    next_server=list(set(next_server))
    if (server in next_server):
        next_server.remove(server)
    return next_server

def next_value(hashring,key):
    if list(hashring.keys())[-1]==key:
        next_value=list(hashring.values())[0]
        return next_value
    else:
        next_key=list(hashring)[list(hashring.keys()).index(key) + 1]
        return hashring[next_key]

    

def remove_server_from_hashring(server):
    next_server_list=[]
    for i in range(num_vservers_per_pservers):
        vserver_name=server+str(i)
        vserver_index=get_hashvalue(vserver_name)
        nextvalue=next_value(hashring,vserver_index)
        next_server=vserver_to_pserver_map[nextvalue]
        next_server_list.append(next_server)
        del vserver_to_pserver_map[vserver_name]
        del hashring[vserver_index]
    return next_server_list
    


def get_hashvalue(key):
    hash_object=hash(key)%ringSlots
    return hash_object

def get_server_ch(key):
    data_hash=get_hashvalue(key)
    vserver_index_list=hashring.keys()
    vserver_index_list=sorted(vserver_index_list)
    vserver_index_for_keystore=bisect.bisect(vserver_index_list,data_hash)
    if vserver_index_for_keystore>=len(vserver_index_list):
        vserver_index_for_keystore=0
    vserver_index=vserver_index_list[vserver_index_for_keystore]
    vserver_name=hashring[vserver_index]
    v_node_id=vserver_name[-1]
    server=vserver_to_pserver_map[vserver_name]
    return server
    


import hashlib
import bisect
from itertools import cycle
ringSlots=32
ring={}
server_hashes=[]
num_virtual_servers=8
virtual_servers=[]
vserver_to_pserver_map=[]
def create_hashRing(servers):
    print("Creating Ring in consistent hashing")
    ## TODO
    global ring
    global num_virtual_servers
    global virtual_servers
    print(ringSlots)
    for each_vserver in range(num_virtual_servers):
        vserver_name="vserver{}".format(each_vserver)
        virtual_servers.append(vserver_name)
        vserver_index=get_hashvalue(vserver_name)
        print(f"index value of {vserver_name}:{vserver_index}")
        ring[vserver_index]= vserver_name
    print(ring)
    ring=sorted(ring.items())
    map_vserver_to_pserver(servers)
    #print(ring)
    #print("created ring")

def map_vserver_to_pserver(servers):
    global virtual_servers,vserver_to_pserver_map
    servers=cycle(servers)
    vserver_to_pserver_map=dict(zip(virtual_servers,servers))
    print(vserver_to_pserver_map)


def get_hashvalue(key):
    hash_object=abs(hash(key))%ringSlots
    print(f"Hash value of key {key}:{hash_object}")
    return hash_object

def get_server_ch(key):
    data_hash=get_hashvalue(key)
    vserver_index_list=[i[0] for i in ring]
    #print(server_index_list)
    vserver_index=bisect.bisect(vserver_index_list,data_hash)
    #print(server_index)
    if vserver_index>=len(vserver_index_list):
        vserver_index=0
    vserver_name=ring[vserver_index][1]
    print(vserver_to_pserver_map[vserver_name])
    return vserver_to_pserver_map[vserver_name]
    


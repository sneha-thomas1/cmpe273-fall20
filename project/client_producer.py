import zmq
import time
import sys
from itertools import cycle
from consistent_hashing import *
from hrw import *
import json
import consul


producers = {}
servers=[]

def generate_data_consistent_hashing(servers):
    print("Starting Consistent Hashing...")
    producers = create_clients(servers)
    hashRing=create_hashRing(servers)
    for num in range(10):
        key=num
        value=num
        option="PUT"
        data = { 'op':f'{option}','key': f'{key}', 'value': f'{value}' }
        print(f"Sending data:{data}")
        server=get_server_ch(data['key'])
        server_conn=producers[server]
        server_conn.send_json(data)
    print("Done")
    

    
def generate_data_hrw_hashing(servers):
    print("Starting HRW hashing...")
    option="PUT"
    producers = create_clients(servers)
    for num in range(10): 
        key=num
        value=num
        data = { 'op':f'{option}','key': f'{key}', 'value': f'{value}' }
        print(f"Sending data:{data}")
        server=get_server_hrw(data['key'],servers)
        server_conn=producers[server]
        server_conn.send_json(data)
    print("Done")


def get_all_data_from_server(server):
    print(f"Getting all data from {server}")
    request_data={'op':"GET_ALL"}
    context = zmq.Context()
    receiver = context.socket(zmq.PULL)
    server_conn=producers[server]
    server_conn.send_json(request_data)
    receiver.bind("tcp://127.0.0.1:5000")
    response = receiver.recv_json()
    return response

def manage_membership_consistent_hashing(server,command):
    global servers
    global producers
    ##add node
    if command=='add':
        producers=create_clients(server)
        next_server=add_server_to_hashring(server[0])
        data_to_be_rehashed=[]
        for server in next_server:
            data=get_all_data_from_server(server)
            data_to_be_rehashed.extend(data)
            server_conn=producers[server]
            req={'op':"DELETE"}
            server_conn.send_json(req)
        data_to_be_rehashed=json.dumps({'collection': data_to_be_rehashed})
        data_to_be_rehashed=json.loads(data_to_be_rehashed)
        for collection in data_to_be_rehashed['collection']:
            collection["op"]="PUT"
            server=get_server_ch(collection['key'])
            server_conn=producers[server]
            server_conn.send_json(collection)
    ##remove node
    elif command=="remove":
        data_from_deleted_node=get_all_data_from_server(server[0])
        data_from_deleted_node=json.dumps({"collection":data_from_deleted_node})
        data_from_deleted_node=json.loads(data_from_deleted_node)
        print(f"Deleting node {server[0]}")
        next_server_list=remove_server_from_hashring(server[0])
        servers.remove(server[0])
        for collection in data_from_deleted_node['collection']:
            collection["op"]="PUT"
            server=get_server_ch(collection['key'])
            server_conn=producers[server]
            server_conn.send_json(collection)
    else :
        print("invalid command")
    print("Done")


def check_for_server_changes(server):
    global servers
    servers=server
    index=None
    new_server=[]
    while True:
        index, data = consul_server.kv.get('', index=index,recurse=True)
        consul_kv=data
        num_server_new =len(consul_kv)
        server_new=[]
        if num_server_new != len(servers):
            if num_server_new > len(servers):
                server_new_port=consul_kv[num_server_new-1]['Value'].decode('UTF-8')[-4:]
                if not (server_new_port.startswith('.')):
                    print("Server membership change")
                    new_server.append(consul_kv[num_server_new-1]['Value'].decode('UTF-8'))
                    manage_membership_consistent_hashing(new_server,'add')
                    servers.append(consul_kv[num_server_new-1]['Value'].decode('UTF-8'))
            else :
                for each_server in range(num_server_new):
                    server_new.append(consul_kv[each_server]['Value'].decode('UTF-8'))
                server_diff = [i for i in server_new + servers if i not in servers or i not in server_new]
                manage_membership_consistent_hashing(server_diff,'remove')
      
                


def create_clients(servers):
    global producers
    context = zmq.Context()
    for server in servers:
        print(f"Creating a server connection to {server}...")
        producer_conn = context.socket(zmq.PUSH)
        producer_conn.bind(server)
        producers[server] = producer_conn
    return producers

if __name__ == "__main__":
    servers = []
    consul_server = consul.Consul(host='127.0.0.1', port=8500)
    consul_kv = consul_server.kv.get(key='', recurse=True)
    consul_kv=consul_kv[1]
    num_server =len(consul_kv)
    print(f"num_server={num_server}")
        
    for each_server in range(num_server):
        server_ip = consul_kv[each_server]['Value'].decode('UTF-8')
        servers.append(server_ip)
        
    #generate_data_round_robin(servers)
    #generate_data_hrw_hashing(servers)
    generate_data_consistent_hashing(servers)
    check_for_server_changes(servers)

  


















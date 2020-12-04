import zmq
import sys
from  multiprocessing import Process
import consul
import time

num_server=1
servers=[]

def server(port):
    context = zmq.Context()
    consumer = context.socket(zmq.PULL)
    consumer.connect(f"tcp://127.0.0.1:{port}")
    data={}

    while True:
        raw = consumer.recv_json()
        op= raw['op']
        if op=="PUT":
            key, value= raw['key'], raw['value']
            if key not in data.keys():
                print(f"Server_port={port}:key={key},value={value}")
                data[key] =value
        elif op=="GET_ONE":
            key= raw['key']
            value=data[key]
            response_data = { 'key': f'{key}', 'value': f'{value}' }
            context = zmq.Context()
            sender = context.socket(zmq.PUSH)
            sender.connect("tcp://127.0.0.1:4000")
            sender.send_json(response_data)
        elif op=="GET_ALL":
            print(f"get all from {port}")
            response_collection=[]
            for key,value in data.items():
                response={ 'key': f'{key}', 'value': f'{value}' }
                response_collection.append(response)
            print(response_collection)
            context = zmq.Context()
            sender = context.socket(zmq.PUSH)
            sender.connect("tcp://127.0.0.1:5000")
            sender.send_json(response_collection)
        elif op=="DELETE":
            data.clear()

            
def check_for_server_changes(server):
    global servers
    servers=server
    index=None
    while True:
        index, data = consul_server.kv.get('', index=index,recurse=True)
        consul_kv=data
        num_server_new =len(consul_kv)
        server_new=[]
        port_no=[]
        if num_server_new > len(servers):
            print("Server membership change")
            server_name=consul_kv[num_server_new-1]['Key']
            for each_server in range(num_server_new-1):
                server_ip = consul_kv[each_server]['Value'].decode('UTF-8')
                server_new.append(server_ip)
                port_no.append(int(server_ip[-4:]))
            server_port=max(port_no)+1
            add_server(server_name,server_port)
            server_new.append(f'tcp://127.0.0.1:{server_port}')
            consul_server.kv.put(f'{server_name}',f'tcp://127.0.0.1:{server_port}')
            servers=server_new
        time.sleep(10)


def add_server(server_name,server_port):
    print(f"Starting {server_name} at:{server_port}...")
    consul_server.kv.put(f'{server_name}',f'tcp://127.0.0.1:{server_port}')
    Process(target=server, args=(server_port,)).start()

       
if __name__ == "__main__":
    consul_server = consul.Consul(host='127.0.0.1', port=8500)
    consul_kv = consul_server.kv.get(key='', recurse=True)
    consul_kv=consul_kv[1]
    num_server =len(consul_kv)
    print(f"num_server={num_server}")
    servers=[]   
    for each_server in range(num_server):
        server_port = "200{}".format(each_server)
        server_name=consul_kv[each_server]['Key']
        add_server(server_name,server_port)
        servers.append(f'tcp://127.0.0.1:{server_port}')
    check_for_server_changes(servers)
    
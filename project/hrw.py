import hashlib

def calculate_weight(key,node):
    a = 1103515245
    b = 12345
    node=int(node[-4:])
    weight=(a * ((a * node + b) ^ hash(key)) + b) % (2**31)
    return weight

def get_server_hrw(key,servers):
    server_weights=[]
    for each_server in servers:
        server_weight=calculate_weight(key,each_server)
        server_weights.append((each_server,server_weight))
    print (server_weights)
    print(max(server_weights, key=lambda x:x[1]))
    server=max(server_weights, key=lambda x:x[1])[0]
    print(server)
    return server

    
import time
import zmq
import math

def worker():
    context = zmq.Context()
    # recieve number from generator
    worker_receiver = context.socket(zmq.PULL)
    worker_receiver.connect("tcp://127.0.0.1:5557")
    # send result to dashboard
    worker_sender = context.socket(zmq.PUSH)
    worker_sender.connect("tcp://127.0.0.1:5558")
    
    while True:
        number = worker_receiver.recv_json()
        data = number['num']
        print(data)
        square_root=math.sqrt(data)
        result = {  'num' : data,'square_root':square_root}
        #print(result)
        worker_sender.send_json(result)

worker()
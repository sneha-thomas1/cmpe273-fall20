import time
import zmq

def dashboard():
    context = zmq.Context()
    dashboard_receiver = context.socket(zmq.PULL)
    dashboard_receiver.bind("tcp://127.0.0.1:5558")
    for x in range(10000):
        result = dashboard_receiver.recv_json()
        print(result)
dashboard()
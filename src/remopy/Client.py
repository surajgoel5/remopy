import zmq
import dill
import threading
import time

class Client:

    WAITTIME_RES_RECV=0.5
    N_UPDATE_COUNTER_MAX=1000
    def __init__(self, server_address="localhost", job_port=5555,sub_port=5556):
        self.context = zmq.Context()
        # Socket for sending jobs        
        self.job_socket = self.context.socket(zmq.REQ)
        self.job_socket.connect(f"tcp://{server_address}:{job_port}")


        # Socket for subscribing to progress updates
        self.sub_socket = self.context.socket(zmq.SUB)
        self.sub_socket.connect(f"tcp://{server_address}:{sub_port}")
        self.sub_socket.setsockopt_string(zmq.SUBSCRIBE, "")  # Subscribe to all messages

    def listen_for_updates(self):
        """Listen for job progress updates."""
        message = self.sub_socket.recv_json()
        return message 
        
    def submit_job(self, func, *args, **kwargs):
        """Submit a job to the server."""
        job_data = {
            "func": dill.dumps(func),  # Serialize the function
            "args": args,
            "kwargs": kwargs,
            'request':'job'}
        #self.result_thread= threading.Thread(target = self. get_result )
        #self.result_thread.start()
        
        self.job_socket.send(dill.dumps(job_data))
        result = self.job_socket.recv()  # Receive job ID and status
        self.result = dill.loads(result)
        return self.result
import zmq
import dill
import threading
import time

class Client:
    def __init__(self, server_address="localhost", job_port=5555,sub_port=5556,res_port=2000):
        self.context = zmq.Context()
        # Socket for sending jobs
        self.res_port=res_port

        
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
            "res_port":self.res_port}
        self.result_thread= threading.Thread(target = self. get_result )
        self.result_thread.start()
        
        self.job_socket.send(dill.dumps(job_data))
        response = self.job_socket.recv_json()  # Receive job ID and status
        return response["job_id"]

    def get_result(self):
        """Retrieve and deserialize the job result."""
        self.res_socket = self.context.socket(zmq.REP)
        self.res_socket.bind(f"tcp://*:{self.res_port}")
        
        message = self.res_socket.recv()
        self.result = dill.loads(message)
        self.res_socket.send_json({'recieved':True})
        self.res_socket.close()

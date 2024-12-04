import zmq
import dill
import threading
import uuid
import traceback
import time


class Server:
    WAITTIME_RES_SENDER=1
    N_RETRIES_RES_SENDER=3
    
    def __init__(self,ip='*' job_port=5555,pub_port=5556):
        
        self.pub_port=pub_port
        self.job_port= job_port
        self.context = zmq.Context()
        
        self.job_socket = self.context.socket(zmq.REP)
        self.job_socket.bind(f"tcp://{ip}:{job_port}")

                
        self.pub_socket = self.context.socket(zmq.PUB)
        self.pub_socket.bind(f"tcp://{ip}:{pub_port}")

        
        self.jobs = {}  # Store job detail
        self.lock = threading.Lock()  # Ensure thread-safe access to `self.jobs`
    
    def handle_jobs(self):
        """Main loop to handle incoming jobs."""
        while True:
            message = self.job_socket.recv()
            client_ip=self.job_socket.getsockopt(zmq.LAST_ENDPOINT).decode().split('//')[-1].split(':')[0]
            job_data = dill.loads(message)

            func_serialized = job_data["func"]
            args_serialized = dill.dumps(job_data.get("args", []))
            kwargs_serialized = dill.dumps(job_data.get("kwargs", {}))
            result_port=job_data["res_port"]

            job_id = str(uuid.uuid4())
            with self.lock:
                self.jobs[job_id] = {"status": "running", "result": None, "machine_ip": client_ip,"machine_result_port":result_port, "res_sent":False}  
            self.job_socket.send_json({"job_id": job_id, "status": "received"})
            thread = threading.Thread(
                target=self.worker,
                args=(job_id, func_serialized, args_serialized, kwargs_serialized),
                daemon=True,
            )
            thread.start()

    def worker(self, job_id, func_serialized, args_serialized, kwargs_serialized):
        """Worker thread to process a job."""
        result=None
        try:
            # Deserialize function and arguments
            func = dill.loads(func_serialized)
            args = dill.loads(args_serialized)
            kwargs = dill.loads(kwargs_serialized)

            # Execute the function
            result = func(*args, **kwargs)
            with self.lock:
                self.jobs[job_id]["status"] = "completed"
                self.jobs[job_id]["result"] = "sending"  # Serialize result
        except Exception as e:
            with self.lock:
                self.jobs[job_id]["status"] = "error"
                self.jobs[job_id]["result"] = None
                self.jobs[job_id]["error"] = str(e)
                self.jobs[job_id]["traceback"] = traceback.format_exc()
        
        print('Job complete', job_id)
        self.send_result(job_id,result)
                
    def update_clients(self):
        """Publish periodic job status updates."""
        while True:
            with self.lock:
                for job_id, job_info in list(self.jobs.items()):
                    if not job_info["res_sent"]:
                        pub_data={
                            "job_id": job_id,
                            "status": job_info["status"],
                            "result": job_info.get("result"),  # Serialize updates
                            "traceback": job_info.get("traceback"),
                             "res_sent":job_info.get("res_sent")
                        }
                        print(f'[[PORT {self.pub_port}]] {pub_data} ')
                        self.pub_socket.send_json(pub_data)
            time.sleep(1)

  
    def send_result(self,job_id,result):#
        for i in range(self.N_RETRIES_RES_SENDER):
            try:
                
                context = zmq.Context()
                res_socket = context.socket(zmq.REQ)
                ip_res=self.jobs[job_id]["machine_ip"]
                if ip_res == '0.0.0.0':
                    ip_res='127.0.0.1'
                job_res_port=self.jobs[job_id]["machine_result_port"]
                res_socket.connect(f"tcp://{ip_res}:{job_res_port}")
                res_socket.send(dill.dumps(result))
                message =  res_socket.recv_json()
                # print(message)
                # if message['recieved']=='recieved':
                    
                self.jobs[job_id]["res_sent"] =  True
                self.jobs.pop(job_id)
                print(f'Job Result Recieved {job_id}')
                break
                #     self.jobs.pop(job_id)
                #     print("Job Result Recieved")
                # else:
                #     pass
            except Exception as e:
                print(e)
                time.sleep(self.WAITTIME_RES_SENDER)
    
    def run(self):
        """Run the server."""
        threading.Thread(target=self.handle_jobs, daemon=True).start()
        threading.Thread(target=self.update_clients, daemon=True).start()
        print("Server is running...")
        while True:
            time.sleep(1)
# server = Server()
# server.run()

# cli.py
import argparse
from .server import server

def main():
    parser = argparse.ArgumentParser(description="Run the Server.")
    parser.add_argument("--ip", type=str, default="0.0.0.0", help="IP address to bind to")
    parser.add_argument("--job_port", type=int, default=5555, help="Port to bind to")
    parser.add_argument("--pub_port", type=int, default=5556, help="Port to bind to")
  

    args = parser.parse_args()

    # Instantiate and run the server
    server = Server(ip=args.ip, job_port=args.job_port,pub_port=args.pub_port)
    server.run()

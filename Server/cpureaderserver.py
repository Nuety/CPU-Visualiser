import socket
import os
import sys
import time

script_dir = os.path.abspath(os.path.dirname(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
from rpimatrix.bindings.python.samples.samplebase import SampleBase

class cpuServer(SampleBase):
    def __init__(self, *args, **kwargs):
        super(cpuServer, self).__init__(*args, **kwargs)

    def run(self):
        width = self.matrix.width
        height = self.matrix.height


        # Set up a server
        server_ip = '0.0.0.0'
        server_port = 5555




        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((server_ip, server_port))
        server_socket.listen(1)
        print(f"Server running on port {server_port}")
        while True:
            print(f"Waiting for connection on {server_ip}:{server_port}")
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")
            
            cpu_old = []

            while True:
                try:
                    # Receive data from the client
                    data = client_socket.recv(1024).decode()
                    if not data:
                        raise ConnectionError("Connection closed by the client")
                    num_cpu = int(data.count(',')) + 1

                    cpu_str = data.split(',')

                    # How wide should a cpu be
                    cpucol = width / num_cpu
                    #how high cpu should show itself
                    cpu_list = list(map(float, cpu_str))
                    print(cpu_list)

                    for index, cpu in enumerate(cpu_list):
                        if cpu == 0.0:
                            cpurow = 1
                        else:
                            cpurow = int((cpu / 100) * height)
                            
                        # Define color components for the current cpu
                        red, green, blue = 100, 100, 100  # Default color
                        

                        for col in range(int(index * cpucol), int((index + 1) * cpucol)):
                            for row in range(cpurow):
                                if 0.0 <= row <= 33.0:
                                    red, green, blue = 0, 100, 0  # Green
                                elif 33.0 < row <= 66.0:
                                    red, green, blue = 100, 100, 0  # Yellow
                                elif 66.0 < row <= 100.0:
                                    red, green, blue = 100, 0, 0  # Red
                                else:
                                    red, green, blue = 100, 100, 100  # Gray for unknown
                                self.matrix.SetPixel(row,col,red,green,blue)
                        for col in range(int(index * cpucol), int((index + 1) * cpucol)):
                            for row in range(cpurow, height):
                                self.matrix.SetPixel(row,col,0,0,0)

                    cpu_old = cpu_list


                except Exception as e:
                    # Print or handle the exception'
                    self.matrix.Clear()
                    print(f"An exception occurred: {e}")
                    break


# Main function
if __name__ == "__main__":
    server = cpuServer()
    if (not server.process()):
        server.print_help()
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


        # thresholds
        tg = 0.25 #green
        ty = 0.50 #yellow
        to = 0.75 #orange



        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((server_ip, server_port))
        server_socket.listen(1)
        print(f"Server running on port {server_port}")
        while True:
            print(f"Waiting for connection on {server_ip}:{server_port}")
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")
            
            cpu_old = []
            
            client_socket.send(b'OK')


            first = 0
            while True:
                try:
                    client_socket.setblocking(1)
                    data = client_socket.recv(1024).decode()
                    data = data.split('-')[0]
                    client_socket.send(b'OK')
                    if data == 'UPDATE':
                        continue
                    if not data:
                        raise ConnectionError("Connection closed by the client")
                    num_cpu = int(data.count(',')) + 1

                    cpu_str = data.split(',')
                    

                    # How wide should a cpu be
                    cpucol = width / num_cpu
                    #how high cpu should show itself
                    cpu_list = list(map(float, cpu_str))
                    if first == 0:
                        cpu_old = [0] * len(cpu_list)
                        first = 1
                    
                    while True:
                        for index, cpu in enumerate(cpu_list):
                            # Define color components for the current cpu
                            red, green, blue = 100, 100, 100  # Default color
                            diff = int(cpu) - cpu_old[index]
                            if 0.0 <= cpu_old[index] <= height * tg:
                                red, green, blue = 0, 100, 0  # Green
                            elif height * tg < cpu_old[index] <= height * ty:
                                red, green, blue = 100, 100, 0  # Yellow
                            elif height * ty < cpu_old[index] <= height * to:
                                red, green, blue = 100, 64, 0  # Orange
                            elif height * to < cpu_old[index] <= height:
                                red, green, blue = 100, 0, 0  # Red
                            else:
                                red, green, blue = 100, 100, 100  # Gray for unknown

                            for col in range(int(index * cpucol), int((index + 1) * cpucol)):
                                if diff > 0:
                                    inc = 1
                                    self.matrix.SetPixel(cpu_old[index],col,red,green,blue)
                                elif diff < 0:
                                    self.matrix.SetPixel(cpu_old[index],col,0,0,0)
                                    inc = -1
                                else:
                                    inc = 0

                            cpu_old[index] += inc
                        client_socket.setblocking(0)
                        message = ""
                        try:
                            message = client_socket.recv(1024).decode()
                            
                        except socket.error as e:
                            pass

                        message = message.split('-')[0]
                        if message == 'UPDATE':
                            # Receive data from the client
                            client_socket.send(b'OK')
                            break

                        time.sleep(0.05)

                except Exception as e:
                    # Print or handle the exception'
                    self.matrix.Clear()
                    client_socket.close()
                    print(f"An exception occurred: {e}")
                    break


# Main function
if __name__ == "__main__":
    server = cpuServer()
    if (not server.process()):
        server.print_help()
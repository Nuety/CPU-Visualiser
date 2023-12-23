import psutil
import socket

# Set up a server
# server_ip = '192.168.1.131'  # Update with the IP address of your server
server_ip = '172.26.1.131'  # Update with the IP address of your server
server_port = 5555

print(f"Connecting to server on port {server_port}")
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((server_ip, server_port))
print(f"connected to server with ip {server_ip}")
client_socket.setblocking(0)

while True:
    # Calculate cpu%
    cpu_usage = psutil.cpu_percent(interval=0.5, percpu=True)
    

    # Convert the list to a string for easy transmission
    cpu_str = ','.join(map(str, cpu_usage))
    server_ok_signal = ""
    try: 
        server_ok_signal = client_socket.recv(1024)
    except socket.error as e:
        pass

    if server_ok_signal == b'OK':
        # Send the data over Wi-Fi
        client_socket.send(cpu_str.encode())
    else:
        client_socket.send(b'UPDATE')
    
    


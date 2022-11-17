import socket
HOST = "10.35.70.30"  # The server's hostname or IP address
PORT = 33005  # The port used by the server
data = "Abhinaw sending to Amogh"
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    s.send(data.encode())
    data = s.recv(1024)
print(f"Received {data}")

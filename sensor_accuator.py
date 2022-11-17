import socket
HOST = "10.35.70.24"
PORT = 33005
HOST2 = "10.35.70.30"
PORT2 = 33005


def send_data(data_send, host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s2:
        s2.connect((host, port))
        s2.send(data_send.encode())
        data4 = s2.recv(1024)
        return data4


with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.bind((HOST2, PORT2))
    while True:
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                print('Message received from IP 1: ', addr)
                print('Data received is 1: ', data)
                new_data = data.decode('utf-8')
                data2 = new_data+" Jai Shree Ram"
                data3 = data2 + "Data appended by Amogh"
                data4 = send_data(data3, HOST, PORT)
                conn.sendall(data4)




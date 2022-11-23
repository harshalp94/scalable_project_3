#!/usr/bin/env python3

import argparse
import random
import selectors
import socket
import time
import types
ROUTER_IP='127.0.0.1'
CLIENT_IP='127.0.0.1'
ROUTER_PORT=33301
CLIENT_PORT=33302
data_dictionary = {'cpu_temperature': 'None', 'gpu_temperature': 'None'}
def getData(data_type):
    requestData(data_type)
    while data_dictionary[data_type] == None:
        pass
    return data_dictionary[data_type]

def requestData(data_type):
    send(ROUTER_IP, ROUTER_PORT, 'request:'+data_type)

def processRequest(source_host, data_type, data):
    data_dictionary[data_type] = data

def send(ip,port,msg):
        sent = False
        # if command == 'ALERT':´
        peer = (ip,port)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(peer)
            s.send(msg.encode())
            sent = True
            s.close()
        except Exception:
            print("Exception")
        if sent:
            print("Transmission finished")

def listen():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((CLIENT_IP, CLIENT_PORT))
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
                    data2 = new_data + " Jai Shree Ram"
                    data3 = data2 + "Data appended by Amogh"
                    data4 = send_data(data3, HOST, PORT)
                    conn.sendall(data4)
def main():
    # parser = argparse.ArgumentParser()
    # parser.add_argument('--command', help='Type of sensor', required=True)
    # args = parser.parse_args()
    command_name = ['vehicle/speed', 'vehicle/proximity', 'vehicle/tyre/pressure']
    while True:
        for c in command_name:
            time.sleep(10)
            sendData(c)
        time.sleep(5)
    # port_table = {'VehiclePort': 33401}  # Hardcoded port table for testing
    # port = port_table['VehiclePort']     # The port used by the server

    # sendData(command_name)
    # initial_message = sensorType + " 1"
    # byte_messages = [initial_message.encode('UTF-8')]

    # The server's hostname or IP address
    # host = socket.gethostbyname(socket.gethostname())


if __name__ == '__main__':
    main()
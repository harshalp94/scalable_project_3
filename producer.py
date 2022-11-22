#!/usr/bin/env python3

import socket
import threading
import time
from data_handler import *

RUNNING = True


# Tell router what type of data we are producing, every x seconds
def advertise(host, port, delay):
    index = 0
    while RUNNING:
        datatype = DATA_TYPES[index]
        data = encode_data(PRODUCING_ACTION, datatype)
        print(f'Advertising producing {datatype} to {host}:{port}')
        send_raw_data(host, port, data)

        index += 1
        if index >= len(DATA_TYPES):
            index = 0
        time.sleep(delay)


# Request data from the router every x seconds
def requester(host, port, delay):
    index = 0
    while RUNNING:
        datatype = DATA_TYPES[index]
        print(f'Requesting {datatype} from {host}:{port}')
        request = encode_data(REQUESTING_ACTION, datatype)
        send_raw_data(host, port, request)

        index += 1
        if index >= len(DATA_TYPES):
            index = 0
        time.sleep(delay)


# Send data using raw sockets
def send_raw_data(host, port, data):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(data.encode())
    data4 = s.recv(1024)
    return data4


def decode_request(data):
    action, datatype, consumer_host, consumer_port = data.decode('utf-8').split()
    if action != REQUESTING_ACTION:
        raise Exception(f'Expected {REQUESTING_ACTION} got {action} instead')
    else:
        return datatype, consumer_host, consumer_port


def process_incoming_connection(data):
    action, datatype, data = decode_data(data)
    if action == SENDTO_ACTION:
        requested_data = encode_data(datatype, "VERY GOOD DATA")  # TODO return smth more sensible
        consumer_host = data['consumer_host']
        consumer_port = data['consumer_port']
        send_raw_data(consumer_host, consumer_port, requested_data)
    elif action == SENDING_ACTION:
        print(f'Received data of type {datatype}: {data}')
    else:
        print(f'Received unexpected action {action}')


# Listen for data requests or incoming data
def listen(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        while RUNNING:
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connection started by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    process_incoming_connection(data.decode('utf-8'))


def get_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


def main():
    threads = [
        # Listen for data requests from the router
        threading.Thread(target=listen, args=(get_ip(), PI_PORT)),
        # Tell the router what type of data we are collecting
        threading.Thread(target=advertise, args=(ROUTER_HOST, ROUTER_PORT, 10)),
        # Request data from other producers
        threading.Thread(target=requester, args=(ROUTER_HOST, ROUTER_PORT, 10))
    ]

    for thread in threads:
        thread.start()

    # Run until user input
    input('Enter quit to stop program\n')
    RUNNING = False
    # Wait for threads to quit
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()

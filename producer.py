#!/usr/bin/env python3

import socket
import threading
import time

ROUTER_HOST = "10.35.70.30"
ROUTER_PORT = 33005
PI_PORT = ROUTER_PORT
REQUESTING_ACTION = "requesting"


# Tell router what type of data we are producing, every x seconds
def advertise(host, port, delay):
    while True:
        data = "Producing vehicle/speed"  # TODO make this change periodically
        send_raw_data(host, port, data)
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


def get_data(datatype):
    return "VERY GOOD DATA"  # TODO return something more sensible


def process_data_request(data):
    datatype, consumer_host, consumer_port = decode_request(data)
    requested_data = get_data(datatype)
    send_raw_data(consumer_host, consumer_port, requested_data)


# Listen for data requests
def listen(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        while True:
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connection started by {addr}")
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    process_data_request(data)


def get_ip():
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


def main():
    listener_thread = threading.Thread(target=listen, args=(get_ip(), PI_PORT))
    listener_thread.start()

    advertising_thread = threading.Thread(target=advertise, args=(ROUTER_HOST, ROUTER_PORT, 10))
    advertising_thread.start()

    # Run until user input
    input('Enter quit to stop program\n')


if __name__ == '__main__':
    main()

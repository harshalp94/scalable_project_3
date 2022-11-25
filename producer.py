#!/usr/bin/env python3

import socket
import threading
import time
from base_utils import *

RUNNING = True
VEHICLE_TYPE = "bike"


# Tell router what type of data we are producing, every x seconds
def advertise(delay):
    index = 0
    while RUNNING:
        # TODO we can send multiple types of data at once
        # We should also only send data of the same type as this vehicle
        datatypes = DATA_TYPES[index]
        data = f'HOST {get_host(socket)} PORT {PEER_PORT} ACTION {datatypes}'
        print(f'Advertising producing {datatypes} to {ROUTER_HOST}:{ROUTER_PORT}')
        send_raw_data(ROUTER_HOST, ROUTER_PORT, data)

        index += 1
        if index >= len(DATA_TYPES):
            index = 0
        time.sleep(delay)


# Send data using raw sockets
def send_raw_data(host, port, data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((host, port))
        s.send(data.encode())


def generate_data(datatype):
    # TODO return something more relevant
    return "VERY GOOD DATA"


# Listen for data requests or incoming data
def listen():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((get_host(socket), PEER_PORT))
        while RUNNING:
            s.listen()
            conn, addr = s.accept()
            with conn:
                print(f"Connection started by {addr}")

                data = conn.recv(1024)
                data = decode_msg(data.decode())
                # TODO might also have IP address for direct transfer
                print(f'{data} was requested')

                # Gather the data
                [vehicle_type, datatype] = data.split('/')
                if VEHICLE_TYPE == vehicle_type:
                    data = generate_data(datatype)

                # TODO if data is large, tell router, close connection and initiate direct HTTP transfer with consumer
                send_data_back(conn, data)


# Send requested data back to router on same connection
def send_data_back(conn, data):
    try:
        conn.send(encode_msg(data).encode())
    except Exception as e:
        print(f'Exception while sending data to router: {e}')


def main():
    threads = [
        # Listen for data requests from the router
        threading.Thread(target=listen, args=()),
        # Tell the router what type of data we are collecting
        threading.Thread(target=advertise, args=(10,)),
    ]

    for thread in threads:
        thread.start()

    # Run until user input
    input('Enter quit to stop program\n')
    global RUNNING
    RUNNING = False
    # Wait for threads to quit
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()

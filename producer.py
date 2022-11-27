#!/usr/bin/env python3

import socket
import threading
import time
from base_utils import *

RUNNING = True
VEHICLE_TYPE = VEHICLES[0]


# Tell router what type of data we are producing, every x seconds
def advertise(delay):
    index = 0
    while RUNNING:
        # TODO we can send multiple types of data at once, comma-delimited
        # We should also only send data of the same type as this vehicle
        datatypes = VEHICLE_TYPE + "/" + DATA_TYPES[VEHICLE_TYPE][index]
        data = f'HOST {get_host(socket)} PORT {PRODUCER_PORT_COMPAT} ACTION {datatypes}'
        print(f'Advertising producing {datatypes}')
        try:
            send_advertising_data(ROUTER_TUPLE, data)
        except Exception as e:
            print(f"Failed to advertise {e}")

        index += 1
        if index >= len(DATA_TYPES):
            index = 0
        time.sleep(delay)


def send_advertising_data(ROUTER_TUPLE, data):
    for tries in range(2):
        try:
            router_host, router_port = ROUTER_TUPLE[tries]
            print(f'Advertising to {router_host}:{router_port}')
            send_raw_data(router_host, router_port, data)
            break
        except Exception:
            continue


# Send data using tcp sockets
def send_raw_data(host, port, data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(3)
        s.connect((host, port))
        s.sendall(data.encode())


# Send requested data back to router on same connection
def send_data_back(conn, data):
    try:
        conn.send(encode_msg(data).encode())
    except Exception as e:
        print(f'Exception while sending data to router: {e}')


def generate_data(datatype):
    # TODO return something more relevant
    return "VERY GOOD DATA"


# Listen for data requests
def listen():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((get_host(socket), PRODUCER_PORT_COMPAT))
        s.listen(5)
        s.settimeout(3)
        while RUNNING:
            try:
                conn, addr = s.accept()
                with conn:
                    print(f"Connection started by {addr}")

                    raw_data = conn.recv(1024)
                    print("Raw data received:", raw_data)
                    data = decode_msg(raw_data.decode())
                    split_data = data.split()
                    if len(split_data) > 2:
                        data, consumer_host, consumer_port = split_data
                    print(f'Data {data} was requested')

                    # Gather the data
                    [vehicle_type, datatype] = data.split('/')
                    data = generate_data(datatype) if VEHICLE_TYPE == vehicle_type else "Wrong vehicle type"

                    # If data too large send p2p to consumer
                    # We check we were sent IP to be compatible with common protocol
                    if len(split_data) > 2 and len(data) > LARGE_DATA_THRESHOLD:
                        send_data_back(conn, PAYLOAD_TOO_LARGE_STRING)
                        # Send large data directly to peer on separate thread
                        threading.Thread(target=send_raw_data, args=(consumer_host, consumer_port, data))
                    else:
                        send_data_back(conn, data)
                        print("We sent the data back:", data)
            except TimeoutError:
                continue


def main():
    threads = [
        # Listen for data requests from the router
        threading.Thread(target=listen),
        # Tell the router what type of data we are collecting
        threading.Thread(target=advertise, args=(10,)),
    ]

    for thread in threads:
        thread.start()

    # Run until user input
    try:
        input('Enter quit or press Ctrl-C to stop program\n')
    except KeyboardInterrupt:
        pass

    print("Shutting down, please wait 3 seconds...")

    # Make sure we release socket binds properly
    global RUNNING
    RUNNING = False
    # Wait for threads to quit
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()

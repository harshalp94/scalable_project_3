#!/usr/bin/env python3

import socket
import threading
from base_utils import *

RUNNING = True

requested_types = {}


def send_msg(msg):
    for tries in range(2):
        try:
            router_host, router_port = INTEREST_ROUTER_TUPLE[tries]
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((router_host, router_port))
            s.send(encrypt_msg(msg))
            answer = s.recv(1024)
            decrypted = decrypt_msg(answer)
            s.close()
            return decrypted
        except Exception as exp:
            print(exp)


def request_data(data_type):
    answer = send_msg(data_type)
    print(f'Answer from router: {answer}')
    if answer == PAYLOAD_TOO_LARGE_STRING:
        print("Data too large, waiting for direct connection")
        requested_types.add(data_type)
    else:
        process_data(answer)


def listen():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', CONSUMER_PORT_COMPAT))
        s.listen(5)
        s.settimeout(3)
        while RUNNING:
            try:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(1024)
                    if not data:
                        continue
                    requested_types.pop()
                    threading.Thread(target=process_data, args=(data,), daemon=True).start()
            except TimeoutError:
                continue


# TODO this is where we would do something fancy with the received data
def process_data(data):
    print(f'Received data {data}')


def main():
    listen_thread = threading.Thread(target=listen)
    listen_thread.start()

    global RUNNING
    while RUNNING:
        try:
            vehicle = input("Enter vehicle to gather data about (help for possible types): ")
            while vehicle not in VEHICLES:
                print("Possible vehicles: " + ', '.join(str(e) for e in VEHICLES))
                vehicle = input("Enter vehicle to gather data about (help for possible types):")
            data_type = input("Enter data to gather (help for possible types): ")
            vehicle_data_types = DATA_TYPES[vehicle]
            while data_type not in vehicle_data_types:
                print("Possible data types: " + ', '.join(str(e) for e in vehicle_data_types))
                data_type = input("Enter data type (help for possible types): ")

            data_name = f'{vehicle}/{data_type}'
            request_data(data_name)
        except KeyboardInterrupt:
            RUNNING = False

    print("Shutting down, please wait 3 seconds...")

    # Make sure we release socket binds properly
    listen_thread.join()


if __name__ == '__main__':
    main()

#!/usr/bin/env python3

import socket
import threading
from base_utils import *

RUNNING = True


def send(msg):
    try:
        router_host, router_port = INTEREST_ROUTER_TUPLE[0]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((router_host, router_port))
        s.send(str(encode_msg(msg)).encode())
        answer = s.recv(1024)
        s.close()
        if answer:
            return decode_msg(answer.decode('utf-8'))
        else:
            return None
    except Exception:
        router_host, router_port = INTEREST_ROUTER_TUPLE[1]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((router_host, router_port))
        s.send(str(encode_msg(msg)).encode())
        answer = s.recv(1024)
        s.close()
        if answer:
            return decode_msg(answer.decode('utf-8'))
        else:
            return None


def request_data(data_type):
    answer = send(data_type)
    if answer == PAYLOAD_TOO_LARGE_STRING:
        print("Data too large, waiting for direct connection")
        # TODO we might want to store that we requested this data type in a set, and remove it once received
        # This way we can re-requested it after x seconds if we haven't gotten it yet
    else:
        process_data(answer)


def listen():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', CONSUMER_PORT))
        s.listen(5)
        s.settimeout(3)
        while RUNNING:
            try:
                conn, addr = s.accept()
                with conn:
                    data = conn.recv(1024)
                    if not data:
                        continue
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

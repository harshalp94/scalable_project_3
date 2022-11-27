#!/usr/bin/env python3

import socket
import threading

from base_utils import *

RUNNING = True


def send(ip, port, msg):
    peer = (ip, port)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(peer)
        s.send(str(encode_msg(msg)).encode())
        answer = s.recv(1024)
        s.close()
        if answer:
            return decode_msg(answer.decode('utf-8'))
        else:
            return None
    except Exception as e:
        print("Exception", e)


def get_data(data_type):
    answer = send(ROUTER_HOST, ROUTER_INTEREST_PORT, data_type)
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


def process_data(data):
    print(f'Received data {data}')


def main():
    listen_thread = threading.Thread(target=listen)
    listen_thread.start()

    global RUNNING
    while RUNNING:
        try:
            data_type = input("Enter data to fetch: ")
            get_data(data_type)
        except KeyboardInterrupt:
            RUNNING = False

    print("Shutting down, please wait 3 seconds...")

    # Make sure we release socket binds properly
    listen_thread.join()


if __name__ == '__main__':
    main()

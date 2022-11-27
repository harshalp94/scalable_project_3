#!/usr/bin/env python3

import base64
import socket
import time
from base_utils import *

ROUTER_IP='127.0.0.1'
ROUTER_REQUEST_PORT=33301
CLIENT_IP='127.0.0.1'
LISTEN_PORT=33302


def base64encode(msg):
    return base64.b64encode(msg.encode("ascii")).decode("ascii")


def base64decode(msg):
    return base64.b64decode(msg.encode("ascii")).decode("ascii")


def send(msg):
    try:
        router_host, router_port = INTEREST_ROUTER_TUPLE[0]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((router_host, router_port))
        s.send(str(base64encode(msg)).encode())
        answer = s.recv(1024)
        s.close()
        if answer:
            return base64decode(answer.decode('utf-8'))
        else:
            return None
    except Exception:
        router_host, router_port = INTEREST_ROUTER_TUPLE[1]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((router_host, router_port))
        s.send(str(base64encode(msg)).encode())
        answer = s.recv(1024)
        s.close()
        if answer:
            return base64decode(answer.decode('utf-8'))
        else:
            return None


def get_data(data_type):
    result = send(data_type)
    if result:
        return result
    else:
        return listen()


def listen():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((CLIENT_IP, LISTEN_PORT))
        while True:
            s.listen()
            conn, addr = s.accept()
            with conn:
                while True:
                    data = conn.recv(1024)
                    if not data:
                        break
                    return data


def main():
    while True:
        data_type = input("Enter data to fetch:")
        print(data_type + ": " + get_data(data_type))
        time.sleep(5)


if __name__ == '__main__':
    main()

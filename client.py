#!/usr/bin/env python3

import base64
import socket
import time
from base_utils import *
from cryptography.fernet import Fernet

ROUTER_IP='127.0.0.1'
ROUTER_REQUEST_PORT=33310
CLIENT_IP='127.0.0.1'
LISTEN_PORT=33302

cipher_suite = Fernet(ENCRYPTION_KEY)

def base64encode(msg):
    return base64.b64encode(msg.encode("ascii")).decode("ascii")


def base64decode(msg):
    return base64.b64decode(msg.encode("ascii")).decode("ascii")


def send(msg):
    try:
        router_host, router_port = INTEREST_ROUTER_TUPLE[0]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((router_host, router_port))
        s.send(cipher_suite.encrypt(str(base64encode(msg)).encode()))
        answer = s.recv(1024)
        answer = cipher_suite.decrypt(answer)
        s.close()
        if answer:
            return base64decode(answer.decode('utf-8'))
        else:
            return None
    except Exception:
        router_host, router_port = INTEREST_ROUTER_TUPLE[1]
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((router_host, router_port))
        s.send(cipher_suite.encrypt(str(base64encode(msg)).encode()))
        answer = s.recv(1024)
        answer = cipher_suite.decrypt(answer)
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
        vehicle = input("Enter vehicle to gather data about (help for possible types):")
        vehicles = ['bus', 'train', 'tram', 'metro', 'taxi']
        while vehicle not in vehicles:
            print("Possible vehicles: " + ', '.join(str(e) for e in vehicles))
            vehicle = input("Enter vehicle to gather data about (help for possible types):")
        data_type = input("Enter data to gather (help for possible types):")
        match vehicle:
            case 'bus':
                data_types = ['position', 'passengers', 'waiting', 'maintain', 'in_service', 'destination',
                              'ambient_temperature', 'fuel_sensor']
            case 'tram':
                data_types = ['position', 'passengers', 'waiting', 'maintain', 'in_service', 'destination',
                              'ambient_temperature', 'track_temperature']
            case 'taxi':
                data_types = ['position', 'passengers', 'waiting', 'maintain', 'in_service', 'destination',
                              'ambient_temperature', 'fuel_sensor']
            case 'train':
                data_types = ['position', 'passengers', 'waiting', 'maintain', 'in_service', 'destination',
                              'ambient_temperature', 'fuel_sensor', 'locomotive', 'track_temperature']
            case 'metro':
                data_types = ['position', 'passengers', 'waiting', 'maintain', 'in_service', 'destination',
                              'ambient_temperature', 'locomotive', 'track_temperature']
        while data_type not in data_types:
            print("Possible data types: " + ', '.join(str(e) for e in data_types))
            data_type = input("Enter data type (help for possible types):")

        data_name = vehicle + data_type
        print(data_name + ": " + get_data(data_name))
        time.sleep(5)


if __name__ == '__main__':
    main()

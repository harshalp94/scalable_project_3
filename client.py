#!/usr/bin/env python3

import socket
import threading
import re
from base_utils import *

RUNNING = True


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
    else:
        process_data(answer)


def listen():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', CONSUMER_PORT_COMPAT))
        s.listen(5)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        while RUNNING:
            conn, addr = s.accept()
            with conn:
                data = conn.recv(1024)
                if not data:
                    continue
                decrypted_data = decrypt_msg(data)
                threading.Thread(target=process_data, args=(decrypted_data,), daemon=True).start()


# TODO this is where we would do something fancy with the received data
def process_data(data):
    [datatype, datavalue] = data.split(' ')
    [vehicle, vehicle_property] = datatype.split('/')

    if vehicle_property == "fuel_sensor" and int((datavalue.replace('%', ''))) < 10:
        print(f'Less than 10% of fuel left for vehicle {vehicle}.')
    if vehicle_property == "maintain" and datavalue == 'True':
        print(f'Vehicle {vehicle} needs maintenance.')
    if vehicle_property == "track_temperature" and int(datavalue) > 50:
        print(f'Track temperature for train {vehicle} is too high.')


def main():
    listen_thread = threading.Thread(target=listen, daemon=True)
    listen_thread.start()

    global RUNNING
    while RUNNING:
        try:
            vehicle_string = input("Enter vehicle to gather data about (help for possible types): ")
            vehicle_num = re.findall(r'\d+', vehicle_string)[0]
            vehicle_type = vehicle_string.replace(vehicle_num, '')

            while vehicle_type not in VEHICLES:
                print("Possible vehicles: " + ', '.join(str(e) for e in VEHICLES))
                vehicle_string = input("Enter vehicle to gather data about (help for possible types):")
                vehicle_num = re.findall(r'\d+', vehicle_string)[0]
                vehicle_type = vehicle_string.replace(vehicle_num, '')

            data_type = input("Enter data to gather (help for possible types): ")
            vehicle_data_types = DATA_TYPES[vehicle_type]
            while data_type not in vehicle_data_types:
                print("Possible data types: " + ', '.join(str(e) for e in vehicle_data_types))
                data_type = input("Enter data type (help for possible types): ")

            data_name = f'{vehicle_string}/{data_type}'
            request_data(data_name)
        except KeyboardInterrupt:
            RUNNING = False

    print("Shutting down...")


if __name__ == '__main__':
    main()

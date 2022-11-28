#!/usr/bin/env python3

import sys
import socket
import threading
import time
import random
import re
from base_utils import *

RUNNING = True
# Vehicle type can be passed in as first command-line argument
VEHICLE_TYPE = VEHICLES[0]
# Vehicle number can be passed in as second command-line argument
VEHICLE_NUM = 1


# Tell router what type of data we are producing, every x seconds
def advertise(delay):
    while RUNNING:
        advertising_message = f'HOST {get_host(socket)} PORT {PRODUCER_PORT_COMPAT} ACTION '
        for data_type in DATA_TYPES[VEHICLE_TYPE]:
            advertising_message += f'{VEHICLE_TYPE}{VEHICLE_NUM}/{data_type},'
        advertising_message = advertising_message[:-1]  # Remove trailing comma
        try:
            send_advertising_data(ROUTER_TUPLE, advertising_message)
        except Exception as e:
            print(f"Failed to advertise {e}")

        time.sleep(delay)


def send_advertising_data(router_tuple, data):
    for tries in range(2):
        try:
            router_host, router_port = router_tuple[tries]
            print(f'Advertising {data} {router_host}:{router_port}')
            send_raw_data(router_host, router_port, data)
            break
        except Exception:
            continue


# Send data using tcp sockets
def send_raw_data(host, port, data):
    print(f'We are sending {data} to {host}:{port}')
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((host, port))
        s.sendall(encrypt_msg(data))


# Listen for data requests
def listen():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((get_host(socket), PRODUCER_PORT_COMPAT))
        s.listen(5)
        while RUNNING:
            conn, addr = s.accept()
            with conn:
                print(f"Connection started by {addr}")

                raw_data = conn.recv(1024)
                requested_data = decrypt_msg(raw_data)
                split_data = requested_data.split()
                if len(split_data) > 1:
                    requested_data = split_data[0]
                    consumer_host = split_data[1]

                # Whether a direct transfer was requested
                direct_transfer = split_data[2] if len(split_data) > 2 else False

                print(f'Data {requested_data} was requested')

                # Gather the data
                [vehicle_string, datatype] = requested_data.split('/')
                vehicle_num = re.findall(r'\d+|\*', vehicle_string)[0]
                vehicle_type = vehicle_string.replace(vehicle_num, '')
                data_to_send = f'{VEHICLE_TYPE}{VEHICLE_NUM}/{datatype} {generate_data(vehicle_type, datatype)}' if VEHICLE_TYPE == vehicle_type else ""

                # If data too large send p2p to consumer
                # We check we were sent IP to be compatible with common protocol
                if direct_transfer or (len(split_data) > 1 and len(data_to_send) > LARGE_DATA_THRESHOLD):
                    print("Data too large, sending directly...")
                    send_data_back(conn, PAYLOAD_TOO_LARGE_STRING)
                    # Send large data directly to peer on separate thread
                    threading.Thread(target=send_raw_data,
                                     args=(consumer_host, CONSUMER_PORT_COMPAT, data_to_send)).start()
                else:
                    send_data_back(conn, data_to_send)
                    print("We sent the data back:", data_to_send)


def generate_boolean():
    return random.choice(['True', 'False'])


def generate_destination():
    return random.choice(['Harbour', 'City Hall', 'College'])


def generate_temperature():
    return str(random.randint(-10, 40))


def generate_track_position():
    return str(random.randint(0, 99)) + '/' + str(random.randint(0, 99))


def generate_gps_position():
    return str(random.randint(-9000, 9000) / 100) + ',' + str(random.randint(-9000, 9000) / 100)


def generate_percentage():
    return str(random.randint(0, 100)) + '%'


def generate_integer():
    return str(random.randint(0, 300))


def generate_data(vehicle, specific_type):
    if specific_type == 'waiting':
        return generate_boolean()
    elif specific_type == 'maintain':
        return generate_boolean()
    elif specific_type == 'in_service':
        return generate_boolean()
    elif specific_type == 'ambient_temperature':
        return generate_temperature()
    elif specific_type == 'track_temperature':
        return generate_temperature()
    elif specific_type == 'locomotive':
        return generate_boolean()
    elif specific_type == 'position':
        if vehicle == 'train' or vehicle == 'metro' or vehicle == 'tram':
            return generate_track_position()
        else:
            return generate_gps_position()
    elif specific_type == 'fuel':
        return generate_percentage()
    elif specific_type == 'passengers':
        return generate_integer()
    elif specific_type == 'destination':
        return generate_destination()
    else:
        print(f'Error: data type {vehicle}/{specific_type} not known')


# Send requested data back to router on same connection
def send_data_back(conn, data):
    try:
        conn.send(encrypt_msg(data))
    except Exception as e:
        print(f'Exception while sending data to router: {e}')


def main():
    global VEHICLE_TYPE
    # Take vehicle type as first command-line argument
    if len(sys.argv) > 1:
        vehicle_type = sys.argv[1]
        if vehicle_type in VEHICLES:
            VEHICLE_TYPE = vehicle_type
            print(f'Set vehicle type to {vehicle_type}')
        else:
            print(f'Unknown vehicle type {vehicle_type}, defaulting to {VEHICLE_TYPE}')

    # Take vehicle number as second command-line argument
    global VEHICLE_NUM
    if len(sys.argv) > 2:
        vehicle_number = sys.argv[2]
        try:
            number = int(vehicle_number)
            VEHICLE_NUM = number
            print(f'Set vehicle number to {number}')
        except ValueError:
            print(f'Unknown vehicle number {vehicle_number}, defaulting to {VEHICLE_NUM}')

    threads = [
        # Listen for data requests from the router
        threading.Thread(target=listen, daemon=True),
        # Tell the router what type of data we are collecting
        threading.Thread(target=advertise, args=(10,), daemon=True),
    ]

    for thread in threads:
        thread.start()

    # Run until user input
    global RUNNING
    try:
        while RUNNING:
            pass
    except KeyboardInterrupt:
        pass

    print("Shutting down...")


if __name__ == '__main__':
    main()

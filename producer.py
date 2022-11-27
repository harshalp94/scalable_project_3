#!/usr/bin/env python3

import socket
import threading
import time
import random
from base_utils import *

RUNNING = True
VEHICLE_TYPE = "bike"
# Data size threshold after which we use a direct peer transfer instead of going through the router
LARGE_DATA_THRESHOLD = 20


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


# Send data using tcp sockets
def send_raw_data(host, port, data):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(3)
        s.connect((host, port))
        s.sendall(data.encode())


def generate_boolean():
    return random.choice('True', 'False')


def generate_destination():
    return random.choice('Harbour', 'City Hall', 'College')


def generate_temperature():
    return str(random.randint(-10, 40))


def generate_track_position():
    return str(random.randint(0, 99)) + '/' + str(random.randint(0, 99))


def generate_gps_position():
    return str(random.randint(-9000, 9000)/100) + ',' + str(random.randint(-9000, 9000)/100)


def generate_percentage():
    return str(random.randint(0, 100)) + '%'


def generate_integer():
    return str(random.randint(0, 300))


def generate_data(datatype):
    [vehicle, specific_type] = datatype.split('/')
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
        if vehicle == 'train' | vehicle == 'metro' | vehicle == 'tram':
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
        print('Error: data type ' + datatype + ' not known')


# Listen for data requests or incoming data
def listen():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((get_host(socket), PEER_PORT))
        while RUNNING:
            s.listen()  # TODO make non-blocking to be able to stop threads
            conn, addr = s.accept()
            with conn:
                print(f"Connection started by {addr}")

                data = conn.recv(1024)
                data = decode_msg(data.decode())
                split_data = data.split()
                if len(split_data) > 2:
                    data, consumer_host, consumer_port = split_data
                print(f'{data} was requested')

                # Gather the data
                [vehicle_type, datatype] = data.split('/')
                data = generate_data(datatype) if VEHICLE_TYPE == vehicle_type else ""

                # If data too large send p2p to consumer
                # We check we were sent IP to be compatible with common protocol
                if len(split_data) > 2 and len(data) > LARGE_DATA_THRESHOLD:
                    s.send(b"HTTP/1.1 413 Payload Too Large")
                    # Send large data directly to peer on separate thread
                    threading.Thread(target=send_raw_data, args=(consumer_host, consumer_port, data))
                else:
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
    try:
        input('Enter quit to stop program\n')
    except KeyboardInterrupt:
        pass

    global RUNNING
    RUNNING = False
    # Wait for threads to quit
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()

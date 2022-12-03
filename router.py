# authors: Harshal Patil, Amogh Anil Rao

import socket
import threading
import re
from base_utils import *

RUNNING = True
map_dict = {}


def split_str(act_string):
    temp_str = act_string[1].replace('[', '').replace(']', '').replace(' ', '').lower()
    return str(temp_str)


# Takes e.g. bus1/position or bus*/position or bus2/* or bus*/*, returns dictionary of interest,host
def find_producers_with_requested_data(interest):
    return_dict = dict()

    [vehicle_string, datatype] = interest.split('/')
    vehicle_num = re.findall(r'\d+|\*', vehicle_string)[0]
    vehicle_type = vehicle_string.replace(vehicle_num, '')

    if '*' not in interest:
        if interest in map_dict:
            return_dict[interest] = map_dict[interest]
    else:
        for k, v in map_dict.items():
            if (vehicle_num == '*' or k.startswith(vehicle_type)) and (datatype == '*' or k.endswith(datatype)):
                return_dict[k] = v

    return return_dict


def request_data_from_producer(peer, command, consumer_host, direct_transfer=False):
    """Send sensor data to all peers."""
    print("What is peer and command :{} {}".format(peer, command))
    print(f"Data requested by {consumer_host}")
    print(f"Requesting {command} from {peer}:{PRODUCER_PORT_COMPAT}")
    try:
        # Request data from producer
        msg = f'{command} {consumer_host} {direct_transfer}'
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((peer, PRODUCER_PORT_COMPAT))
        encrypted_message = encrypt_msg(msg)
        s.send(encrypted_message)
        received_data = s.recv(1024)

        print("Data received:", received_data)
        decoded_data = decrypt_msg(received_data)
        print("Decoded data:", decoded_data)
        s.close()
        return decoded_data
    except Exception as e:
        print("An exception occurred requesting data", e)
        # self.remove_node(peer,command)


class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peers = set()

    def advertising_listener(self):
        """Update peers list on receipt of their address broadcast."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', ROUTER_ADVERTISING_PORT_COMPAT))
        s.listen(5)
        while RUNNING:
            conn, addr = s.accept()
            data = conn.recv(1024)
            data = decrypt_msg(data)
            dataMessage = data.split(' ')
            action_list = split_str(data.split('ACTION '))
            host = dataMessage[1]
            port = int(dataMessage[3])
            peer = (host, port, action_list)

            if peer not in self.peers:
                self.peers.add(peer)
                print('Known Public transport Vehicles:', self.peers)
                self.add_adv_peer()

    def data_requests_listener(self):
        """Listen on own port for a data request"""
        print("Listening for data requests...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', ROUTER_REQUEST_PORT_COMPAT))
        s.listen(10)
        while RUNNING:
            conn, addr = s.accept()
            print("addr: ", addr[0])
            print("connection: ", str(conn))
            data = conn.recv(1024)
            print("Received data", data)
            decrypted = decrypt_msg(data)
            print("Base 64 decode data", decrypted)
            # print(utf_data, " to actuate on")
            interest = decrypted.lower()
            print("Final interest", interest)

            # Key dictionary of interest,host
            found_producers: dict = find_producers_with_requested_data(interest)

            if len(found_producers) <= 0:
                print("Data not found!")
                send_err_ack(conn)
            elif len(found_producers) <= 1:
                received_data = request_data_from_producer(found_producers.popitem()[1], interest, addr[0])
                if received_data is None or received_data == '':
                    send_err_ack(conn)
                else:
                    send_data_to_cons(received_data, conn)
            else:
                # Multiple data requests, send via direct transfer
                send_data_to_cons(MULTIPLE_CHOICES_STRING, conn)
                for specific_interest, producer in found_producers.items():
                    request_data_from_producer(producer, specific_interest, addr[0], True)

            conn.close()

    def add_adv_peer(self):
        for peer in self.peers:
            host = peer[0]
            action_list = peer[2].split(',')
            for action in action_list:
                map_dict[action] = host


def send_err_ack(conn):
    msg = "404 not found"
    encoded_msg = encrypt_msg(msg)
    conn.send(encoded_msg)
    return


def send_data_to_cons(message, conn):
    encoded_msg = encrypt_msg(message)
    print(f'Sending data to consumer... {encoded_msg}')
    conn.send(encoded_msg)
    return


def main():
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    peer = Peer(host, PRODUCER_PORT_COMPAT)

    threads = [
        threading.Thread(target=peer.advertising_listener, daemon=True),
        threading.Thread(target=peer.data_requests_listener, daemon=True)
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

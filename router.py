import socket
import threading
import time
import base64
from cryptography.fernet import Fernet
from base_utils import *

from base_utils import *

RUNNING = True
map_dict = {}

cipher_suite = Fernet(ENCRYPTION_KEY)

def tabular_display(temp_dict):
    print("{:<25} | {:<15}".format('ACTION', 'IP_ADDR'))
    for key, val in temp_dict.items():
        print("{:<25} | {:<15}".format(key, str(val)))


class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peers = set()

    def updatePeerList(self):
        """Update peers list on receipt of their address broadcast."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', ROUTER_ADVERTISING_PORT_COMPAT))
        s.settimeout(3)
        s.listen(5)
        while RUNNING:
            try:
                conn, addr = s.accept()
                # print("BRaddr: ", addr[0])
                # print("BRconnection: ", str(conn))
                data = conn.recv(1024)
                data = cipher_suite.decrypt(data)
                # #print("Base 64 decode data updat peer", data)
                # base64_decode_data = self.decode(data)
                # print("Base 64 decode data updat peer", base64_decode_data)
                # utf_data = base64_decode_data.decode(data)
                # print("utd 8 decode data updat peer", utf_data)
                # print(data, " Peer List data")
                # #data, _ = s.recvfrom(1024)
                data = data.decode()
                # print("received message:", data)
                dataMessage = data.split(' ')
                action_list = self.split_using_act(data.split('ACTION '))
                command = dataMessage[0]
                if command == 'HOST':
                    host = dataMessage[1]
                    port = int(dataMessage[3])
                    if len(dataMessage) > 5:
                        action = dataMessage[5]
                    else:
                        action = ''
                    # host = dataMessage[1]
                    # port = int(dataMessage[3])

                    peer = (host, port, action_list)

                    if peer not in self.peers:
                        self.peers.add(peer)
                        print('Known vehicles:', self.peers)
                        self.maintain_router()
            except TimeoutError:
                continue

    def parse_interest(self, interest):
        return interest
        # inter = interest.split("/")
        # return inter[len(inter) - 1]

    def filter_ips(self, data):
        if data in map_dict.keys():
            return map_dict[data]
        else:
            return None

    def split_using_act(self, act_string):

        temp_str = act_string[1].replace('[', '').replace(']', '').replace(' ', '').lower()
        # new_ls = temp_str.split(',')
        return str(temp_str)

    def send_none_to_interested_node(self, host, conn):
        msg = "404 not found"
        encoded_msg = cipher_suite.encrypt(str(encode_msg(msg)).encode())
        conn.send(encoded_msg)
        return

    def receiveData(self):
        """Listen on own port for other peer data."""
        print("Listening for data requests...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', ROUTER_REQUEST_PORT_COMPAT))
        s.settimeout(3)
        s.listen(5)
        while RUNNING:
            try:
                conn, addr = s.accept()
                print("addr: ", addr[0])
                print("connection: ", str(conn))
                data = conn.recv(1024)
                print("Received data", data)
                data = cipher_suite.decrypt(data)
                print("Data After Decryption", data)
                utf_data = data.decode()
                print("Decoded data", utf_data)
                base64_decode = decode_msg(utf_data)
                print("Base 64 decode data", base64_decode)
                # print(utf_data, " to actuate on")
                interest = self.parse_interest(base64_decode.lower())
                print("Final interest", interest)
                filtered_ips = self.filter_ips(interest)
                if filtered_ips is None:
                    print("Data not found!")
                    self.send_none_to_interested_node(addr[0], conn)
                else:
                    received_data = self.route_to_pi(filtered_ips, interest, addr)
                    self.send_back_to_interested_node(received_data, addr[0], conn)
                conn.close()
            except TimeoutError:
                continue

    def send_back_to_interested_node(self, message, host, conn):
        # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # s.connect((host,INTEREST_PORT))
        encoded_msg = cipher_suite.encrypt(str(encode_msg(message)).encode())
        print(f'Sending data to consumer... {encoded_msg}')
        conn.send(encoded_msg)
        return

    def remove_node(self, node, command):
        try:
            print("REMOVING NODE", node)
            if node in map_dict[command]:
                map_dict[command].remove(node)
            print("UPDATED MAP DICT", tabular_display(map_dict))
        except:
            print("ERROR IN REMOVING NODE")

    def route_to_pi(self, peer_list, command, consumer_address):
        """Send sensor data to all peers."""
        print("What is peer list and command :{} {}".format(peer_list, command))
        for peer in peer_list:
            print(f"Data requested by {consumer_address}")
            print(f"Requesting {command} from {peer}:{PRODUCER_PORT_COMPAT}")
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((peer, PRODUCER_PORT_COMPAT))
                encoded_message = cipher_suite.encrypt(str(encode_msg(command)).encode())
                s.send(encoded_message)
                received_data = s.recv(1024)
                received_data = cipher_suite.decrypt(received_data)
                print("Data received:", received_data)
                utf_decode = received_data.decode()
                decoded_data = decode_msg(utf_decode)
                print("Decoded data:", decoded_data)
                s.close()
                return decoded_data
            except Exception as e:
                print("An exception occurred requesting data", e)
                continue
                # self.remove_node(peer,command)

    def maintain_router(self):
        empty_set = set()
        count = 1
        for peer in self.peers:
            # print("No of iterations", count)
            # print("Inside peer", peer)
            host = peer[0]
            # print("Inside host",host)
            port = peer[1]
            action_list = peer[2].split(',')
            # print("Inside action", action)
            for action in action_list:
                if action in map_dict.keys():
                    temp_set = map_dict[action]
                    temp_set.add(host)
                    map_dict[action] = temp_set
                else:
                    empty_set.add(host)
                    map_dict[action] = empty_set
            count += 1
        print("What is router table now", tabular_display(map_dict))


def main():
    hostname = socket.gethostname()
    host = socket.gethostbyname(hostname)
    peer = Peer(host, PRODUCER_PORT_COMPAT)

    threads = [
        threading.Thread(target=peer.updatePeerList),
        threading.Thread(target=peer.receiveData)
    ]

    for thread in threads:
        thread.start()

    # Run until user input
    global RUNNING
    try:
        while RUNNING:
            pass
        #input('Enter quit or press Ctrl-C to stop program\n')
    except KeyboardInterrupt:
        pass

    print("Shutting down, please wait 3 seconds...")

    # Make sure we release socket binds properly
    RUNNING = False
    # Wait for threads to quit
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    main()

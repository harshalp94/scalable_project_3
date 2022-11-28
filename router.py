import socket
import threading
from base_utils import *

RUNNING = True
map_dict = {}


def split_str(act_string):
    temp_str = act_string[1].replace('[', '').replace(']', '').replace(' ', '').lower()
    return str(temp_str)


class Peer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.peers = set()

    def gen_adv_peer_list(self):
        """Update peers list on receipt of their address broadcast."""
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', ROUTER_ADVERTISING_PORT_COMPAT))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
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
            #self.remove_producer(host)
            if peer not in self.peers:
                self.peers.add(peer)
                print('Known Public transport Vehicles:', self.peers)
                self.add_adv_peer()

    def get_data(self):
        """Listen on own port for other peer data."""
        print("Listening for data requests...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(('', ROUTER_REQUEST_PORT_COMPAT))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.listen(5)
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
            #filtered_ips = map_dict[interest]
            if interest not in map_dict:
                print("Data not found!")
                send_err_ack(conn)
            else:
                received_data = self.request_data_from_producer(map_dict[interest], interest, addr[0])
                send_data_to_cons(received_data, conn)
            conn.close()

    # def remove_producer(self, host):
    #     for key, val in map_dict:
    #         if host in val:
    #             val.remove(host)
    #
    # def remove_node(self, node, command):
    #     try:
    #         print("REMOVING NODE", node)
    #         if node in map_dict[command]:
    #             map_dict[command].remove(node)
    #         print("UPDATED MAP DICT", tabular_display(map_dict))
    #     except Exception as exp:
    #         print("ERROR IN REMOVING NODE")

    def request_data_from_producer(self, peer, command, consumer_host):
        """Send sensor data to all peers."""
        print("What is peer and command :{} {}".format(peer, command))
        print(f"Data requested by {consumer_host}")
        print(f"Requesting {command} from {peer}:{PRODUCER_PORT_COMPAT}")
        try:
            # Request data from producer
            msg = f'{command} {consumer_host}'
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

    def add_adv_peer(self):
        #count = 1
        for peer in self.peers:
            host = peer[0]
            action_list = peer[2].split(',')
            for action in action_list:
                map_dict[action] = host
            #count += 1
        #print("What is router table now", tabular_display(map_dict))


# def filter_ips(data):
#         return map_dict[data]


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
        threading.Thread(target=peer.gen_adv_peer_list, daemon=True),
        threading.Thread(target=peer.get_data, daemon=True)
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

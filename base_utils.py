import base64

ROUTER_HOST = '10.35.70.30'
ROUTER_IP_1 = '10.35.70.31'

ROUTER_PORT = 33334
PEER_PORT = 33310  # Port for listening to other peers
SENSOR_PORT = 33401  # Port for listening to other sensors
PRODUCER_LISTENING_PORT = 33310
ROUTER_TUPLE = [(ROUTER_HOST, ROUTER_PORT), (ROUTER_IP_1, ROUTER_PORT)]
INTEREST_ROUTER_TUPLE = [(ROUTER_HOST, PEER_PORT), (ROUTER_IP_1, PEER_PORT)]
DATA_TYPES = ["bike/speed", "bike/engine_temp", "bike/battery_temp"]


def get_host(socket):
    """Get Pi's hostname from current socket"""
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


def encode_msg(toEncode):
    ascii_encoded = toEncode.encode("ascii")
    base64_bytes = base64.b64encode(ascii_encoded)
    base64_string = base64_bytes.decode("ascii")
    return base64_string


def decode_msg(toDecode):
    base64_bytes = toDecode.encode("ascii")
    sample_string_bytes = base64.b64decode(base64_bytes)
    sample_string = sample_string_bytes.decode("ascii")
    return sample_string

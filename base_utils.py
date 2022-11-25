import base64

ROUTER_HOST = '10.35.70.24'
ROUTER_PORT = 33334
PEER_PORT = 33301  # Port for listening to other peers
SENSOR_PORT = 33401  # Port for listening to other sensors

DATA_TYPES = ["ebike/speed", "ebike/engine_temp", "ebike/battery_temp"]


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

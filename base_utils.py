import base64

# ROUTER_HOST = '10.35.70.24' # For testing on Pi
ROUTER_HOST = '127.0.0.1'  # For testing locally
ROUTER_PORT = 33334
ROUTER_INTEREST_PORT = 33310

PRODUCER_PORT = 33301  # Port the producer expects requests to come in from
CONSUMER_PORT = 33302  # Port consumer expects requested data to come in from

# Data size threshold after which we use a direct peer transfer instead of going through the router
LARGE_DATA_THRESHOLD = 20
PAYLOAD_TOO_LARGE_STRING = "HTTP/1.1 413 Payload Too Large"

DATA_TYPES = ["ebike/speed", "ebike/engine_temp", "ebike/battery_temp"]


def get_host(socket):
    """Get Pi's hostname from current socket"""
    hostname = socket.gethostname()
    return socket.gethostbyname(hostname)


def encode_msg(to_encode):
    ascii_encoded = to_encode.encode("ascii")
    base64_bytes = base64.b64encode(ascii_encoded)
    base64_string = base64_bytes.decode("ascii")
    return base64_string


def decode_msg(to_decode):
    base64_bytes = to_decode.encode("ascii")
    sample_string_bytes = base64.b64decode(base64_bytes)
    sample_string = sample_string_bytes.decode("ascii")
    return sample_string

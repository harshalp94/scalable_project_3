import base64

# ROUTER_HOST = '10.35.70.24' # For testing on Pi
ROUTER_HOST = '127.0.0.1'  # For testing locally
ROUTER_IP_1 = '10.35.70.31'

# Set of ports that are compatible with common protocol
ROUTER_ADVERTISING_PORT_COMPAT = 33334  # Port router expects to receive advertising messages on
ROUTER_REQUEST_PORT_COMPAT = 33310  # Port router expects data requests to come in from
PRODUCER_PORT_COMPAT = 33301  # Port the producer expects requests to come in from
CONSUMER_PORT_COMPAT = 33302  # Port consumer expects requested data to come in from

# Set of ports for our own, better protocol supporting direct transfers and encryption
ROUTER_ADVERTISING_PORT_CRYPT = 33335  # Port router expects to receive advertising messages on
ROUTER_REQUEST_PORT_CRYPT = 33336  # Port router expects data requests to come in from
PRODUCER_PORT_CRYPT = 33337  # Port the producer expects requests to come in from
CONSUMER_PORT_CRYPT = 33338  # Port consumer expects requested data to come in from

# Data size threshold after which we use a direct peer transfer instead of going through the router
LARGE_DATA_THRESHOLD = 20
PAYLOAD_TOO_LARGE_STRING = "HTTP/1.1 413 Payload Too Large"

ROUTER_TUPLE = [(ROUTER_HOST, ROUTER_ADVERTISING_PORT_COMPAT), (ROUTER_IP_1, ROUTER_ADVERTISING_PORT_COMPAT)]
INTEREST_ROUTER_TUPLE = [(ROUTER_HOST, ROUTER_REQUEST_PORT_COMPAT), (ROUTER_IP_1, ROUTER_REQUEST_PORT_COMPAT)]
VEHICLES = ['bus', 'train', 'tram', 'metro', 'taxi']
DATA_TYPES = dict(
    bus=['position', 'passengers', 'waiting', 'maintain', 'in_service', 'destination', 'ambient_temperature',
         'fuel_sensor'],
    tram=['position', 'passengers', 'waiting', 'maintain', 'in_service', 'destination',
          'ambient_temperature', 'track_temperature'],
    taxi=['position', 'passengers', 'waiting', 'maintain', 'in_service', 'destination',
          'ambient_temperature', 'fuel_sensor'],
    train=['position', 'passengers', 'waiting', 'maintain', 'in_service', 'destination',
           'ambient_temperature', 'fuel_sensor', 'locomotive', 'track_temperature'],
    metro=['position', 'passengers', 'waiting', 'maintain', 'in_service', 'destination',
           'ambient_temperature', 'locomotive', 'track_temperature']
)


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

import json

ROUTER_HOST = "10.35.70.30"
ROUTER_PORT = 33005
PI_PORT = ROUTER_PORT
DATA_TYPES = ["vehicle/speed", "vehicle/engine_temp", "vehicle/internal_temp"]

# Actions
# A producer telling the router it is making this type of data, no data field needed
PRODUCING_ACTION = "producing"
# A consumer asking the router for a specific type of data, no data field needed
REQUESTING_ACTION = "requesting"
# The router requesting the producer send data to a consumer
# Data field must contain consumer_host and consume_port keys
SENDTO_ACTION = "sendto"
# A producer sending data to a consumer
SENDING_ACTION = "sending"


# Encode data in compact JSON for sending
def encode_data(action, datatype, data=None):
    json_dict = {
        'action': action,
        'type': datatype,
    }
    if data is not None:
        json_dict['data'] = data

    return json.dumps(json_dict, indent=None, separators=(',', ':'))


# Decode data from JSON. Returns (action, type, data) tuple
# data file may be None if there was no data
def decode_data(data):
    decoded = json.loads(data)
    output = (decoded['action'], decoded['type'], data['data'] if 'data' in data else None)
    return output

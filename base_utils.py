import base64


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

import json

def create_packet(packet_type, seq, data):
    return json.dumps({
        "type": packet_type,
        "seq": seq,
        "data": data
    }).encode()

def parse_packet(packet_bytes):
    return json.loads(packet_bytes.decode())
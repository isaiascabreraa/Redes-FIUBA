
BUFSIZE = 2040

''' | Type | Seq Num | Algoritmo | P Len |
    | 1B   |   4B    |    1B     |  2B   |
    |0 dow |         |  0  S&W   |
    |1 upl |         |  1  TCP   |
    |2 ack |
'''


def create_header(msg_type, seq_num, protocol, p_len):
    header = bytearray()
    header += msg_type.to_bytes(1, byteorder='big')
    header += seq_num.to_bytes(4, byteorder='big')
    header += protocol.to_bytes(1, byteorder='big')
    header += p_len.to_bytes(2, byteorder='big')
    return header


def create_segment(msg_type, seq_num, protocol, p_len, payload):
    header = create_header(msg_type, seq_num, protocol, p_len)

    segment = bytearray()
    segment += header
    segment += payload

    return segment


def get_header_and_payload(segment):
    header = segment[:8]
    payload = segment[8:]

    return header, payload


def is_ack(header):
    msg_type = header[0]
    return msg_type == 2


def get_seq_num(header):
    return int.from_bytes(header[1:5], byteorder='big')


def get_msg_type(header):
    msg_type = header[0]
    return msg_type


def get_protocol(header):
    return header[5]


def get_payload_length(header):
    return int.from_bytes(header[6:])


def get_sacks(payload):
    i = 0
    sacks = []
    if len(payload) >= 4:
        while i < len(payload):
            sack = int.from_bytes(payload[i:i+4], byteorder='big')
            sacks.append(sack)
            i += 4
    return sorted(sacks)

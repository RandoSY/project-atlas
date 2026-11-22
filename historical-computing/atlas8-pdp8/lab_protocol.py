"""ATLAS-8 laboratory device wire protocol v1. CPython/MicroPython compatible.

Frame: A5 version sequence opcode length payload crc16-hi crc16-lo.
CRC-16/CCITT-FALSE (initial FFFF, polynomial 1021), over version..payload.
Max payload eight bytes. Reply opcode = request | 80, payload begins status.
"""
SYNC = 0xA5
VERSION = 1
MAX_PAYLOAD = 8
IDENTIFY = 0x01
ADC_START = 0x10
ADC_READ = 0x11
TIMER_START = 0x20
TIMER_READ = 0x21
STATUS = 0x30
CLEAR = 0x31
OK = 0
BUSY = 1
NOT_READY = 2
BAD_ARGUMENT = 3
UNSUPPORTED = 4
FAULT = 5


def crc16(data):
    crc = 0xffff
    for value in data:
        crc ^= value << 8
        for _ in range(8):
            crc = ((crc << 1) ^ (0x1021 if crc & 0x8000 else 0)) & 0xffff
    return crc


def frame(seq, opcode, payload=b''):
    if not 0 <= seq <= 255 or not 0 <= opcode <= 255 or len(payload) > MAX_PAYLOAD:
        raise ValueError('bad lab protocol frame arguments')
    body = bytes((VERSION, seq, opcode, len(payload))) + bytes(payload)
    checksum = crc16(body)
    return bytes((SYNC,)) + body + bytes((checksum >> 8, checksum & 255))


class Decoder:
    """Incremental bounded decoder. Bad CRC/version/length resynchronizes."""
    def __init__(self):
        self.buffer = bytearray()
        self.errors = 0

    def feed(self, data):
        self.buffer.extend(data)
        packets = []
        while self.buffer:
            if self.buffer[0] != SYNC:
                del self.buffer[0]
                continue
            if len(self.buffer) < 5:
                break
            if self.buffer[1] != VERSION or self.buffer[4] > MAX_PAYLOAD:
                self.errors += 1
                del self.buffer[0]
                continue
            size = 7 + self.buffer[4]
            if len(self.buffer) < size:
                break
            check = (self.buffer[size-2] << 8) | self.buffer[size-1]
            if crc16(self.buffer[1:size-2]) != check:
                self.errors += 1
                del self.buffer[0]
                continue
            packets.append((self.buffer[2], self.buffer[3], bytes(self.buffer[5:size-2])))
            del self.buffer[:size]
        return packets

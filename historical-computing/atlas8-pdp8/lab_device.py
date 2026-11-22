"""PDP-8 laboratory IOT adapter and deterministic simulated MSP430 controller.

Reserved ATLAS extensions: device octal 54, IOT 6540/1/2/4/5.
NOT historical DEC instructions. Uses a single outstanding request and nonblocking
transport polling. No physical ADC value is ever fabricated in LIVE PICO mode.
"""
import lab_protocol as p
try:
    import utime as _clock
    def _now_ms(): return _clock.ticks_ms()
    def _elapsed_ms(now, before): return _clock.ticks_diff(now, before)
except ImportError:
    import time as _clock
    def _now_ms(): return _clock.monotonic_ns() // 1000000
    def _elapsed_ms(now, before): return now - before


class SimulatedController:
    """Wire-compatible MSP430 simulation for host tests and teaching.

    The ADC result is a fixed educational fixture; never claim it is hardware.
    Deferred completion requires two service polls to show BUSY -> READY.
    """
    def __init__(self):
        self.reset()

    def reset(self):
        self.busy = False
        self.ready = False
        self.timer = False
        self.countdown = 0
        self.value = 0

    def poll(self):
        if self.busy and self.countdown:
            self.countdown -= 1
            if not self.countdown:
                self.busy = False
                self.ready = True

    def handle(self, op, payload):
        if op == p.IDENTIFY and not payload:
            return p.OK, bytes((1, 0, 1))  # protocol major/minor, ADC present
        if op == p.ADC_START and len(payload) == 1 and payload[0] < 8 and payload[0] not in (1, 2):
            if self.busy:
                return p.BUSY, b''
            self.timer = False
            self.busy, self.ready, self.countdown = True, False, 2
            # Fixture is explicit: A0 => 512, A3 => 515.
            self.value = 512 + payload[0]
            return p.OK, b''
        if op == p.TIMER_START and not payload:
            if self.busy:
                return p.BUSY, b''
            self.timer = True
            self.busy, self.ready, self.countdown = True, False, 2
            self.value = 1000  # 1000 ticks @ nominal 1 MHz = 1 ms
            return p.OK, b''
        if op == p.STATUS and not payload:
            return p.OK, bytes((int(self.ready) | (int(self.busy) << 1),))
        if op == p.CLEAR and not payload:
            self.reset()
            return p.OK, b''
        if op in (p.ADC_READ, p.TIMER_READ) and not payload:
            if self.busy or not self.ready:
                return p.NOT_READY, b''
            if (op == p.TIMER_READ) != self.timer:
                return p.BAD_ARGUMENT, b''
            value = self.value
            self.ready = False
            return p.OK, (bytes((value & 255, (value >> 8) & 255)) if op == p.ADC_READ
                          else bytes((value & 255, (value >> 8) & 255,
                                      (value >> 16) & 255, (value >> 24) & 255)))
        return p.BAD_ARGUMENT if op in (p.ADC_START, p.TIMER_START, p.ADC_READ,
                p.TIMER_READ, p.STATUS, p.CLEAR, p.IDENTIFY) else p.UNSUPPORTED, b''


class SimTransport:
    def __init__(self):
        self.controller = SimulatedController()
        self.queued = []

    def send(self, seq, op, payload):
        # Enforce real frame encoding/CRC on the simulator too.
        decoder = p.Decoder()
        packet = decoder.feed(p.frame(seq, op, payload))[0]
        status, result = self.controller.handle(packet[1], packet[2])
        self.queued.append(p.frame(seq, op | 0x80, bytes((status,)) + result))

    def receive(self):
        self.controller.poll()
        frames = self.queued
        self.queued = []
        return frames

    def ready(self):
        return self.controller.ready


class LabPeripheral:
    """IOT-facing state. Every step takes bounded work; never sleeps in IOT."""
    def __init__(self, transport=None):
        self.transport = transport
        self.online = False
        self.reset()
        if self.transport:
            self._send(p.IDENTIFY, b'', 'identify')

    def reset(self):
        self.ready = False
        self.busy = False
        self.error = ''
        self.value = 0
        self.mode = 'adc'
        self.phase = None
        self.seq = getattr(self, 'seq', 0)  # Never reuse sequence after CPU reset.
        self.pending_seq = None
        self.pending_op = None
        self.age = 0
        self.sent_ms = None
        self.decoder = p.Decoder()
        self.last_status = None

    def _send(self, op, payload=b'', phase=None):
        if not self.transport:
            self.error = 'MSP430 disconnected'
            self.online = False
            return False
        self.seq = (self.seq + 1) & 255
        self.pending_seq = self.seq
        self.pending_op = op
        self.phase = phase
        self.age = 0
        self.sent_ms = _now_ms()
        self.transport.send(self.seq, op, payload)
        return True

    def start(self, channel=0, mode='adc'):
        if self.busy:
            self.error = 'lab device busy'
            return False
        if mode == 'adc' and (not 0 <= channel <= 7 or channel in (1, 2)):
            self.error = 'invalid ADC channel (A1/A2 reserved for UART)'
            return False
        self.ready = False
        self.error = ''
        self.mode = mode
        self.busy = True
        result = self._send(p.ADC_START if mode == 'adc' else p.TIMER_START,
                            bytes((channel,)) if mode == 'adc' else b'', 'ack')
        if not result:
            self.busy = False
        return result

    def clear(self):
        self.reset()
        if self.transport:
            self._send(p.CLEAR, b'', 'clear')

    def service(self):
        if not self.transport:
            return
        self.age += 1
        # If an MCU becomes unreachable, fail instead of hanging guest software.
        if self.pending_seq is not None and self.sent_ms is not None and \
                _elapsed_ms(_now_ms(), self.sent_ms) > 1200:
            self.error = 'lab response timeout'
            self.online = False
            self.busy = False
            self.pending_seq = None
            self.phase = None
            return
        try:
            for raw in self.transport.receive():
                for seq, op, payload in self.decoder.feed(raw):
                    if seq != self.pending_seq or op != (self.pending_op | 0x80):
                        continue
                    self.pending_seq = None
                    self.online = True  # Recognized reply from a real device.
                    if not payload or payload[0] != p.OK:
                        self.error = 'lab error %d' % (payload[0] if payload else 255)
                        self.busy = False
                        self.phase = None
                        continue
                    if self.phase == 'read':
                        required = 3 if self.mode == 'adc' else 5
                        if len(payload) != required:
                            self.error = 'invalid lab value length'
                            self.busy = False
                        else:
                            self.value = payload[1] | (payload[2] << 8)
                            if self.mode == 'timer':
                                self.value |= payload[3] << 16 | payload[4] << 24
                            self.ready, self.busy = True, False
                        self.phase = None
                    elif self.phase == 'ack':
                        self.phase = 'await-ready'
                    elif self.phase in ('clear', 'identify'):
                        self.phase = None
            if self.phase == 'await-ready' and self.pending_seq is None and self.transport.ready():
                op = p.ADC_READ if self.mode == 'adc' else p.TIMER_READ
                self._send(op, b'', 'read')
        except Exception as exc:
            self.error = str(exc)[:80]
            self.busy = False
            self.phase = None
            self.pending_seq = None

    def status_word(self):
        return int(self.ready) | (int(self.busy) << 1) | (int(bool(self.error)) << 2) | (int(self.online) << 3)

    def state(self):
        return {'kind': 'simulation' if isinstance(self.transport, SimTransport) else
                ('hardware' if self.transport else 'disconnected'),
                'online': self.online, 'ready': self.ready, 'busy': self.busy,
                'error': self.error, 'value': self.value, 'mode': self.mode}

    def iot(self, ir, cpu):
        if ir == 0o6540:  # LABCLR
            self.clear()
        elif ir == 0o6541:  # LABGO, channel in AC[2:0]
            self.start(cpu.ac & 7)
        elif ir == 0o6543:  # LABTIM, start period capture on P2.1
            self.start(mode='timer')
        elif ir == 0o6542:  # LABRDY, skip
            if self.ready:
                cpu.pc = (cpu.pc + 1) & 0o7777
        elif ir == 0o6544:  # LABGET, OR into AC, like physical IOT
            if self.ready:
                cpu.ac |= self.value & 0o7777
                self.ready = False
            else:
                self.error = 'read before ready'
        elif ir == 0o6545:  # LABSTS, OR flags into AC
            cpu.ac |= self.status_word()
        elif ir == 0o6546:  # LABHI, bits 12..23 of 32-bit period
            if self.ready and self.mode == 'timer':
                cpu.ac |= (self.value >> 12) & 0o7777
            else:
                self.error = 'timer high word not ready'
        elif ir == 0o6547:  # LABTOP, bits 24..31 of 32-bit period
            if self.ready and self.mode == 'timer':
                cpu.ac |= (self.value >> 24) & 0o377
            else:
                self.error = 'timer top word not ready'
        else:
            raise ValueError('unimplemented ATLAS lab IOT %04o' % ir)

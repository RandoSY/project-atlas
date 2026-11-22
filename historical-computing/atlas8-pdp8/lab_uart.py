"""RP2040 UART0 transport to MSP430G2553 (separate from USB dashboard CDC).

No fake measurements. A missing controller leaves ATLAS IOTs offline.
"""
class PicoLabTransport:
    def __init__(self, baudrate=38400):
        from machine import UART, Pin
        import lab_protocol as p
        self.proto = p
        self.uart = UART(0, baudrate=baudrate, tx=Pin(0), rx=Pin(1), timeout=0)
        self.irq_pin = Pin(2, Pin.IN, Pin.PULL_DOWN)

    def send(self, seq, op, payload=b''):
        data = self.proto.frame(seq, op, payload)
        sent = self.uart.write(data)
        if sent != len(data):
            raise OSError('incomplete MSP430 UART write')

    def receive(self):
        waiting = self.uart.any()
        if not waiting:
            return []
        payload = self.uart.read(min(waiting, 64))
        return [payload] if payload else []

    def ready(self):
        return bool(self.irq_pin.value())

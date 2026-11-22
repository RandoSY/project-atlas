"""ATLAS-8 standalone programmable-calculator demonstration.
Works in desktop Python 3 or supported RP2040 MicroPython.
No browser, serial port or cross-compiler is required.
"""
from pdp8 import PDP8
from programs import load_calculator

def show(op, a, b):
    cpu = PDP8()
    load_calculator(cpu, op, a, b)
    cpu.run(20000)
    raw = cpu.peek(0o252)
    signed = raw if raw < 0o4000 else raw - 0o10000
    print("%s(%d, %d): signed=%d octal=%04o steps=%d reason=%s" %
          (op, a, b, signed, raw, cpu.instructions, cpu.reason))
    print(cpu.state())

show("add", 7, 6)
show("subtract", 6, 7)
show("multiply", 7, 6)

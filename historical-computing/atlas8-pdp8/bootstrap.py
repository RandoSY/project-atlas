"""Documented DEC PDP-8/I RIM loader and small RIM tape test generator.

The words below are transcribed from DEC PDP-8 Family Paper Tape System
User's Guide, DEC-08-NGCC-D, RIM-2, high-speed reader column.
No host-side interpreter is used to execute the RIM loader.
"""
RIM_ORIGIN = 0o7756
RIM_HIGH_SPEED = (
    0o6014, 0o6011, 0o5357, 0o6016, 0o7106, 0o7006,
    0o7510, 0o5374, 0o7006, 0o6011, 0o5367, 0o6016,
    0o7420, 0o3776, 0o3376, 0o5357, 0o0000
)


def install_rim(cpu):
    """Console deposit equivalent; historical lesson can toggle each word instead."""
    for index, word in enumerate(RIM_HIGH_SPEED):
        cpu.poke(RIM_ORIGIN + index, word, 0)
    cpu.pc = RIM_ORIGIN
    cpu.ifield = cpu.dfield = cpu.ibuffer = 0
    cpu.ac = cpu.l = 0
    cpu.halted = False
    cpu.reason = ''
    return len(RIM_HIGH_SPEED)


def rim_tape(pairs, leader=24, trailer=24):
    """Encode RIM address/value pairs as raw eight-channel tape frames.

    The high address frame uses channel 7 (0o100). 0o200 alone marks
    leader/trailer. Each 12-bit word occupies two six-bit frames.
    This is a fixture generator, not a cross-assembler.
    """
    out = bytearray([0o200] * leader)
    for address, word in pairs:
        if not (0 <= address <= 0o7777 and 0 <= word <= 0o7777):
            raise ValueError('RIM address and word must be 12 bits')
        out.extend((0o100 | (address >> 6), address & 0o77,
                    word >> 6, word & 0o77))
    out.extend([0o200] * trailer)
    return bytes(out)

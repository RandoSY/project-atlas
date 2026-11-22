"""In-memory, host-assisted readers for historical PDP-8 tape image bytes.

These loaders bypass a *physical* reader and deposit original PDP-8 machine
words into emulated core. They do not assemble or translate the program.

RIM is straightforward. BIN is best-effort and should be tested against each
historical image; original BIN variants and peripherals are not all supported.
"""

class TapeError(Exception):
    pass


def _pairs(data):
    """Yield paper-tape 12/13-bit words; high marker in first frame."""
    started = False
    pending = None
    for frame in data:
        if frame & 0o200:
            if started:
                break
            continue
        started = True
        if pending is None:
            pending = frame
        else:
            yield pending, frame, ((pending & 0o177) << 6) | (frame & 0o77)
            pending = None
    if pending is not None:
        raise TapeError('odd tape frame count')


def load_rim(cpu, filename, field=0):
    """Load RIM address/data pairs; return count. Use set pc manually."""
    with open(filename, 'rb') as fp:
        data = fp.read()
    addr = None
    count = 0
    for left, right, word in _pairs(data):
        if left & 0o100:
            addr = word & 0o7777
        else:
            if addr is None:
                raise TapeError('RIM data before address')
            cpu.poke(addr, word, field)
            addr = None
            count += 1
    if addr is not None:
        raise TapeError('RIM address without data')
    return count


def load_bin(cpu, filename, field=0, verify=False):
    """Load a typical BIN-format image, conservatively.

    The last word is treated as checksum, not core content. A *syntactic* image
    is decoded; for checksum validation enable verify. Behavior varies among
    historical BIN variants, so treat this as provisional until comparison to
    original DEC tapes and SIMH. No peripherals are emulated by this function.
    """
    with open(filename, 'rb') as fp:
        data = fp.read()
    addr = None
    count = 0
    current_field = field
    i = 0
    started = False
    pending = None
    words = []
    byte_sum = 0
    for raw in data:
        if raw == 0o200:
            if started:
                break
            continue
        if raw & 0o300 == 0o300:  # field designation
            current_field = (raw >> 3) & 7
            if current_field >= cpu.fields:
                raise TapeError('field %d not installed' % current_field)
            continue
        if raw & 0o200:
            if started:
                break
            continue
        started = True
        if pending is None:
            pending = raw
        else:
            left, right = pending, raw
            words.append((left, right, ((left & 0o177) << 6) | (right & 0o77), current_field))
            pending = None
    if pending is not None:
        raise TapeError('odd BIN frame count')
    if not words:
        return 0
    if len(words) < 2:
        raise TapeError('BIN has no payload and checksum')
    checksum = words[-1][2] & 0o7777
    for left, right, word, memfield in words[:-1]:
        byte_sum += (left & 0o177) + (right & 0o77)
        if left & 0o100:
            addr = word & 0o7777
        else:
            if addr is None:
                raise TapeError('BIN data before origin')
            cpu.poke(addr, word, memfield)
            addr = (addr + 1) & 0o7777
            count += 1
    if verify and (byte_sum & 0o7777) != checksum:
        raise TapeError('BIN checksum mismatch %04o != %04o' % (byte_sum & 0o7777, checksum))
    return count


def load_octal_text(cpu, filename, field=0):
    """Simple operator-supplied octal listing, never cross-assembled by tool.

    Each non-comment line: 0200 7300 [word2 word3 ...]
    """
    count = 0
    with open(filename, 'r') as fp:
        for line in fp:
            line = line.split('#', 1)[0].split('/', 1)[0].strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) < 2:
                raise TapeError('listing line needs address and word')
            address = int(parts[0], 8)
            for word in parts[1:]:
                cpu.poke(address, int(word, 8), field)
                address = (address + 1) & 0o7777
                count += 1
    return count


def save_core(cpu, filename):
    """Portable core snapshot in explicitly big-endian 12-bit word storage."""
    with open(filename, 'wb') as fp:
        fp.write(b'PDP8CORE1\n')
        fp.write(bytes([cpu.fields]))
        for word in cpu.memory:
            fp.write(bytes([word >> 8, word & 0xff]))


def restore_core(cpu, filename):
    with open(filename, 'rb') as fp:
        if fp.read(10) != b'PDP8CORE1\n':
            raise TapeError('wrong core image format')
        n = fp.read(1)
        if not n or n[0] != cpu.fields:
            raise TapeError('core image memory fields mismatch')
        data = fp.read()
    if len(data) != len(cpu.memory) * 2:
        raise TapeError('wrong core image size')
    for i in range(len(cpu.memory)):
        cpu.memory[i] = ((data[2*i] << 8) | data[2*i+1]) & 0o7777

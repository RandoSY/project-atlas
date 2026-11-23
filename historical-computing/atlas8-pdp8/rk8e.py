"""Incremental RK8-E/RK05 disk-controller model for ATLAS-8.

Host-side, instruction-level compatibility work. This is NOT an OS/8 boot
claim or cycle-accurate drive simulation. DEC RK8-E device 74 (octal),
IOTs 6741-6747. Mounted images use SIMH-style little-endian 16-bit
containers for 12-bit PDP-8 words, with cylinder/surface/sector order.

The image is file-backed: a full cartridge never occupies Pico RAM.
Only attach local, explicitly supplied image paths. Images are read-only
unless the operator deliberately chooses a writable working COPY.
"""
from array import array

WORD_MASK = 0o7777
CYLINDERS = 203
SURFACES = 2
SECTORS = 16
WORDS_PER_SECTOR = 256
SECTOR_BYTES = WORDS_PER_SECTOR * 2
IMAGE_BYTES = CYLINDERS * SURFACES * SECTORS * SECTOR_BYTES

# Bits in the DEC status register (DEC numbers bits 0..11 from MSB).
DONE = 0o4000
FILE_NOT_READY = 0o0200
CONTROL_BUSY = 0o0100
WRITE_LOCK = 0o0020
DRIVE_STATUS_ERROR = 0o0002
CYLINDER_ERROR = 0o0001


class RK05Image:
    """Seekable, low-memory, optionally writable image of one cartridge."""
    def __init__(self, path, read_only=True):
        self.path = path
        self.read_only = bool(read_only)
        self.file = open(path, 'rb' if self.read_only else 'r+b')
        self.file.seek(0, 2)
        size = self.file.tell()
        if size > IMAGE_BYTES or size & 1:
            self.close()
            raise ValueError('RK05 image length is invalid: %d bytes' % size)

    def close(self):
        if self.file is not None:
            self.file.close()
            self.file = None

    @staticmethod
    def offset(cylinder, surface, sector):
        if not (0 <= cylinder < CYLINDERS and
                0 <= surface < SURFACES and 0 <= sector < SECTORS):
            raise ValueError('RK05 cylinder/surface/sector out of range')
        block = ((cylinder * SURFACES + surface) * SECTORS + sector)
        return block * SECTOR_BYTES

    def read_sector(self, cylinder, surface, sector):
        self.file.seek(self.offset(cylinder, surface, sector))
        raw = self.file.read(SECTOR_BYTES)
        if len(raw) < SECTOR_BYTES:
            raw += b'\x00' * (SECTOR_BYTES - len(raw))
        return [raw[i] | ((raw[i + 1] & 0x0f) << 8)
                for i in range(0, SECTOR_BYTES, 2)]

    def write_sector(self, cylinder, surface, sector, words):
        if self.read_only:
            raise OSError('RK05 image is write protected')
        if len(words) != WORDS_PER_SECTOR:
            raise ValueError('RK05 sector needs exactly 256 words')
        raw = bytearray(SECTOR_BYTES)
        for i, word in enumerate(words):
            word &= WORD_MASK
            raw[2 * i] = word & 0xff
            raw[2 * i + 1] = (word >> 8) & 0x0f
        self.file.seek(self.offset(cylinder, surface, sector))
        self.file.write(raw)
        self.file.flush()


class RK8E:
    """Selected RK8-E IOTs, synchronous data-break approximation.

    I/O completes within DLAG for deterministic testability. This is a
    functional first increment; real rotational latency, CRC, drive
    maintenance instructions and command-overlap timing need later work.
    """
    def __init__(self):
        self.drives = [None, None, None, None]
        self.reset()

    def attach(self, unit, path, read_only=True):
        if type(unit) is not int or not 0 <= unit < 4:
            raise ValueError('RK8-E unit must be 0..3')
        new_drive = RK05Image(path, read_only=read_only)
        old = self.drives[unit]
        self.drives[unit] = new_drive
        if old is not None:
            old.close()

    def close(self):
        for i in range(4):
            drive = self.drives[i]
            if drive is not None:
                drive.close()
                self.drives[i] = None

    def reset(self):
        # Reset controller state, NOT installed cartridges.
        self.command = 0
        self.disk_address = 0
        self.current_address = 0
        self.status = 0
        self.error = False

    def state(self):
        return {'command': self.command, 'disk_address': self.disk_address,
                'current_address': self.current_address,
                'status': self.status, 'error': self.error, 'irq': self.irq,
                'mounted': [x is not None for x in self.drives],
                'read_only': [x.read_only if x is not None else None
                              for x in self.drives]}

    @property
    def irq(self):
        return bool((self.command & 0o0400) and
                    ((self.status & DONE) or self.error))

    def _finish(self, error=0):
        self.error = bool(error)
        self.status = DONE | error

    def _go(self, cpu):
        cmd = self.command
        operation = (cmd >> 9) & 7
        field = (cmd >> 3) & 7
        unit = (cmd >> 1) & 3
        nwords = 128 if cmd & 0o100 else 256
        cylinder = ((self.disk_address >> 5) & 0o177) | ((cmd & 1) << 7)
        surface = (self.disk_address >> 4) & 1
        sector = self.disk_address & 0o17
        drive = self.drives[unit]
        self.status = 0
        self.error = False

        if drive is None:
            self._finish(FILE_NOT_READY | DRIVE_STATUS_ERROR)
            return
        if cylinder >= CYLINDERS:
            self._finish(CYLINDER_ERROR)
            return
        if field >= cpu.fields:
            # Do not silently wrap a nonexistent memory field.
            self._finish(DRIVE_STATUS_ERROR)
            return
        if operation == 3:  # Seek only
            self._finish()
            return
        if operation == 2:  # Write protect selected drive
            drive.read_only = True
            self._finish()
            return
        if operation not in (0, 1, 4, 5):
            self._finish(DRIVE_STATUS_ERROR)
            return
        if operation in (4, 5) and drive.read_only:
            self._finish(WRITE_LOCK)
            return
        try:
            if operation in (0, 1):
                words = drive.read_sector(cylinder, surface, sector)
                for i in range(nwords):
                    cpu.poke((self.current_address + i) & WORD_MASK,
                             words[i], field)
            else:
                words = [cpu.peek((self.current_address + i) & WORD_MASK,
                                  field) for i in range(nwords)]
                if nwords == 128:
                    words.extend([0] * 128)
                drive.write_sector(cylinder, surface, sector, words)
            self.current_address = (self.current_address + nwords) & WORD_MASK
            self._finish()
        except OSError:
            self._finish(DRIVE_STATUS_ERROR)

    def iot(self, ir, cpu):
        """Execute selected real DEC IOTs, manipulating the guest AC/PC."""
        if ir == 0o6741:  # DSKP: skip on done or error
            if self.status & DONE or self.error:
                cpu.pc = (cpu.pc + 1) & WORD_MASK
        elif ir == 0o6742:  # DCLR: clear/reset per AC low two bits
            mode = cpu.ac & 3
            cpu.ac = 0
            if mode == 1:  # Clear entire controller
                self.reset()
            elif mode == 2:  # Recalibrate: zero cylinder, signal done
                self.disk_address &= 0o37
                self._finish()
            else:  # Clear status only
                self.status = 0
                self.error = False
        elif ir == 0o6743:  # DLAG: load disk address, start operation
            self.disk_address = cpu.ac & WORD_MASK
            cpu.ac = 0
            self._go(cpu)
        elif ir == 0o6744:  # DLCA: load current memory address
            self.current_address = cpu.ac & WORD_MASK
            cpu.ac = 0
        elif ir == 0o6745:  # DRST: read status (replace AC)
            cpu.ac = self.status & WORD_MASK
        elif ir == 0o6746:  # DLDC: load command, clear status
            self.command = cpu.ac & WORD_MASK
            cpu.ac = 0
            self.status = 0
            self.error = False
        elif ir == 0o6747:
            raise ValueError('RK8-E maintenance IOT DMAN not implemented')
        else:
            raise ValueError('RK8-E IOT %04o not implemented' % ir)

"""PDP-8/I-style machine core for MicroPython RP2040 and desktop CPython.

Original implementation, no third-party runtime dependencies. All instruction
words and register values use DEC octal conventions in the documentation.

Supported: 4K-32K 12-bit core, six MRI, autoindex, group-1/group-2 OPR,
PDP-8/E MQ basics, TTY IOT, memory extension, basic interrupts.
Not supported: EAE, user-mode protection, disk, DECtape, calibrated time.
"""
from array import array

WORD = 0o7777
FIELD_SIZE = 0o10000
FULL_LINK_AC = 0o17777


class PDP8Error(Exception):
    pass


class UnsupportedIOT(PDP8Error):
    pass


class UnsupportedEAE(PDP8Error):
    pass


class PDP8:
    def __init__(self, fields=1, output=None, strict=True):
        if fields < 1 or fields > 8:
            raise ValueError('fields must be from 1 to 8')
        self.fields = fields
        # Build in small chunks to avoid a giant temporary Python list on Pico.
        self.memory = array('H', [0] * 512)
        for _ in range(fields * (FIELD_SIZE // 512) - 1):
            self.memory.extend(array('H', [0] * 512))
        self.output = output
        self.strict = strict
        self.reset()

    def reset(self, clear_memory=False):
        if clear_memory:
            for i in range(len(self.memory)):
                self.memory[i] = 0
        self.ac = 0
        self.l = 0
        self.mq = 0
        self.pc = 0
        self.ifield = 0
        self.dfield = 0
        self.ibuffer = 0
        self.saved_fields = 0
        self.cif_pending = False
        self.ion = False
        self.ion_delay = 0
        self.tty_ie = False
        self.kbd_flag = False
        self.kbd_buf = 0
        self.kbd_queue = bytearray()
        self.tty_flag = False  # Reset state, per original terminal practice.
        self.tty_busy = 0
        self.tty_output = bytearray()
        self.switches = 0
        self.halted = False
        self.instructions = 0
        self.last_pc = 0
        self.last_ir = 0
        self.reason = ''
        self.breakpoints = set()
        self.last_iot = 0

    def _addr(self, field, offset):
        if field < 0 or field >= self.fields:
            raise PDP8Error('memory field %o not installed' % field)
        return field * FIELD_SIZE + (offset & WORD)

    def peek(self, offset, field=0):
        return self.memory[self._addr(field, offset)]

    def poke(self, offset, word, field=0):
        self.memory[self._addr(field, offset)] = word & WORD

    def load_words(self, origin, words, field=0):
        loc = origin
        for word in words:
            self.poke(loc, word, field)
            loc = (loc + 1) & WORD
        return loc

    def feed_keyboard(self, data):
        if isinstance(data, str):
            data = data.encode('ascii', 'replace')
        for b in data:
            self.kbd_queue.append(b & 0xff)
        self._kbd_update()

    def _kbd_update(self):
        if not self.kbd_flag and self.kbd_queue:
            self.kbd_buf = self.kbd_queue[0]
            del self.kbd_queue[0]
            self.kbd_flag = True

    def _tick(self):
        if self.tty_busy > 0:
            self.tty_busy -= 1
            if self.tty_busy == 0:
                self.tty_flag = True
        self._kbd_update()
        if self.ion_delay > 0:
            self.ion_delay -= 1

    def _interrupt_pending(self):
        return self.tty_ie and (self.kbd_flag or self.tty_flag)

    def _take_interrupt(self):
        # Store the return PC at 0000 of field 0, enter 0001 of field 0.
        self.saved_fields = ((self.ifield & 7) << 3) | (self.dfield & 7)
        self.memory[0] = self.pc
        self.pc = 1
        self.ifield = self.dfield = self.ibuffer = 0
        self.cif_pending = False
        self.ion = False

    def _ea(self, instruction, fetch_pc, opcode):
        page = (fetch_pc & 0o7600) if (instruction & 0o200) else 0
        offset = page | (instruction & 0o177)
        if not (instruction & 0o400):
            field = self.ifield  # Direct operands are in the instruction field.
            return self._addr(field, offset)
        pointer = self._addr(self.ifield, offset)
        ptr_value = self.memory[pointer]
        # Autoindex locations 0010-0017 exist ONLY in field 0.
        if pointer >= 0o10 and pointer <= 0o17:
            ptr_value = (ptr_value + 1) & WORD
            self.memory[pointer] = ptr_value
        field = self.ibuffer if opcode >= 4 else self.dfield
        return self._addr(field, ptr_value)

    def _opr(self, ir):
        if not (ir & 0o400):  # Group 1
            if ir & 0o200:
                self.ac = 0
            if ir & 0o100:
                self.l = 0
            if ir & 0o040:
                self.ac ^= WORD
            if ir & 0o020:
                self.l ^= 1
            if ir & 0o001:
                combined = ((self.l << 12) | self.ac) + 1
                self.l = (combined >> 12) & 1
                self.ac = combined & WORD
            rotate = (ir >> 1) & 7
            if rotate == 1:  # BSW, PDP-8/E
                self.ac = ((self.ac & 0o77) << 6) | ((self.ac >> 6) & 0o77)
            elif rotate in (2, 3, 4, 5):
                combined = (self.l << 12) | self.ac
                distance = 2 if rotate in (3, 5) else 1
                if rotate in (2, 3):
                    combined = ((combined << distance) | (combined >> (13 - distance))) & FULL_LINK_AC
                else:
                    combined = ((combined >> distance) | (combined << (13 - distance))) & FULL_LINK_AC
                self.ac = combined & WORD
                self.l = (combined >> 12) & 1
            elif rotate in (6, 7):
                if self.strict:
                    raise PDP8Error('undefined group-1 rotate %04o' % ir)
        elif not (ir & 1):  # Group 2
            cond = False
            tests = 0
            if ir & 0o100:  # SMA
                cond = cond or bool(self.ac & 0o4000)
                tests += 1
            if ir & 0o040:  # SZA
                cond = cond or self.ac == 0
                tests += 1
            if ir & 0o020:  # SNL
                cond = cond or bool(self.l)
                tests += 1
            if ir & 0o010:  # reversed-sense 'AND' group; SKP if none
                if tests == 0 or not cond:
                    self.pc = (self.pc + 1) & WORD
            elif cond:
                self.pc = (self.pc + 1) & WORD
            if ir & 0o200:  # CLA, follows test
                self.ac = 0
            if ir & 0o004:  # OSR
                self.ac |= self.switches
            if ir & 0o002:  # HLT
                self.halted = True
                self.reason = 'HLT'
        else:  # Group 3: standard MQ operations, no EAE
            if ir & 0o056:
                if self.strict:
                    raise UnsupportedEAE('EAE not installed: %04o' % ir)
            old_mq = self.mq
            if ir & 0o200:
                self.ac = 0
            if ir & 0o020:  # MQL
                self.mq = self.ac
                self.ac = 0
            if ir & 0o100:  # MQA
                self.ac |= old_mq

    def _type_char(self, code):
        value = code & 0xff
        self.tty_output.append(value)
        if self.output is not None:
            self.output(value)

    def _iot(self, ir):
        self.last_iot = ir
        if 0o6000 <= ir <= 0o6007:
            pulse = ir & 7
            if pulse == 0:  # SKON, skip if interrupts enabled, then disable
                if self.ion:
                    self.pc = (self.pc + 1) & WORD
                self.ion = False
            elif pulse == 1:  # ION, one-instruction defer
                self.ion = True
                self.ion_delay = 2
            elif pulse == 2:  # IOF
                self.ion = False
            elif pulse == 3:  # SRQ
                if self._interrupt_pending():
                    self.pc = (self.pc + 1) & WORD
            elif pulse == 7:  # CAF
                self.ac = 0
                self.l = 0
                self.ion = False
                self.tty_ie = False
                self.kbd_flag = False
                self.tty_flag = False
            elif self.strict:
                raise UnsupportedIOT('CPU IOT %04o not implemented' % ir)
            return
        if 0o6200 <= ir <= 0o6277:
            pulse = ir & 7
            field = (ir >> 3) & 7
            if pulse in (1, 2, 3):
                if field >= self.fields:
                    raise PDP8Error('IOT requests absent memory field %o' % field)
                if pulse & 1:
                    self.dfield = field
                if pulse & 2:
                    self.ibuffer = field
                    self.cif_pending = True
            elif pulse == 4:
                if field == 1:  # RDF
                    self.ac |= self.dfield << 3
                elif field == 2:  # RIF
                    self.ac |= self.ifield << 3
                elif field == 3:  # RIB
                    self.ac |= self.saved_fields
                elif field == 4:  # RMF
                    self.ibuffer = (self.saved_fields >> 3) & 7
                    self.dfield = self.saved_fields & 7
                    self.cif_pending = True
                elif self.strict:
                    raise UnsupportedIOT('memory IOT %04o not implemented' % ir)
            elif self.strict:
                raise UnsupportedIOT('memory IOT %04o not implemented' % ir)
            return
        if 0o6030 <= ir <= 0o6037:  # Console keyboard
            pulse = ir & 7
            if pulse == 0:  # KCF, PDP-8/E
                self.kbd_flag = False
            elif pulse == 1:  # KSF
                if self.kbd_flag:
                    self.pc = (self.pc + 1) & WORD
            elif pulse == 2:  # KCC
                self.kbd_flag = False
                self.ac = 0
            elif pulse == 4:  # KRS (OR transfer)
                self.ac |= self.kbd_buf
            elif pulse == 5:  # KIE, PDP-8/E
                self.tty_ie = bool(self.ac & 1)
            elif pulse == 6:  # KRB
                self.ac = self.kbd_buf
                self.kbd_flag = False
            elif self.strict:
                raise UnsupportedIOT('TTY keyboard IOT %04o' % ir)
            return
        if 0o6040 <= ir <= 0o6047:  # Teleprinter
            pulse = ir & 7
            if pulse == 0:  # TFL, PDP-8/E
                self.tty_flag = True
            elif pulse == 1:  # TSF
                if self.tty_flag:
                    self.pc = (self.pc + 1) & WORD
            elif pulse == 2:  # TCF
                self.tty_flag = False
            elif pulse == 4:  # TPC
                self._type_char(self.ac)
                self.tty_busy = 3
                self.tty_flag = False
            elif pulse == 5:  # TSK, PDP-8/E
                if self.tty_flag or self.kbd_flag:
                    self.pc = (self.pc + 1) & WORD
            elif pulse == 6:  # TLS
                self._type_char(self.ac)
                self.tty_busy = 3
                self.tty_flag = False
            elif self.strict:
                raise UnsupportedIOT('teleprinter IOT %04o' % ir)
            return
        if self.strict:
            raise UnsupportedIOT('unattached IOT %04o (device %02o)' % (ir, (ir >> 3) & 0o77))

    def step(self):
        if self.halted:
            return False
        if self.ion and self.ion_delay == 0 and not self.cif_pending and self._interrupt_pending():
            self._take_interrupt()
        self.last_pc = self.pc
        if (self.ifield, self.pc) in self.breakpoints:
            self.reason = 'BREAKPOINT'
            self.halted = True
            return False
        ir = self.peek(self.pc, self.ifield)
        self.last_ir = ir
        self.pc = (self.pc + 1) & WORD
        op = (ir >> 9) & 7
        try:
            if op <= 5:
                addr = self._ea(ir, self.last_pc, op)
                if op == 0:  # AND
                    self.ac &= self.memory[addr]
                elif op == 1:  # TAD with 13-bit carry through LINK
                    total = ((self.l << 12) | self.ac) + self.memory[addr]
                    self.l = (total >> 12) & 1
                    self.ac = total & WORD
                elif op == 2:  # ISZ
                    new_value = (self.memory[addr] + 1) & WORD
                    self.memory[addr] = new_value
                    if new_value == 0:
                        self.pc = (self.pc + 1) & WORD
                elif op == 3:  # DCA
                    self.memory[addr] = self.ac
                    self.ac = 0
                elif op == 4:  # JMS: store return address at subroutine address
                    self.memory[addr] = self.pc
                    self.pc = ((addr & WORD) + 1) & WORD
                    if self.cif_pending:
                        self.ifield = self.ibuffer
                        self.cif_pending = False
                else:  # JMP
                    self.pc = addr & WORD
                    if self.cif_pending:
                        self.ifield = self.ibuffer
                        self.cif_pending = False
            elif op == 6:
                self._iot(ir)
            else:
                self._opr(ir)
        except PDP8Error as exc:
            self.reason = str(exc)
            self.halted = True
            raise
        self.instructions += 1
        self._tick()
        return not self.halted

    def run(self, limit=10000, poll=None, poll_every=256):
        """Run for up to limit instructions. 0 is not unlimited: use batches."""
        executed = 0
        while not self.halted and executed < limit:
            self.step()
            executed += 1
            if poll is not None and executed % poll_every == 0:
                poll(self)
        if not self.halted and executed == limit:
            self.reason = 'BUDGET'
        return executed

    def state(self):
        return ('IF=%o DF=%o PC=%04o AC=%04o L=%o MQ=%04o '
                'ION=%d KBF=%d TPF=%d IR=%04o RUN=%s') % (
                self.ifield, self.dfield, self.pc, self.ac, self.l,
                self.mq, self.ion, self.kbd_flag, self.tty_flag,
                self.last_ir, not self.halted)

    def dump(self, start=0, count=16, field=0):
        lines = []
        for base in range(start, start + count, 8):
            values = []
            for offs in range(base, min(base + 8, start + count)):
                values.append('%04o' % self.peek(offs, field))
            lines.append('%o:%04o  %s' % (field, base & WORD, ' '.join(values)))
        return '\n'.join(lines)

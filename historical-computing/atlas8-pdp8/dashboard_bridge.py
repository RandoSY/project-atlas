"""Atlas PDP-8 dashboard bridge for MicroPython RP2040 USB CDC.

JSON-lines protocol, version 1. One request -> one response; no REPL prompt.
Run in bounded batches via TICK requests: the browser stays responsive and
its Run/Stop commands cannot be trapped behind an unbounded guest loop.

CPython compatible for desktop protocol tests. This module does not open a
network socket and does not evaluate commands or execute uploaded Python.
"""
try:
    import ujson as json
except ImportError:
    import json
import sys

from pdp8 import PDP8, PDP8Error, WORD
from programs import load_demo, PROGRAMS, load_calculator, CALC_RESULT, CALC_A, CALC_B
from bootstrap import install_rim, RIM_HIGH_SPEED, RIM_ORIGIN, rim_tape
from lab_device import LabPeripheral, SimTransport

VERSION = '0.7.0-lab-preview'
PROTOCOL = 'ATLAS-PDP8/1'


def _number(value, label='number', maximum=None):
    if type(value) is not int or value < 0 or (maximum is not None and value > maximum):
        raise ValueError('%s must be a nonnegative integer%s' % (
            label, ' <= %d' % maximum if maximum is not None else ''))
    return value


class Bridge:
    def __init__(self, fields=1, lab_transport=None):
        # Desktop explicitly uses a labeled simulation; Pico passes hardware UART.
        self.lab = LabPeripheral(lab_transport)
        self.cpu = PDP8(fields=fields, output=self.tty_char, lab=self.lab)
        self.tty_pending = bytearray()
        self.cursor = 0
        self.mb = 0
        self.panel_field = 0
        self.running = False
        self.calc_operation = None
        self.tape_upload = None
        self.tape_expected = 0

    def tty_char(self, code):
        # CR, LF and printable bytes retain their original values. JSON encoder
        # escapes controls; JS terminal performs CR/LF display normalization.
        if len(self.tty_pending) < 8192:
            self.tty_pending.append(code & 0x7f)

    def state(self):
        cpu = self.cpu
        return {
            'pc': cpu.pc, 'ac': cpu.ac, 'l': cpu.l, 'mq': cpu.mq,
            'ir': cpu.last_ir, 'last_pc': cpu.last_pc,
            'ifield': cpu.ifield, 'dfield': cpu.dfield, 'ibuffer': cpu.ibuffer,
            'switches': cpu.switches, 'ma': self.cursor, 'mb': self.mb,
            'panel_field': self.panel_field, 'panel_next_addr': self.cursor,
            'halted': cpu.halted, 'running': self.running and not cpu.halted,
            'reason': cpu.reason, 'instructions': cpu.instructions,
            'tape': cpu.reader_status(),
            'lab': self.lab.state(),
            'fields': cpu.fields, 'tty_kbd_ready': cpu.kbd_flag,
            'tty_print_ready': cpu.tty_flag, 'ion': cpu.ion,
            'breakpoints': [[f, a] for f, a in sorted(cpu.breakpoints)],
            'calculator': ({'operation': self.calc_operation, 'a': cpu.peek(CALC_A),
                            'b': cpu.peek(CALC_B), 'result': cpu.peek(CALC_RESULT),
                            'complete': cpu.halted and cpu.reason == 'HLT'}
                           if self.calc_operation else None),
        }

    def _execute_steps(self, count, collect_trace=False):
        cpu = self.cpu
        trace = []
        done = 0
        active_bp = (cpu.ifield, cpu.pc)
        # A Continue from a breakpoint executes the breakpointed word once.
        # Breakpoint is restored immediately after that first instruction.
        skip_break = active_bp in cpu.breakpoints and cpu.reason == 'BREAKPOINT'
        if skip_break:
            cpu.breakpoints.remove(active_bp)
        try:
            while done < count and not cpu.halted:
                if collect_trace and len(trace) < 64:
                    trace.append([cpu.ifield, cpu.pc, cpu.peek(cpu.pc, cpu.ifield)])
                cpu.step()
                done += 1
                if skip_break:
                    cpu.breakpoints.add(active_bp)
                    skip_break = False
        finally:
            if skip_break:
                cpu.breakpoints.add(active_bp)
        if cpu.halted:
            self.running = False
        return done, trace

    def _dispatch(self, op, args):
        cpu = self.cpu
        data = {}
        if op in ('hello', 'status'):
            data['protocol'] = PROTOCOL
            data['version'] = VERSION
            data['model'] = 'PDP-8 MicroPython alpha'
            data['features'] = ['cpu', 'tty', 'memory', 'octal-load', 'demos', 'breakpoints', 'calculator', 'pdp8i-panel', 'high-speed-paper-tape', 'native-rim-loader', 'reader-speed', 'reader-transport', 'lab-device-54', 'lab-adc10', 'lab-timer-capture']
            if op == 'hello':
                data['warning'] = 'Original FOCAL/OS8 unverified; high-speed reader works with RIM, no disk or LINC mode.'
        elif op == 'lab_identify':
            self.lab._send(1, b'', 'identify')
        elif op == 'lab_status':
            self.lab.service()
            data['lab'] = self.lab.state()
        elif op == 'lab_timer_start':
            if self.running:
                raise ValueError('STOP before starting a panel measurement')
            data['accepted'] = self.lab.start(mode='timer')
        elif op == 'lab_demo':
            if self.running:
                raise ValueError('STOP before loading laboratory demo')
            self.lab.clear()
            # Real PDP-8 IOT program, channel A0 => AC=0 before LABGO.
            mode = args.get('mode', 'adc')
            if mode not in ('adc', 'timer'):
                raise ValueError('lab demo mode must be adc or timer')
            words = [0o7200, 0o6541 if mode == 'adc' else 0o6543, 0o6542, 0o5202,
                     0o7200, 0o6544, 0o3210, 0o7402, 0]
            cpu.load_words(0o200, words)
            cpu.pc = 0o200
            cpu.ac = cpu.l = 0
            cpu.halted = False
            cpu.reason = ''
            self.calc_operation = None
            self.cursor = 0o200
            self.running = False
            data['listing'] = [[0o200+i, word] for i, word in enumerate(words)]
            data['result_address'] = 0o210
        elif op == 'tape_begin':
            if self.running:
                raise ValueError('STOP before mounting paper tape')
            size = _number(args.get('size'), 'tape size', 32768)
            if size < 1:
                raise ValueError('tape must not be empty')
            self.tape_expected = size
            self.tape_upload = bytearray()
            data['accepted'] = size
        elif op == 'tape_chunk':
            if self.tape_upload is None:
                raise ValueError('begin tape transfer first')
            chunk = args.get('bytes')
            if not isinstance(chunk, list) or not 1 <= len(chunk) <= 192:
                raise ValueError('tape chunk must have 1..192 bytes')
            if any(type(item) is not int or item < 0 or item > 255 for item in chunk):
                raise ValueError('tape bytes must be integers 0..255')
            if len(self.tape_upload) + len(chunk) > self.tape_expected:
                raise ValueError('tape transfer exceeds declared size')
            self.tape_upload.extend(chunk)
            data['received'] = len(self.tape_upload)
        elif op == 'tape_end':
            if self.tape_upload is None or len(self.tape_upload) != self.tape_expected:
                raise ValueError('incomplete paper tape transfer')
            cpu.mount_reader(self.tape_upload)
            self.tape_upload = None
            self.tape_expected = 0
            data['mounted'] = len(cpu.ptr_data)
        elif op == 'tape_speed':
            speed = args.get('speed')
            cpu.reader_speed(speed)
            data['speed'] = speed
        elif op == 'tape_transport':
            action = args.get('action')
            if action not in ('play', 'pause'):
                raise ValueError('tape transport must be play or pause')
            cpu.reader_pause(action == 'pause')
            data['transport'] = action
        elif op == 'tape_rewind':
            if self.running:
                raise ValueError('STOP before rewinding tape')
            cpu.rewind_reader()
        elif op == 'tape_unmount':
            if self.running:
                raise ValueError('STOP before removing tape')
            cpu.mount_reader(b'')
        elif op == 'tape_status':
            data['tape'] = self.state()['tape']
        elif op == 'rim_install':
            if self.running:
                raise ValueError('STOP before entering RIM loader')
            data['deposited'] = install_rim(cpu)
            data['origin'] = RIM_ORIGIN
            data['listing'] = [[RIM_ORIGIN+i, w] for i,w in enumerate(RIM_HIGH_SPEED)]
            self.cursor = RIM_ORIGIN
            self.panel_field = 0
            self.calc_operation = None
            self.running = False
        elif op == 'rim_fixture':
            if self.running:
                raise ValueError('STOP before mounting tape')
            # Original machine words on a synthetic tape. RIM must execute to
            # transfer them into core; this command never writes those words.
            example = [(0o0200, 0o7301), (0o0201, 0o7001),
                       (0o0202, 0o7001), (0o0203, 0o7402)]
            cpu.mount_reader(rim_tape(example))
            data['mounted'] = len(cpu.ptr_data)
            data['expected_memory'] = [[address,word] for address,word in example]
        elif op == 'calculator':
            operation = args.get('operation', 'add')
            a = _number(args.get('a'), 'calculator A', WORD)
            b = _number(args.get('b'), 'calculator B', WORD)
            words = load_calculator(cpu, operation, a, b)
            self.calc_operation = operation
            self.running = False
            self.cursor = 0o200
            self.panel_field = 0
            self.mb = words[0]
            self.tty_pending = bytearray()
            data['listing'] = [[0o200 + i, word] for i, word in enumerate(words)]
            data['data_addresses'] = [CALC_A, CALC_B, CALC_RESULT]
        elif op == 'demo':
            name = args.get('name', 'hello')
            if name not in PROGRAMS:
                raise ValueError('unknown demonstration')
            data['description'] = load_demo(cpu, name)
            self.calc_operation = None
            self.cursor = cpu.pc
            self.panel_field = 0
            self.mb = cpu.peek(cpu.pc)
            self.tty_pending = bytearray()
            self.running = False
        elif op == 'reset':
            self.calc_operation = None
            cpu.reset(clear_memory=args.get('clear', False) is True)
            self.cursor = 0
            self.mb = 0
            self.panel_field = 0
            self.running = False
            self.tty_pending = bytearray()
        elif op == 'switches':
            cpu.switches = _number(args.get('value'), 'switch value', WORD)
        elif op == 'panel_fields':
            # These correspond to the separate 3-bit field-selector switches.
            ifield = _number(args.get('ifield', cpu.ifield), 'instruction field', cpu.fields - 1)
            dfield = _number(args.get('dfield', cpu.dfield), 'data field', cpu.fields - 1)
            if self.running:
                raise ValueError('STOP before operating front-panel field switches')
            cpu.ifield = cpu.ibuffer = ifield
            cpu.dfield = dfield
            cpu.cif_pending = False
            self.panel_field = ifield
        elif op == 'panel_addr':
            # PDP-8/I LOAD ADD: load the address register and set the field
            # switches; no accumulator or link clearing takes place.
            if self.running:
                raise ValueError('STOP before LOAD ADD')
            address = _number(args.get('address'), 'address', WORD)
            ifield = _number(args.get('ifield', args.get('field', cpu.ifield)), 'instruction field', cpu.fields - 1)
            dfield = _number(args.get('dfield', cpu.dfield), 'data field', cpu.fields - 1)
            self.cursor = address
            self.panel_field = ifield
            cpu.pc = address
            cpu.ifield = ifield
            cpu.dfield = dfield
            cpu.ibuffer = ifield
            cpu.cif_pending = False
            self.mb = cpu.peek(address, ifield)
            cpu.halted = True
            cpu.reason = 'LOAD ADD'
            self.running = False
        elif op == 'pc':
            cpu.pc = _number(args.get('address'), 'PC', WORD)
            cpu.halted = False
            cpu.reason = ''
            self.running = False
        elif op == 'field':
            field = _number(args.get('value'), 'field', cpu.fields - 1)
            kind = args.get('which')
            if kind == 'if':
                cpu.ifield = cpu.ibuffer = field
                cpu.cif_pending = False
            elif kind == 'df':
                cpu.dfield = field
            else:
                raise ValueError('field must be if or df')
        elif op == 'examine':
            if args.get('panel', False) is True and self.running:
                raise ValueError('STOP before front-panel EXAM')
            address = _number(args.get('address', self.cursor), 'address', WORD)
            field = _number(args.get('field', self.panel_field), 'field', cpu.fields - 1)
            count = _number(args.get('count', 1), 'count', 128)
            if count < 1:
                raise ValueError('count must be >= 1')
            data['address'] = address
            data['field'] = field
            data['words'] = [cpu.peek((address + n) & WORD, field) for n in range(count)]
            self.cursor = (address + count) & WORD
            self.panel_field = field
            self.mb = data['words'][-1]
            if args.get('panel', False) is True:
                cpu.pc = self.cursor  # PDP-8/I address lamps advance after EXAM
        elif op == 'deposit':
            if args.get('panel', False) is True and self.running:
                raise ValueError('STOP before front-panel DEP')
            address = _number(args.get('address', self.cursor), 'address', WORD)
            field = _number(args.get('field', self.panel_field), 'field', cpu.fields - 1)
            value = _number(args.get('value', cpu.switches), 'word', WORD)
            cpu.poke(address, value, field)
            self.cursor = (address + 1) & WORD
            self.panel_field = field
            self.mb = value
            if args.get('panel', False) is True:
                cpu.pc = self.cursor  # next address after each toggle-in
            data['address'] = address
            data['field'] = field
            data['value'] = value
        elif op == 'load_words':
            origin = _number(args.get('origin'), 'origin', WORD)
            field = _number(args.get('field', 0), 'field', cpu.fields - 1)
            words = args.get('words')
            if not isinstance(words, list) or not 1 <= len(words) <= 64:
                raise ValueError('load_words requires 1-64 words')
            for i, value in enumerate(words):
                cpu.poke((origin + i) & WORD, _number(value, 'word', WORD), field)
            data['loaded'] = len(words)
            data['origin'] = origin
        elif op == 'keyboard':
            value = args.get('text', '')
            if not isinstance(value, str) or len(value) > 512:
                raise ValueError('keyboard text must be <= 512 characters')
            cpu.feed_keyboard(value)
            data['queued'] = len(value)
        elif op == 'breakpoint':
            addr = _number(args.get('address'), 'breakpoint address', WORD)
            field = _number(args.get('field', cpu.ifield), 'field', cpu.fields - 1)
            enable = args.get('enabled', True)
            key = (field, addr)
            if enable:
                cpu.breakpoints.add(key)
            else:
                cpu.breakpoints.discard(key)
        elif op == 'breakpoints_clear':
            cpu.breakpoints.clear()
        elif op == 'step':
            count = _number(args.get('count', 1), 'step count', 64)
            if count < 1:
                raise ValueError('step count must be >=1')
            cpu.halted = False
            cpu.reason = '' if cpu.reason != 'BREAKPOINT' else 'BREAKPOINT'
            self.running = False
            data['executed'], data['trace'] = self._execute_steps(count, True)
        elif op in ('panel_start', 'panel_continue'):
            # START is a fresh console start at the address in the switches:
            # clear AC and LINK, preserve manually deposited core memory.
            # CONT resumes from the halted PC without clearing computation.
            single = args.get('single_instruction', False)
            if type(single) is not bool:
                raise ValueError('single_instruction must be boolean')
            if self.running:
                raise ValueError('STOP before starting from the front panel')
            if op == 'panel_start':
                cpu.pc = cpu.switches
                cpu.ac = 0
                cpu.l = 0
                self.cursor = cpu.pc
                cpu.ifield = cpu.ibuffer
            cpu.halted = False
            if cpu.reason != 'BREAKPOINT':
                cpu.reason = ''
            self.calc_operation = None
            self.running = True
            if single:
                data['executed'], data['trace'] = self._execute_steps(1, True)
                self.running = False
                if not cpu.halted:
                    cpu.halted = True
                    cpu.reason = 'SINGLE INSTRUCTION'
        elif op in ('start', 'resume'):
            if 'address' in args:
                cpu.pc = _number(args['address'], 'start address', WORD)
            cpu.halted = False
            # Keep BREAKPOINT reason until first step to skip it once.
            if cpu.reason != 'BREAKPOINT':
                cpu.reason = ''
            self.running = True
        elif op == 'tick':
            count = _number(args.get('count', 512), 'instruction budget', 4096)
            if count < 1:
                raise ValueError('tick budget must be >= 1')
            if self.running and not cpu.halted:
                data['executed'], data['trace'] = self._execute_steps(count, False)
            else:
                data['executed'] = 0
            if not cpu.halted and self.running:
                cpu.reason = ''
        elif op == 'halt':
            self.running = False
            cpu.halted = True
            cpu.reason = 'OPERATOR STOP'
        else:
            raise ValueError('unknown dashboard command: %s' % op)
        return data

    def handle(self, message):
        ident = message.get('id') if isinstance(message, dict) else None
        try:
            if not isinstance(message, dict):
                raise ValueError('request must be JSON object')
            op = message.get('op')
            if not isinstance(op, str):
                raise ValueError('missing operation')
            args = message.get('args', {})
            if not isinstance(args, dict):
                raise ValueError('args must be object')
            self.lab.service()  # Also service hardware while the guest is STOPPED.
            data = self._dispatch(op, args)
            response = {'id': ident, 'ok': True, 'state': self.state(), 'data': data}
        except Exception as exc:
            self.running = False
            response = {'id': ident, 'ok': False, 'state': self.state(),
                        'error': '%s: %s' % (type(exc).__name__, exc)}
        if self.tty_pending:
            response['tty'] = ''.join(chr(c) for c in self.tty_pending)
            self.tty_pending = bytearray()
        return response


def serve(fields=1, lab_mode='off'):
    transport = None
    if lab_mode == 'uart':
        try:
            from lab_uart import PicoLabTransport
            transport = PicoLabTransport()
        except Exception as exc:
            # Keep PDP-8/Teletype/paper-tape working with MSP430 unplugged.
            sys.stderr.write('ATLAS LAB offline: %s\n' % exc)
    elif lab_mode == 'simulate':
        transport = SimTransport()
    bridge = Bridge(fields=fields, lab_transport=transport)
    # USB CDC is the MicroPython REPL UART. While this program is active it is
    # a dedicated JSON-line protocol. Ctrl-C interrupts to return to REPL.
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                continue
            if len(line) > 6000:
                sys.stdout.write(json.dumps({'id': None, 'ok': False,
                                              'error': 'request too long'}) + '\n')
                continue
            try:
                req = json.loads(line)
            except Exception:
                sys.stdout.write(json.dumps({'id': None, 'ok': False,
                                              'error': 'invalid JSON line'}) + '\n')
                continue
            sys.stdout.write(json.dumps(bridge.handle(req)) + '\n')
        except KeyboardInterrupt:
            # A raw Ctrl-C can break into the MicroPython REPL for service.
            break
        except Exception as exc:
            sys.stdout.write(json.dumps({'id': None, 'ok': False,
                                          'error': 'bridge: %s' % exc}) + '\n')


if __name__ == '__main__':
    serve(fields=1)

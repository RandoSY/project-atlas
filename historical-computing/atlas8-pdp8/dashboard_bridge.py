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

VERSION = '0.3.0-alpha'
PROTOCOL = 'ATLAS-PDP8/1'


def _number(value, label='number', maximum=None):
    if type(value) is not int or value < 0 or (maximum is not None and value > maximum):
        raise ValueError('%s must be a nonnegative integer%s' % (
            label, ' <= %d' % maximum if maximum is not None else ''))
    return value


class Bridge:
    def __init__(self, fields=1):
        self.cpu = PDP8(fields=fields, output=self.tty_char)
        self.tty_pending = bytearray()
        self.cursor = 0
        self.mb = 0
        self.panel_field = 0
        self.running = False
        self.calc_operation = None

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
            'panel_field': self.panel_field,
            'halted': cpu.halted, 'running': self.running and not cpu.halted,
            'reason': cpu.reason, 'instructions': cpu.instructions,
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
            data['features'] = ['cpu', 'tty', 'memory', 'octal-load', 'demos', 'breakpoints', 'calculator']
            if op == 'hello':
                data['warning'] = 'Not OS/8 or FOCAL validated; TTY only; no disk or LINC mode.'
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
        elif op == 'panel_addr':
            address = _number(args.get('address'), 'address', WORD)
            field = _number(args.get('field', cpu.ifield), 'field', cpu.fields - 1)
            self.cursor = address
            self.panel_field = field
            cpu.pc = address
            cpu.ifield = field
            cpu.ibuffer = field
            cpu.cif_pending = False
            cpu.halted = False
            cpu.reason = ''
            self.running = False
            self.mb = cpu.peek(address, field)
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
        elif op == 'deposit':
            address = _number(args.get('address', self.cursor), 'address', WORD)
            field = _number(args.get('field', self.panel_field), 'field', cpu.fields - 1)
            value = _number(args.get('value', cpu.switches), 'word', WORD)
            cpu.poke(address, value, field)
            self.cursor = (address + 1) & WORD
            self.panel_field = field
            self.mb = value
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


def serve(fields=1):
    bridge = Bridge(fields=fields)
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

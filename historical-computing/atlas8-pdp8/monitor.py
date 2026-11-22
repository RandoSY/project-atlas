"""Pico USB-serial operator monitor for MicroPython PDP-8 core.
All PDP-8 addresses and words are octal. Instruction budgets are decimal.
"""
import sys
from pdp8 import PDP8, PDP8Error
from programs import PROGRAMS, load_demo
from tape import load_rim, load_bin, load_octal_text, save_core, restore_core


def octal(s):
    return int(s, 8)


HELP = '''PDP-8 operator commands (addresses/data OCTAL):
  help                   Show this guide
  regs                   Display register state
  reset [clear]          Reset CPU; optionally erase core
  fields                 Show configured core size
  pc 0200                Set PC
  if 0 | df 0            Set instruction/data field (0..7)
  sr 1234                Set front-panel switch register
  peek 0200 [field]      Examine one word
  poke 0200 7300 [field] Deposit one word
  dump 0200 [count]      Memory dump in current IF
  demo add|hello|count   Load built-in machine-code example
  step [n]               Single-step n instructions (decimal)
  run [n]                Run n instructions (decimal; default 10000)
  live                   Keep running, polling USB keyboard if possible
  key TEXT               Queue ASCII keyboard input, adds CR
  break 0205             Add breakpoint in current instruction field
  unbreak                Clear all breakpoints
  load rim PATH [field]  Load PDP-8 native RIM paper tape
  load bin PATH [field]  Load PDP-8 BIN (provisional, unchecked)
  load oct PATH [field]  Load octal address/word listing
  save PATH              Snapshot emulated core memory
  restore PATH           Restore core snapshot
  quit                   Exit to MicroPython REPL
All work is native PDP-8 word code, running in MicroPython on RP2040.
Ctrl-C interrupts long runs; no host cross-compiler is used.
'''


class Monitor:
    def __init__(self, fields=1):
        self.cpu = PDP8(fields=fields, output=self.put_char)
        self.poller = None
        try:
            import select
            poller = select.poll()
            poller.register(sys.stdin, select.POLLIN)
            self.poller = poller
        except Exception:
            pass

    def put_char(self, value):
        code = value & 0x7f
        if code in (10, 13) or 32 <= code <= 126:
            sys.stdout.write(chr(code))

    def _poll_input(self, cpu):
        if self.poller is None:
            return
        try:
            if self.poller.poll(0):
                b = sys.stdin.read(1)
                if b:
                    cpu.feed_keyboard(b)
        except Exception:
            self.poller = None

    def execute(self, line):
        args = line.split()
        if not args:
            return True
        op = args[0].lower()
        cpu = self.cpu
        if op in ('help', '?'):
            print(HELP)
        elif op == 'regs':
            print(cpu.state())
        elif op == 'fields':
            print('%d words x 12 bits (%d memory fields)' % (len(cpu.memory), cpu.fields))
        elif op == 'reset':
            cpu.reset(clear_memory=('clear' in args[1:]))
            print(cpu.state())
        elif op == 'pc':
            cpu.pc = octal(args[1]) & 0o7777
            cpu.halted = False
            print(cpu.state())
        elif op == 'if':
            n = octal(args[1]); cpu._addr(n, 0)
            cpu.ifield = cpu.ibuffer = n
            print(cpu.state())
        elif op == 'df':
            n = octal(args[1]); cpu._addr(n, 0)
            cpu.dfield = n
            print(cpu.state())
        elif op == 'sr':
            cpu.switches = octal(args[1]) & 0o7777
            print(cpu.state())
        elif op == 'peek':
            addr = octal(args[1]); field = octal(args[2]) if len(args) > 2 else cpu.ifield
            print('%o:%04o %04o' % (field, addr, cpu.peek(addr, field)))
        elif op == 'poke':
            addr = octal(args[1]); word = octal(args[2]); field = octal(args[3]) if len(args) > 3 else cpu.ifield
            cpu.poke(addr, word, field)
            print('%o:%04o %04o' % (field, addr, cpu.peek(addr, field)))
        elif op == 'dump':
            addr = octal(args[1]) if len(args) > 1 else cpu.pc
            count = int(args[2]) if len(args) > 2 else 16
            print(cpu.dump(addr, min(count, 256), cpu.ifield))
        elif op == 'demo':
            name = args[1] if len(args) > 1 else 'hello'
            print(load_demo(cpu, name))
            print(cpu.state())
        elif op == 'step':
            count = int(args[1]) if len(args) > 1 else 1
            cpu.halted = False
            for _ in range(min(count, 1000)):
                if not cpu.step():
                    break
            print(cpu.state(), cpu.reason)
        elif op in ('run', 'live'):
            count = int(args[1]) if len(args) > 1 else 10000
            cpu.halted = False
            cpu.reason = ''
            try:
                if op == 'live':
                    while not cpu.halted:
                        cpu.run(1024, poll=self._poll_input)
                        self._poll_input(cpu)
                else:
                    cpu.run(count, poll=self._poll_input)
            except KeyboardInterrupt:
                cpu.reason = 'INTERRUPTED BY OPERATOR'
            print('\n' + cpu.state(), cpu.reason)
        elif op == 'key':
            payload = line.partition(' ')[2]
            cpu.feed_keyboard(payload + '\r')
            print('Queued %d characters' % (len(payload) + 1))
        elif op == 'break':
            cpu.breakpoints.add((cpu.ifield, octal(args[1]) & 0o7777))
            print('Breakpoint added')
        elif op == 'unbreak':
            cpu.breakpoints.clear()
            print('Breakpoints cleared')
        elif op == 'load':
            typ = args[1].lower()
            path = args[2]
            field = octal(args[3]) if len(args) > 3 else 0
            if typ == 'rim':
                count = load_rim(cpu, path, field)
            elif typ == 'bin':
                count = load_bin(cpu, path, field, verify=False)
            elif typ == 'oct':
                count = load_octal_text(cpu, path, field)
            else:
                raise ValueError('load types: rim, bin, oct')
            print('Loaded %d native PDP-8 words. Set pc to historical entry point.' % count)
        elif op == 'save':
            save_core(cpu, args[1]); print('Core saved')
        elif op == 'restore':
            restore_core(cpu, args[1]); print('Core restored (set PC as needed)')
        elif op in ('quit', 'exit'):
            return False
        else:
            print('Unknown command; enter help')
        return True

    def loop(self):
        print('\nSDL Atlas PDP-8 / MicroPython RP2040 | Type help')
        while True:
            try:
                line = input('pdp8> ').strip()
                if not self.execute(line):
                    break
            except KeyboardInterrupt:
                print('Interrupted. Type help.')
            except (Exception,) as exc:
                print('%s: %s' % (type(exc).__name__, exc))


def main(fields=1):
    Monitor(fields=fields).loop()

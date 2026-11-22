"""Run from project root: python -m unittest discover -s tests -v"""
import os
import tempfile
import unittest

from pdp8 import PDP8, PDP8Error, UnsupportedIOT, UnsupportedEAE
from programs import load_demo
from tape import load_rim, load_bin, load_octal_text, save_core, restore_core, TapeError


def encode_pair(word, address=False):
    high = (word >> 6) & 0o77
    if address:
        high |= 0o100
    return bytes([high, word & 0o77])


class CoreTests(unittest.TestCase):
    def setUp(self):
        self.cpu = PDP8()

    def execute(self, seq, pc=0o200):
        self.cpu.load_words(pc, seq)
        self.cpu.pc = pc
        self.cpu.run(100)

    def test_tad_add_and_halt(self):
        load_demo(self.cpu, 'add')
        self.cpu.run(100)
        self.assertTrue(self.cpu.halted)
        self.assertEqual(self.cpu.ac, 0o15)

    def test_native_hello_tty(self):
        load_demo(self.cpu, 'hello')
        self.cpu.run(1000)
        self.assertTrue(self.cpu.halted, self.cpu.state())
        self.assertEqual(bytes(self.cpu.tty_output), b'HELLO PDP-8\r\n')

    def test_isz_counter(self):
        load_demo(self.cpu, 'count')
        self.cpu.run(100)
        self.assertTrue(self.cpu.halted)
        self.assertEqual(self.cpu.peek(0o210), 0)

    def test_link_carry_toggles(self):
        self.cpu.poke(0o10, 1)
        self.execute([0o7200, 0o1010, 0o1010, 0o7402])
        self.assertEqual(self.cpu.ac, 2)
        self.assertEqual(self.cpu.l, 0)
        self.cpu.reset(clear_memory=True)
        self.cpu.poke(0o10, 1)
        self.cpu.ac = 0o7777
        self.execute([0o1010, 0o7402])
        self.assertEqual((self.cpu.ac, self.cpu.l), (0, 1))
        self.cpu.reset(clear_memory=True)
        self.cpu.poke(0o10, 1)
        self.cpu.ac = 0o7777
        self.cpu.l = 1
        self.execute([0o1010, 0o7402])
        self.assertEqual((self.cpu.ac, self.cpu.l), (0, 0))

    def test_indirect_autoindex(self):
        self.cpu.poke(0o10, 0o277)
        self.cpu.poke(0o300, 0o2222)
        self.execute([0o1410, 0o7402])
        self.assertEqual(self.cpu.ac, 0o2222)
        self.assertEqual(self.cpu.peek(0o10), 0o300)

    def test_and_dca(self):
        self.cpu.ac = 0o7777
        self.cpu.poke(0o10, 0o2525)
        self.execute([0o0010, 0o3211, 0o7402])
        self.assertEqual(self.cpu.peek(0o211), 0o2525)
        self.assertEqual(self.cpu.ac, 0)

    def test_jms_and_return_indirect(self):
        self.execute([0o4210, 0o7402] + [0]*6 + [0, 0o7001, 0o5610])
        self.assertEqual(self.cpu.peek(0o210), 0o201)
        self.assertEqual(self.cpu.ac, 1)
        self.assertTrue(self.cpu.halted)

    def test_page_end_uses_fetch_page(self):
        # At 0177, current-page reference 0200 offset 000 must be page zero.
        self.cpu.poke(0o0, 0o12)
        self.cpu.poke(0o200, 0o34)
        self.cpu.poke(0o177, 0o1200)
        self.cpu.pc = 0o177
        self.cpu.step()
        self.assertEqual(self.cpu.ac, 0o12)

    def test_opr_rotate_13bits(self):
        self.execute([0o7200, 0o7001, 0o7004, 0o7402])
        self.assertEqual((self.cpu.ac, self.cpu.l), (2, 0))
        self.cpu.reset(clear_memory=True)
        self.execute([0o7200, 0o7001, 0o7010, 0o7402])
        self.assertEqual((self.cpu.ac, self.cpu.l), (0, 1))

    def test_opr_microsequence(self):
        self.execute([0o7340, 0o7001, 0o7402])  # CLA CLL CMA, IAC
        self.assertEqual(self.cpu.ac, 0)
        self.assertEqual(self.cpu.l, 1)  # Carry across 12-bit AC into Link

    def test_group2_or_and_skip(self):
        # SZA skips when AC zero; invert (=SNA) does not skip on zero.
        self.execute([0o7200, 0o7440, 0o7001, 0o7402])
        self.assertEqual(self.cpu.ac, 0)
        self.cpu.reset(clear_memory=True)
        self.execute([0o7200, 0o7450, 0o7001, 0o7402])
        self.assertEqual(self.cpu.ac, 1)
        # SMA SZA OR: skip if negative OR zero.
        self.cpu.reset(clear_memory=True)
        self.cpu.ac = 0o4000
        self.execute([0o7540, 0o7001, 0o7402])
        self.assertEqual(self.cpu.ac, 0o4000)

    def test_osr(self):
        self.cpu.switches = 0o1234
        self.execute([0o7200, 0o7404, 0o7402])
        self.assertEqual(self.cpu.ac, 0o1234)

    def test_group3_mq(self):
        self.cpu.ac = 0o1234
        self.execute([0o7421, 0o7701, 0o7402])  # MQL then CLA MQA
        self.assertEqual(self.cpu.ac, 0o1234)
        self.assertEqual(self.cpu.mq, 0o1234)

    def test_group3_unsupported_eae(self):
        self.cpu.poke(0o200, 0o7403)
        self.cpu.pc = 0o200
        with self.assertRaises(UnsupportedEAE):
            self.cpu.step()

    def test_unknown_device_fails_loudly(self):
        self.cpu.poke(0o200, 0o6051)
        self.cpu.pc = 0o200
        with self.assertRaises(UnsupportedIOT):
            self.cpu.step()

    def test_keyboard(self):
        self.cpu.feed_keyboard('A')
        self.assertTrue(self.cpu.kbd_flag)
        self.execute([0o6031, 0o7402, 0o6036, 0o7402])
        self.assertEqual(self.cpu.ac, ord('A'))
        self.assertFalse(self.cpu.kbd_flag)

    def test_cif_cdf_indirect_data_and_jump(self):
        cpu = PDP8(fields=2)
        cpu.poke(0o200, 0o6211) # CDF to field 1
        cpu.poke(0o201, 0o6212) # CIF to field 1
        cpu.poke(0o202, 0o5205) # JMP direct 0205 commits field change
        cpu.poke(0o205, 0o7402, field=1)
        cpu.pc = 0o200
        cpu.run(8)
        self.assertEqual((cpu.ifield, cpu.dfield, cpu.pc), (1, 1, 0o206))
        self.assertTrue(cpu.halted)

    def test_indirect_uses_data_field(self):
        cpu = PDP8(fields=2)
        cpu.poke(0o20, 0o300)         # Pointer located field 0, not autoindex
        cpu.poke(0o300, 0o1, field=0)
        cpu.poke(0o300, 0o1234, field=1)
        cpu.dfield = 1
        cpu.load_words(0o200, [0o1420, 0o7402])
        cpu.pc = 0o200
        cpu.run(10)
        self.assertEqual(cpu.ac, 0o1234)

    def test_interrupt_vector(self):
        cpu = PDP8()
        cpu.load_words(0o200, [0o6035, 0o6001, 0o7000, 0o7000, 0o7402])
        cpu.poke(1, 0o7402)
        cpu.ac = 1  # KIE using bit 0
        cpu.feed_keyboard('x')
        cpu.pc = 0o200
        cpu.run(15)
        self.assertEqual(cpu.peek(0), 0o203)
        self.assertEqual(cpu.pc, 2)
        self.assertFalse(cpu.ion)

    def test_budget(self):
        self.cpu.poke(0o200, 0o5200)
        self.cpu.pc = 0o200
        self.assertEqual(self.cpu.run(13), 13)
        self.assertFalse(self.cpu.halted)
        self.assertEqual(self.cpu.reason, 'BUDGET')


class TapeTests(unittest.TestCase):
    def setUp(self):
        self.cpu = PDP8()
        self.dir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.dir.cleanup()

    def path(self, name):
        return os.path.join(self.dir.name, name)

    def test_rim(self):
        path = self.path('sample.rim')
        data = bytes([0o200, 0o200]) + encode_pair(0o200, True) + encode_pair(0o7200) + encode_pair(0o201, True) + encode_pair(0o7402) + bytes([0o200])
        with open(path, 'wb') as fp: fp.write(data)
        self.assertEqual(load_rim(self.cpu, path), 2)
        self.assertEqual(self.cpu.peek(0o201), 0o7402)

    def test_bin(self):
        path = self.path('sample.bin')
        words = encode_pair(0o200, True) + encode_pair(0o7200) + encode_pair(0o7402)
        chsum = sum(words) & 0o7777
        with open(path, 'wb') as fp: fp.write(bytes([0o200]) + words + encode_pair(chsum) + bytes([0o200]))
        self.assertEqual(load_bin(self.cpu, path, verify=True), 2)
        self.assertEqual(self.cpu.peek(0o200), 0o7200)

    def test_oct_listing_and_snapshot(self):
        path = self.path('oct.txt')
        with open(path, 'w') as fp: fp.write('0200 7200 7402  / stop\n')
        self.assertEqual(load_octal_text(self.cpu, path), 2)
        snap = self.path('snap.p8core')
        save_core(self.cpu, snap)
        self.cpu.poke(0o200, 0)
        restore_core(self.cpu, snap)
        self.assertEqual(self.cpu.peek(0o200), 0o7200)


if __name__ == '__main__':
    unittest.main()

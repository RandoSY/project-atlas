"""Deterministic tests of the clocked, byte-by-byte virtual paper reader.

No real sleeping or Pico assumed. The CPU's 601x IOTs still control every
frame in the original high-speed RIM loader.
"""
import unittest
from unittest.mock import patch

import pdp8
from dashboard_bridge import Bridge


class TapeTransportTests(unittest.TestCase):
    def setUp(self):
        self.clock = [1_000_000]
        self.clock_patch = patch.object(pdp8, '_now_us', lambda: self.clock[0])
        self.clock_patch.start()
        self.addCleanup(self.clock_patch.stop)
        self.bridge = Bridge()
        self.cpu = self.bridge.cpu
        self.identity = 0

    def advance(self, micros):
        self.clock[0] += micros
        self.cpu._tick()

    def cmd(self, op, **args):
        self.identity += 1
        reply = self.bridge.handle({'id': self.identity, 'op': op, 'args': args})
        self.assertTrue(reply['ok'], reply.get('error'))
        return reply

    def test_asr33_10_cps_without_shortcutting_iot(self):
        self.cpu.mount_reader(b'ABC')
        self.assertEqual(self.cpu.reader_status()['speed'], 'asr33')
        self.cpu._iot(0o6014)  # real RFC IOT
        self.advance(99_999)
        self.assertFalse(self.cpu.ptr_flag)
        self.assertEqual(self.cpu.ptr_pos, 0)
        self.advance(1)
        self.assertTrue(self.cpu.ptr_flag)
        self.assertEqual(self.cpu.ptr_buf, ord('A'))
        self.cpu.ac = 0
        self.cpu._iot(0o6016)  # RRB+RFC, do not skip next byte
        self.assertEqual(self.cpu.ac, ord('A'))
        self.advance(100_000)
        self.assertEqual(self.cpu.ptr_buf, ord('B'))
        state = self.cpu.reader_status()
        self.assertEqual((state['position'],state['delivered']), (2, 2))
        self.assertEqual(state['effective_cps'], 10.0)

    def test_high_speed_300_cps_nominal(self):
        self.cmd('tape_speed', speed='high')
        self.cpu.mount_reader(b'ABC')
        self.cpu._iot(0o6014)
        self.advance(3333)
        self.assertFalse(self.cpu.ptr_flag)
        self.advance(1)
        self.assertTrue(self.cpu.ptr_flag)
        self.cpu._iot(0o6016)
        self.advance(3334)
        self.assertEqual(self.cpu.ptr_buf, ord('B'))
        status = self.cpu.reader_status()
        self.assertEqual(status['nominal_cps'], 300)
        self.assertAlmostEqual(status['effective_cps'], 300, places=0)

    def test_turbo_completes_iot_handshake_without_delay(self):
        self.cmd('tape_speed', speed='turbo')
        self.cpu.mount_reader(b'abc')
        for c in b'abc':
            self.cpu._iot(0o6014)
            self.cpu._tick()
            self.assertTrue(self.cpu.ptr_flag)
            self.assertEqual(self.cpu.ptr_buf, c)
            self.cpu.ac = 0
            self.cpu._iot(0o6012)
            self.assertEqual(self.cpu.ac, c)
        self.assertEqual(self.cpu.ptr_pos, 3)
        self.assertTrue(self.cpu.reader_status()['eof'])
        self.assertEqual(self.cpu.reader_status()['nominal_cps'], None)

    def test_pause_preserves_pending_frame_then_play_restarts_clock(self):
        self.cpu.mount_reader(b'xy')
        self.cpu._iot(0o6014)
        self.advance(50_000)
        self.cmd('tape_transport', action='pause')
        self.advance(10_000_000)
        self.assertEqual(self.cpu.ptr_pos, 0)
        self.assertTrue(self.cpu.ptr_pending)
        self.cmd('tape_transport', action='play')
        self.advance(99_999)
        self.assertFalse(self.cpu.ptr_flag)
        self.advance(1)
        self.assertEqual(self.cpu.ptr_buf, ord('x'))

    def test_speed_change_reschedules_without_skipping_bytes(self):
        self.cpu.mount_reader(b'12')
        self.cpu._iot(0o6014)
        self.advance(40_000)
        self.cmd('tape_speed', speed='high')
        self.advance(3333)
        self.assertEqual(self.cpu.ptr_pos, 0)
        self.advance(1)
        self.assertEqual(self.cpu.ptr_buf, ord('1'))
        self.assertEqual(self.cpu.ptr_pos, 1)

    def test_rewind_clears_pending_and_restores_first_frame(self):
        self.cpu.mount_reader(b'12')
        self.cpu._iot(0o6014)
        self.advance(100_000)
        self.assertEqual(self.cpu.ptr_pos, 1)
        self.cmd('tape_rewind')
        self.assertEqual(self.cpu.ptr_pos, 0)
        self.assertFalse(self.cpu.ptr_flag)
        self.cpu._iot(0o6014)
        self.advance(100_000)
        self.assertEqual(self.cpu.ptr_buf, ord('1'))

    def test_invalid_rates_and_transport_actions_rejected(self):
        self.assertFalse(self.bridge.handle({'id': 1, 'op': 'tape_speed', 'args': {'speed': '999'}})['ok'])
        self.assertFalse(self.bridge.handle({'id': 2, 'op': 'tape_transport', 'args': {'action': 'fast-forward'}})['ok'])

    def test_rim_loader_executes_and_observes_10_cps(self):
        # Mount synthetic RIM bytes, install the *native* historical loader.
        self.cmd('rim_install')
        self.cmd('rim_fixture')
        self.cmd('switches', value=0o7756)
        self.cmd('panel_start', single_instruction=False)
        size = len(self.cpu.ptr_data)
        self.assertEqual(size, 64)
        # Each batch models 20 ms of elapsed reader time; the CPU is still
        # executing its normal 6011/6014/6016 polling loop.
        for _ in range(1500):
            self.clock[0] += 20_000
            self.cmd('tick', count=128)
            if self.cpu.ptr_pos == size:
                break
        self.assertEqual(self.cpu.ptr_pos, size)
        self.assertEqual([self.cpu.peek(0o200 + i) for i in range(4)],
                         [0o7301, 0o7001, 0o7001, 0o7402])
        self.assertGreater(self.cpu.instructions, 100)
        self.assertEqual(self.cpu.ptr_delivered, size)
        self.assertEqual(self.cpu.reader_status()['speed'], 'asr33')


if __name__ == '__main__':
    unittest.main()

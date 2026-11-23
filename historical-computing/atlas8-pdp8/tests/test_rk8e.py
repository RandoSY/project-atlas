"""RK8-E controller regression tests for ATLAS-8 (no archival disk needed)."""
import os
import tempfile
import unittest

from pdp8 import PDP8, UnsupportedIOT
from rk8e import (RK8E, RK05Image, DONE, WRITE_LOCK, FILE_NOT_READY,
                   DRIVE_STATUS_ERROR, CYLINDER_ERROR, SECTOR_BYTES)


def make_image(directory, name='work.rk05', words=None):
    path = os.path.join(directory, name)
    if words is None:
        words = [0] * 256
    data = bytearray(SECTOR_BYTES)
    for i, word in enumerate(words):
        data[2*i] = word & 255
        data[2*i+1] = (word >> 8) & 15
    with open(path, 'wb') as out:
        out.write(data)
    return path


def execute(cpu, ir, ac=0):
    # Exercise through the real PDP-8 instruction fetch and IOT decoder.
    address = cpu.pc
    cpu.poke(address, ir, cpu.ifield)
    cpu.ac = ac
    cpu.step()


class TestRK8E(unittest.TestCase):
    def test_geometry_and_read_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = make_image(tmp, words=[0o7777, 0o1234] + [0] * 254)
            drive = RK05Image(path)
            self.assertEqual(drive.read_sector(0, 0, 0)[:2],
                             [0o7777, 0o1234])
            self.assertEqual(drive.read_sector(0, 0, 1)[0], 0)
            self.assertEqual(RK05Image.offset(0, 0, 1), 512)
            self.assertEqual(RK05Image.offset(0, 1, 0), 16 * 512)
            self.assertEqual(RK05Image.offset(1, 0, 0), 32 * 512)
            with self.assertRaises(OSError):
                drive.write_sector(0, 0, 0, [0] * 256)
            with self.assertRaises(ValueError):
                RK05Image.offset(203, 0, 0)
            drive.close()

    def test_read_via_iot_into_field_and_address_wrap(self):
        with tempfile.TemporaryDirectory() as tmp:
            words = [i & 0o7777 for i in range(256)]
            image = make_image(tmp, words=words)
            controller = RK8E()
            controller.attach(0, image)
            cpu = PDP8(fields=8, rk8e=controller)
            execute(cpu, 0o6744, 0o7700)  # DLCA
            execute(cpu, 0o6746, 0o20)    # DLDC: field 2, read
            execute(cpu, 0o6743, 0)       # DLAG: cylinder 0 / side 0 / sector 0
            self.assertEqual(cpu.ac, 0)
            self.assertEqual(cpu.peek(0o7700, 2), 0)
            self.assertEqual(cpu.peek(0o7777, 2), 63)
            self.assertEqual(cpu.peek(0, 2), 64)
            self.assertEqual(cpu.peek(0o377, 2), 255)
            self.assertEqual(controller.current_address, 0o300)
            self.assertEqual(controller.status, DONE)
            self.assertEqual(cpu.peek(0o6000, 0), 0)
            execute(cpu, 0o6745, 0o7777)  # DRST clears AC and loads status
            self.assertEqual(cpu.ac, DONE)
            before = cpu.pc
            execute(cpu, 0o6741)           # DSKP
            self.assertEqual(cpu.pc, (before + 2) & 0o7777)
            controller.close()

    def test_half_sector_write_zero_fills_tail(self):
        with tempfile.TemporaryDirectory() as tmp:
            image = make_image(tmp)
            controller = RK8E()
            controller.attach(0, image, read_only=False)
            cpu = PDP8(fields=2, rk8e=controller)
            for n in range(128):
                cpu.poke(0o500 + n, n + 1, 1)
            execute(cpu, 0o6744, 0o500)
            # Function 4 (write), half block, extended memory field 1.
            execute(cpu, 0o6746, (4 << 9) | 0o100 | 0o10)
            execute(cpu, 0o6743, 0)
            words = controller.drives[0].read_sector(0, 0, 0)
            self.assertEqual(words[:128], list(range(1, 129)))
            self.assertEqual(words[128:], [0] * 128)
            self.assertEqual(controller.status, DONE)
            self.assertEqual(controller.current_address, 0o700)
            controller.close()

    def test_error_on_readonly_write_and_absent_drive(self):
        with tempfile.TemporaryDirectory() as tmp:
            controller = RK8E()
            controller.attach(0, make_image(tmp), read_only=True)
            cpu = PDP8(rk8e=controller)
            execute(cpu, 0o6746, 4 << 9)
            execute(cpu, 0o6743, 0)
            self.assertTrue(controller.status & WRITE_LOCK)
            self.assertTrue(controller.error)
            execute(cpu, 0o6746, 0o2)  # Select absent drive 1
            execute(cpu, 0o6743, 0)
            self.assertTrue(controller.status & FILE_NOT_READY)
            self.assertTrue(controller.status & DRIVE_STATUS_ERROR)
            controller.close()

    def test_invalid_cylinder_and_controller_reset(self):
        with tempfile.TemporaryDirectory() as tmp:
            controller = RK8E()
            controller.attach(0, make_image(tmp))
            cpu = PDP8(rk8e=controller)
            execute(cpu, 0o6746, 0o1)  # Extended cylinder bit
            execute(cpu, 0o6743, 0o4700)  # Cylinder above 202
            self.assertTrue(controller.status & CYLINDER_ERROR)
            cpu.reset()
            self.assertEqual(controller.status, 0)
            self.assertIsNotNone(controller.drives[0])
            controller.close()

    def test_irq_and_clear(self):
        with tempfile.TemporaryDirectory() as tmp:
            controller = RK8E()
            controller.attach(0, make_image(tmp))
            cpu = PDP8(rk8e=controller)
            execute(cpu, 0o6744, 0o200)
            execute(cpu, 0o6746, 0o400)  # Enable disk interrupt
            execute(cpu, 0o6743, 0)
            self.assertTrue(controller.irq)
            self.assertTrue(cpu._interrupt_pending())
            execute(cpu, 0o6742, 0)
            self.assertFalse(controller.irq)
            self.assertFalse(cpu._interrupt_pending())
            controller.close()

    def test_default_cpu_stays_unmodified(self):
        cpu = PDP8()
        cpu.poke(0, 0o6743)
        with self.assertRaises(UnsupportedIOT):
            cpu.step()


if __name__ == '__main__':
    unittest.main()

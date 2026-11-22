"""ATLAS laboratory I/O: protocol, device state machine, and native PDP-8 code."""
import unittest
from pdp8 import PDP8, UnsupportedIOT
from dashboard_bridge import Bridge
from lab_device import LabPeripheral, SimTransport
import lab_protocol as p


class WireTests(unittest.TestCase):
    def test_crc_known_vector(self):
        self.assertEqual(p.crc16(b'123456789'), 0x29b1)

    def test_fragmented_frame_and_resynchronization(self):
        decoder = p.Decoder()
        raw = p.frame(12, p.ADC_START, b'\x03')
        self.assertEqual(decoder.feed(raw[:2]), [])
        self.assertEqual(decoder.feed(raw[2:5]), [])
        self.assertEqual(decoder.feed(raw[5:]), [(12,p.ADC_START,b'\x03')])
        broken = bytearray(raw)
        broken[-1] ^= 1
        self.assertEqual(decoder.feed(broken), [])
        self.assertEqual(decoder.feed(b'garbage'+raw), [(12,p.ADC_START,b'\x03')])
        self.assertGreaterEqual(decoder.errors, 1)

    def test_bounded_validation(self):
        with self.assertRaises(ValueError):
            p.frame(0,p.STATUS,bytes(9))
        d = p.Decoder()
        self.assertEqual(d.feed(bytes((p.SYNC,1,1,1,9))), [])
        self.assertEqual(d.feed(p.frame(99,p.STATUS)), [(99,p.STATUS,b'')])


class LabIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.b = Bridge(lab_transport=SimTransport())
        self.seq = 0

    def request(self, op, **kw):
        self.seq += 1
        response=self.b.handle({'id':self.seq,'op':op,'args':kw})
        self.assertTrue(response['ok'],response.get('error'))
        return response

    def test_explicit_simulation_online_handshake(self):
        state=self.request('lab_status')['state']['lab']
        self.assertTrue(state['online'])
        self.assertEqual(state['kind'],'simulation')
        self.assertFalse(state['ready'])

    def test_adc_guest_iot_program(self):
        self.request('lab_demo',mode='adc')
        self.request('start',address=0o200)
        response=self.request('tick',count=100)
        self.assertTrue(response['state']['halted'])
        self.assertEqual(self.b.cpu.peek(0o210),512)
        self.assertEqual(self.b.cpu.last_ir,0o7402)
        self.assertEqual(response['state']['lab']['value'],512)

    def test_timer_guest_iot_program(self):
        self.request('lab_demo',mode='timer')
        self.request('start',address=0o200)
        response=self.request('tick',count=100)
        self.assertTrue(response['state']['halted'])
        self.assertEqual(self.b.cpu.peek(0o210),1000)
        self.assertEqual(response['state']['lab']['mode'],'timer')

    def test_absent_hardware_does_not_fabricate_data(self):
        cpu=PDP8()
        cpu.load_words(0o200,[0o6541,0o7402])
        cpu.pc=0o200
        with self.assertRaises(UnsupportedIOT):
            cpu.step()
        b=Bridge()
        state=b.handle({'id':1,'op':'lab_status','args':{}})['state']['lab']
        self.assertEqual(state['kind'],'disconnected')
        self.assertFalse(state['ready'])
        self.assertEqual(state['value'],0)

    def test_adc_channel_select_and_status_flags(self):
        self.request('load_words',origin=0o200,words=[0o7200,0o1010,0o6541,0o6542,0o5203,0o7200,0o6544,0o7402])
        self.b.cpu.poke(0o10,3)
        self.request('start',address=0o200)
        response=self.request('tick',count=200)
        self.assertTrue(response['state']['halted'])
        self.assertEqual(response['state']['ac'],515)
        self.assertEqual(self.b.lab.status_word()&2,0)

    def test_uart_pins_cannot_be_sampled_as_adc(self):
        for channel in (1,2):
            self.assertFalse(self.b.lab.start(channel))
            self.assertIn('reserved for UART',self.b.lab.error)
        self.assertFalse(self.b.lab.ready)

    def test_guest_timer_high_and_top_words(self):
        self.b.lab.value=0x12345678
        self.b.lab.ready=True
        self.b.lab.mode='timer'
        self.request('load_words',origin=0o200,words=[0o7200,0o6547,0o3220,
             0o7200,0o6546,0o3221,0o7200,0o6544,0o3222,0o7402,0,0,0])
        self.request('start',address=0o200)
        response=self.request('tick',count=100)
        self.assertTrue(response['state']['halted'])
        self.assertEqual((self.b.cpu.peek(0o220),self.b.cpu.peek(0o221),self.b.cpu.peek(0o222)),
                         (0x12,0x345,0x678))

    def test_labget_before_ready_does_not_invent_sample(self):
        self.request('load_words',origin=0o200,words=[0o6544,0o7402])
        self.request('start',address=0o200)
        response=self.request('tick',count=20)
        self.assertEqual(response['state']['ac'],0)
        self.assertIn('read before ready',response['state']['lab']['error'])

    def test_legacy_programs_do_not_regress(self):
        self.request('demo',name='hello')
        self.request('start',address=0o200)
        self.request('tick',count=4096)
        self.assertTrue(self.b.cpu.halted)
        self.assertIn(b'HELLO PDP-8',bytes(self.b.cpu.tty_output))

    def test_lab_status_flag_iot(self):
        self.request('load_words',origin=0o200,words=[0o7200,0o6545,0o7402])
        self.request('start',address=0o200)
        response=self.request('tick',count=20)
        self.assertEqual(response['state']['ac'] & 0o10,0o10)


if __name__ == '__main__': unittest.main()

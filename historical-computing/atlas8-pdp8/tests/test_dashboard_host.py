"""ATLAS-8 unified two-mode host: desktop behavior and safe switch failures."""
import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.request import Request, urlopen
from urllib.error import HTTPError

from pc_dashboard_server import SwitchableTransport, make_handler


class DashboardHostTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.transport = SwitchableTransport(fields=1, mode='sim')
        cls.srv = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(cls.transport))
        cls.thread = threading.Thread(target=cls.srv.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = 'http://127.0.0.1:%d' % cls.srv.server_port

    @classmethod
    def tearDownClass(cls):
        cls.srv.shutdown()
        cls.srv.server_close()
        cls.transport.close()
        cls.thread.join(timeout=2)

    def post(self, endpoint, payload):
        req = Request(self.url + endpoint, json.dumps(payload).encode('utf-8'),
                      headers={'Content-Type': 'application/json'}, method='POST')
        try:
            with urlopen(req, timeout=5) as resp:
                return resp.status, json.load(resp)
        except HTTPError as exc:
            return exc.code, json.load(exc)

    def test_static_dashboard_and_info(self):
        with urlopen(self.url+'/', timeout=5) as resp:
            content = resp.read().decode('utf-8')
            self.assertIn('executionMode', content)
            self.assertIn('Calculator', content)
        with urlopen(self.url+'/api/info', timeout=5) as resp:
            info = json.load(resp)
            self.assertEqual(info['mode'], 'sim')
            self.assertEqual(info['protocol'], 'ATLAS-PDP8/1')

    def test_calculator_and_mode_restart(self):
        self.post('/api/command', {'id':10,'op':'calculator','args':{'operation':'add','a':7,'b':6}})
        self.post('/api/command', {'id':11,'op':'start','args':{}})
        resp=None
        for i in range(10):
            _,resp=self.post('/api/command', {'id':20+i,'op':'tick','args':{'count':256}})
            if resp['state']['halted']: break
        self.assertEqual(resp['state']['ac'], 13)
        status,switched=self.post('/api/mode', {'mode':'sim'})
        self.assertEqual(status, 200)
        self.assertEqual(switched['mode'],'sim')
        _,hello=self.post('/api/command', {'id':40,'op':'hello','args':{}})
        self.assertEqual(hello['state']['instructions'],0)
        self.assertEqual(hello['state']['ac'],0)

    def test_failed_live_select_keeps_sim(self):
        status,error=self.post('/api/mode', {'mode':'serial','port':''})
        self.assertEqual(status,400)
        self.assertFalse(error['ok'])
        with urlopen(self.url+'/api/info',timeout=5) as resp:
            self.assertEqual(json.load(resp)['mode'],'sim')


if __name__=='__main__': unittest.main()

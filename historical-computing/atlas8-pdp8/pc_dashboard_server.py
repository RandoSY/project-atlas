"""Project Atlas PDP-8 dashboard host.

No web framework. Runs on the dedicated PC and serves the local dashboard.
  python pc_dashboard_server.py --mode sim
  python pc_dashboard_server.py --mode serial --port COM7

Only binds to 127.0.0.1; no remote access, code execution, or file upload.
Serial mode needs `pip install pyserial`; simulation needs only Python.
"""
import argparse
import json
import mimetypes
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from dashboard_bridge import Bridge, PROTOCOL

BASE = Path(__file__).resolve().parent
WEB = BASE / 'dashboard'
ALLOWED = {'/': 'index.html', '/index.html': 'index.html',
           '/app.js': 'app.js', '/style.css': 'style.css'}
MAX_REQUEST = 8192


class DesktopTransport:
    def __init__(self, fields):
        self.bridge = Bridge(fields=fields)
        self.lock = threading.Lock()

    def request(self, msg):
        with self.lock:
            return self.bridge.handle(msg)

    def close(self):
        pass


class PicoSerialTransport:
    def __init__(self, port, baud=115200):
        try:
            import serial
        except ImportError as exc:
            raise RuntimeError('Serial mode needs: python -m pip install pyserial') from exc
        self.ser = serial.Serial(port, baudrate=baud, timeout=0.3, write_timeout=3)
        self.lock = threading.Lock()
        self.port = port
        self.buffer = b''
        time.sleep(1.2)  # Allow board/USB CDC startup after opening port.
        self.ser.reset_input_buffer()

    def request(self, msg):
        line = json.dumps(msg, separators=(',', ':')).encode('utf-8') + b'\n'
        with self.lock:
            self.ser.write(line)
            self.ser.flush()
            deadline = time.monotonic() + 8.0
            while time.monotonic() < deadline:
                reply = self.ser.readline()
                if not reply:
                    continue
                try:
                    payload = json.loads(reply)
                except (ValueError, UnicodeDecodeError):
                    continue  # REPL startup banners and serial noise.
                if isinstance(payload, dict) and payload.get('id') == msg['id']:
                    return payload
        raise TimeoutError('Pico did not reply: check USB port, main.py and console ownership')

    def close(self):
        self.ser.close()


class SwitchableTransport:
    """One host service, two mutually exclusive PDP-8 execution targets.

    Selection never copies RAM between targets. Reopening SIM starts fresh.
    When switching to serial, acquire and validate the Pico before retiring
    the previous backend; a failed connection leaves SIM available.
    """
    def __init__(self, fields=1, mode='sim', port=None, baud=115200):
        self.lock = threading.RLock()
        self.fields = fields
        self.baud = baud
        self.port = port
        self.active = None
        self.mode = 'sim'
        if mode == 'serial':
            if not port:
                raise ValueError('A USB serial port is required for live Pico mode')
            self.active = PicoSerialTransport(port, baud)
            self.mode = 'serial'
        else:
            self.active = DesktopTransport(fields)

    def info(self):
        with self.lock:
            return {'mode': self.mode, 'protocol': PROTOCOL,
                    'port': self.port, 'host': 'dedicated PC',
                    'available_modes': ['sim', 'serial'],
                    'note': 'Targets have independent machine state; changing modes resets the selected session.'}

    def select(self, mode, port=None):
        if mode not in ('sim', 'serial'):
            raise ValueError('mode must be sim or serial')
        with self.lock:
            if mode == 'serial':
                target_port = port or self.port
                if not target_port or not isinstance(target_port, str):
                    raise ValueError('Enter Pico USB serial port (e.g. COM7 or /dev/ttyACM0)')
                if len(target_port) > 150:
                    raise ValueError('Serial port name too long')
                new = PicoSerialTransport(target_port, self.baud)
            else:
                new = DesktopTransport(self.fields)
                target_port = self.port
            old = self.active
            self.active = new
            self.mode = mode
            self.port = target_port
            if old is not None:
                old.close()
            return self.info()

    def request(self, msg):
        with self.lock:
            return self.active.request(msg)

    def close(self):
        with self.lock:
            if self.active is not None:
                self.active.close()
                self.active = None


def make_handler(transport, mode=None):
    class Handler(BaseHTTPRequestHandler):
        server_version = 'AtlasPDP8/0.5'

        def _write(self, status, body, mimetype='application/json; charset=utf-8'):
            self.send_response(status)
            self.send_header('Content-Type', mimetype)
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.send_header('X-Frame-Options', 'DENY')
            self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'")
            self.send_header('Content-Length', str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            path = self.path.split('?', 1)[0]
            if path == '/api/info':
                body = json.dumps(transport.info()).encode('utf-8')
                return self._write(200, body)
            if path not in ALLOWED:
                return self._write(404, b'{"error":"Not found"}')
            filename = WEB / ALLOWED[path]
            try:
                content = filename.read_bytes()
            except OSError:
                return self._write(500, b'{"error":"UI file missing"}')
            return self._write(200, content, mimetypes.guess_type(str(filename))[0] or 'application/octet-stream')

        def do_POST(self):
            if self.path not in ('/api/command', '/api/mode'):
                return self._write(404, b'{"error":"Not found"}')
            try:
                if self.headers.get('Content-Type', '').split(';')[0].strip().lower() != 'application/json':
                    raise ValueError('Content-Type must be application/json')
                size = int(self.headers.get('Content-Length', '0'))
                if not 1 <= size <= MAX_REQUEST:
                    raise ValueError('Request must be between 1 and 8192 bytes')
                message = json.loads(self.rfile.read(size))
                if not isinstance(message, dict):
                    raise ValueError('Request must be a JSON object')
                if self.path == '/api/mode':
                    info = transport.select(message.get('mode'), message.get('port'))
                    return self._write(200, json.dumps({'ok': True, **info}).encode('utf-8'))
                if type(message.get('id')) is not int:
                    raise ValueError('Command requires numeric request id')
                answer = transport.request(message)
                return self._write(200, json.dumps(answer).encode('utf-8'))
            except (ValueError, TimeoutError, OSError, RuntimeError) as exc:
                return self._write(400, json.dumps({'ok': False, 'error': str(exc)}).encode('utf-8'))
            except Exception as exc:
                return self._write(500, json.dumps({'ok': False, 'error': '%s: %s' % (type(exc).__name__, exc)}).encode('utf-8'))

        def log_message(self, fmt, *args):
            if self.path not in ('/api/command', '/api/mode'):
                super().log_message(fmt, *args)

    return Handler


def main(argv=None):
    ap = argparse.ArgumentParser(description='Project Atlas PDP-8 dashboard for dedicated PC')
    ap.add_argument('--mode', choices=('sim', 'serial'), default='sim')
    ap.add_argument('--port', help='USB serial port, e.g. COM7 or /dev/ttyACM0')
    ap.add_argument('--baud', type=int, default=115200)
    ap.add_argument('--fields', type=int, default=1, choices=range(1, 9))
    ap.add_argument('--http-port', type=int, default=8765)
    ap.add_argument('--open', action='store_true', help='Open default browser after starting')
    opts = ap.parse_args(argv)
    if opts.mode == 'serial' and not opts.port:
        ap.error('--port is required for serial mode')
    transport = SwitchableTransport(opts.fields, mode=opts.mode, port=opts.port, baud=opts.baud)
    server = ThreadingHTTPServer(('127.0.0.1', opts.http_port), make_handler(transport))
    url = 'http://127.0.0.1:%d/' % opts.http_port
    print('Project Atlas PDP-8 | mode: %s | %s' % (opts.mode.upper(), url), flush=True)
    if opts.mode == 'sim':
        print('SIMULATOR MODE — PC executes the same Python CPU; switch targets in dashboard.', flush=True)
    else:
        print('LIVE PICO — port %s. Do not use Thonny/mpremote on the same port.' % opts.port, flush=True)
    if opts.open:
        import webbrowser
        webbrowser.open(url)
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        transport.close()


if __name__ == '__main__':
    main()

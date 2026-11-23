"""Project Atlas PDP-8 dashboard host.

No web framework. Runs on the dedicated PC and serves the local dashboard.
  python pc_dashboard_server.py --mode sim
  python pc_dashboard_server.py --mode serial --port COM7

Only binds to 127.0.0.1; no remote access, code execution, or file upload.
Serial mode needs `pip install pyserial`; simulation needs only Python.
"""
import argparse
import errno
import json
import mimetypes
import os
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.request import urlopen

from dashboard_bridge import Bridge, PROTOCOL
from lab_device import SimTransport
from rk8e import RK8E

BASE = Path(__file__).resolve().parent
WEB = BASE / 'dashboard'
ALLOWED = {'/': 'index.html', '/index.html': 'index.html',
           '/app.js': 'app.js', '/style.css': 'style.css'}
MAX_REQUEST = 8192
APP_ID = 'ATLAS8-PDP8'
DEFAULT_HTTP_PORT = 8878   # Dedicated ATLAS-8 port; 8765 belongs to other Atlas tools.
FALLBACK_PORTS = 20       # If 8878 is occupied, find another free ATLAS-8 port.


class DesktopTransport:
    def __init__(self, fields, rk05_path=None, rk05_write=False):
        self.rk8e = None
        if rk05_path:
            self.rk8e = RK8E()
            self.rk8e.attach(0, rk05_path, read_only=not rk05_write)
        self.bridge = Bridge(fields=fields, lab_transport=SimTransport(), rk8e=self.rk8e)
        self.lock = threading.Lock()

    def request(self, msg):
        with self.lock:
            return self.bridge.handle(msg)

    def close(self):
        if self.rk8e is not None:
            self.rk8e.close()


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
    def __init__(self, fields=1, mode='sim', port=None, baud=115200,
                 rk05_path=None, rk05_write=False):
        self.lock = threading.RLock()
        self.fields = fields
        self.baud = baud
        self.port = port
        self.rk05_path = rk05_path
        self.rk05_write = rk05_write
        self.active = None
        self.mode = 'sim'
        if mode == 'serial':
            if not port:
                raise ValueError('A USB serial port is required for live Pico mode')
            self.active = PicoSerialTransport(port, baud)
            self.mode = 'serial'
        else:
            self.active = DesktopTransport(fields, rk05_path, rk05_write)

    def info(self):
        with self.lock:
            return {'mode': self.mode, 'protocol': PROTOCOL,
                    'port': self.port, 'host': 'dedicated PC', 'app_id': APP_ID,
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
                new = DesktopTransport(self.fields, self.rk05_path, self.rk05_write)
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
            self.send_header('X-Atlas8-Application', APP_ID)
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


def bind_dashboard_server(transport, port=None, fallback_ports=FALLBACK_PORTS, allow_fallback=False):
    """Bind ATLAS-8 safely: a conflicting service is NEVER opened as our UI.

    An explicit port is strict; the default has a small fallback range.
    Passing port=0 requests an OS-assigned port, useful for tests.
    """
    chosen = DEFAULT_HTTP_PORT if port is None else port
    if not 0 <= chosen <= 65535:
        raise ValueError('HTTP port must be 0..65535')
    strict = port is not None and not allow_fallback
    ports = [chosen] if strict else list(range(chosen, min(65536, chosen + fallback_ports + 1)))
    for candidate in ports:
        try:
            return ThreadingHTTPServer(('127.0.0.1', candidate), make_handler(transport))
        except OSError as exc:
            if exc.errno not in (errno.EADDRINUSE, 10048):
                raise
            if strict or candidate == ports[-1]:
                raise RuntimeError(
                    'ATLAS-8 HTTP port %s is already being used by another application. '
                    'Close that application or use --http-port with a free port.' % candidate
                ) from exc
    raise RuntimeError('No free localhost port available for ATLAS-8')


def verify_atlas8_server(url):
    """Require an ATLAS-8 identity response before launching a browser."""
    with urlopen(url + 'api/info', timeout=3) as reply:
        data = json.load(reply)
    if data.get('app_id') != APP_ID or data.get('protocol') != PROTOCOL:
        raise RuntimeError('The URL does not identify an ATLAS-8 server; browser not opened')
    return data


def open_dashboard_browser(url):
    import webbrowser
    # Prefer Chrome for the classroom dashboard, but keep Firefox usable.
    try:
        webbrowser.get('chrome').open(url)
    except webbrowser.Error:
        webbrowser.open(url)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Project Atlas PDP-8 dashboard for dedicated PC')
    ap.add_argument('--mode', choices=('sim', 'serial'), default='sim')
    ap.add_argument('--port', help='USB serial port, e.g. COM7 or /dev/ttyACM0')
    ap.add_argument('--baud', type=int, default=115200)
    ap.add_argument('--fields', type=int, default=1, choices=range(1, 9))
    ap.add_argument('--http-port', type=int, default=None, help='Override default port 8878 (disables automatic fallback)')
    ap.add_argument('--open', action='store_true', help='Open default browser after starting')
    ap.add_argument('--rk05', help='Attach an existing RK05/SIMH 12-bit disk image as drive 0 in PC SIM mode')
    ap.add_argument('--rk05-write', action='store_true', help='Allow writes to the RK05 WORKING COPY (not the historical master)')
    opts = ap.parse_args(argv)
    if opts.mode == 'serial' and not opts.port:
        ap.error('--port is required for serial mode')
    if opts.rk05_write and not opts.rk05:
        ap.error('--rk05-write requires --rk05 IMAGE')
    transport = SwitchableTransport(opts.fields, mode=opts.mode, port=opts.port,
                                    baud=opts.baud, rk05_path=opts.rk05,
                                    rk05_write=opts.rk05_write)
    server = None
    runner = None
    try:
        server = bind_dashboard_server(transport, port=opts.http_port)
        url = 'http://127.0.0.1:%d/' % server.server_port
        if opts.http_port is None and server.server_port != DEFAULT_HTTP_PORT:
            print('Port %d is busy; ATLAS-8 selected port %d instead.' %
                  (DEFAULT_HTTP_PORT, server.server_port), flush=True)
        print('Project Atlas PDP-8 | mode: %s | %s' % (opts.mode.upper(), url), flush=True)
        if opts.mode == 'sim':
            print('SIMULATOR MODE — PC executes the same Python CPU; switch targets in dashboard.', flush=True)
        else:
            print('LIVE PICO — port %s. Do not use Thonny/mpremote on the same port.' % opts.port, flush=True)
        if opts.open:
            # Start serving before checking identity. Never open a stale URL or
            # another application merely because its localhost port is in use.
            runner = threading.Thread(target=server.serve_forever,
                                      kwargs={'poll_interval': 0.2}, daemon=True)
            runner.start()
            verify_atlas8_server(url)
            open_dashboard_browser(url)
            runner.join()
        else:
            server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        pass
    finally:
        if server is not None:
            if runner is not None and runner.is_alive():
                server.shutdown()
                runner.join(timeout=3)
            server.server_close()
        transport.close()


if __name__ == '__main__':
    main()

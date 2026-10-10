#!/usr/bin/env python3
"""Мини-сервер для фронтенда MeDoc (только стандартная библиотека Python).

1) раздаёт статические файлы этой папки;
2) все запросы /api/... пересылает на бэкенд (убирая префикс /api).
Так браузер видит один адрес, и CORS-настройки в бэкенде не нужны.

Запуск:  python3 serve.py            (бэкенд ищется на http://127.0.0.5:8005)
         python3 serve.py --backend http://127.0.0.1:8000 --port 5173
"""
import argparse
import http.client
import mimetypes
import os
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.abspath(__file__))
HOP = {"connection", "keep-alive", "transfer-encoding", "te", "upgrade",
       "proxy-authenticate", "proxy-authorization", "trailers", "content-length", "host"}


class Handler(BaseHTTPRequestHandler):
    backend = None  # (host, port)
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        sys.stderr.write("  %s %s\n" % (self.command, self.path))

    def _send(self, code, body=b"", headers=()):
        self.send_response(code)
        for k, v in headers:
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    def _proxy(self):
        host, port = self.backend
        length = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(length) if length else None
        headers = {k: v for k, v in self.headers.items() if k.lower() not in HOP}
        headers["Host"] = f"{host}:{port}"
        try:
            conn = http.client.HTTPConnection(host, port, timeout=30)
            conn.request(self.command, self.path[4:] or "/", body, headers)
            resp = conn.getresponse()
            data = resp.read()
        except OSError as e:
            msg = ('{"detail":"Бэкенд недоступен (%s:%s). Запустите его и обновите страницу."}' % (host, port)).encode()
            return self._send(502, msg, [("Content-Type", "application/json; charset=utf-8")])
        out = [(k, v) for k, v in resp.getheaders() if k.lower() not in HOP]
        self.send_response(resp.status)
        for k, v in out:
            self.send_header(k, v)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(data)
        conn.close()

    def _static(self):
        path = urlsplit(self.path).path
        if path == "/":
            path = "/index.html"
        full = os.path.normpath(os.path.join(ROOT, path.lstrip("/")))
        if not full.startswith(ROOT) or not os.path.isfile(full):
            full = os.path.join(ROOT, "index.html")  # SPA-fallback
        with open(full, "rb") as f:
            data = f.read()
        ctype = mimetypes.guess_type(full)[0] or "application/octet-stream"
        if ctype.startswith("text/") or ctype in ("application/javascript", "application/json"):
            ctype += "; charset=utf-8"
        self._send(200, data, [("Content-Type", ctype), ("Cache-Control", "no-cache")])

    def do_GET(self):
        self._proxy() if self.path.startswith("/api/") else self._static()

    do_HEAD = do_GET
    do_POST = do_PUT = do_PATCH = do_DELETE = lambda self: (
        self._proxy() if self.path.startswith("/api/") else self._send(405))


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--backend", default=os.environ.get("MEDOC_BACKEND", "http://127.0.0.5:8005"))
    p.add_argument("--port", type=int, default=5173)
    p.add_argument("--host", default="127.0.0.1")
    a = p.parse_args()
    u = urlsplit(a.backend)
    Handler.backend = (u.hostname, u.port or 80)
    srv = ThreadingHTTPServer((a.host, a.port), Handler)
    print(f"MeDoc фронтенд:  http://{a.host}:{a.port}\nБэкенд:          {a.backend}\nОстановить: Ctrl+C")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nОстановлено")


if __name__ == "__main__":
    main()

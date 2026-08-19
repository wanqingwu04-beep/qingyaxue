# -*- coding: utf-8 -*-
"""青崖雪 手机阅读服务。

同一 Wi-Fi 下，手机浏览器打开本机地址即可阅读。
每次发布新章节后，页面会自动检测到新章节，无需重新传文件。

启动：双击 启动手机阅读器.bat
停止：在黑色窗口里按 Ctrl+C
"""

import json
import pathlib
import re
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

ROOT = pathlib.Path(__file__).resolve().parent.parent  # F:\Codex\青崖雪
READER = ROOT / "reader"
CH_DIR = ROOT / "chapters"
EPUB = ROOT / "青崖雪.epub"
PORT = 8765


def chapter_list():
    items = []
    for p in sorted(CH_DIR.glob("ch*.html")):
        text = p.read_text(encoding="utf-8")
        m = re.search(r"<h1>(.*?)</h1>", text, re.S)
        title = m.group(1).strip() if m else p.stem
        body = re.sub(r"<[^>]+>", "", text)
        chars = len(re.sub(r"\s", "", body))
        items.append({"file": p.name, "title": title, "chars": chars})
    return items


def chapter_paragraphs(fname):
    p = CH_DIR / fname
    if not p.exists():
        return None
    text = p.read_text(encoding="utf-8")
    m = re.search(r"<h1>(.*?)</h1>", text, re.S)
    title = m.group(1).strip() if m else p.stem
    paras = re.findall(r"<p>(.*?)</p>", text, re.S)
    paras = [re.sub(r"<[^>]+>", "", x).strip() for x in paras]
    return {"file": fname, "title": title, "paragraphs": paras}


class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        print("[%s] %s" % (self.address_string(), fmt % args))

    def _send(self, code, body, ctype="text/html; charset=utf-8"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        u = urlparse(self.path)
        path = u.path
        if path in ("/", "/index.html"):
            self._send(200, (READER / "index.html").read_bytes())
        elif path == "/api/chapters":
            body = json.dumps(chapter_list(), ensure_ascii=False).encode("utf-8")
            self._send(200, body, "application/json; charset=utf-8")
        elif path == "/api/chapter":
            q = parse_qs(u.query)
            fname = q.get("file", [""])[0]
            data = chapter_paragraphs(fname)
            if not data:
                self._send(404, b'{"error":"not found"}',
                           "application/json; charset=utf-8")
            else:
                body = json.dumps(data, ensure_ascii=False).encode("utf-8")
                self._send(200, body, "application/json; charset=utf-8")
        elif path == "/epub":
            if EPUB.exists():
                self._send(200, EPUB.read_bytes(), "application/epub+zip")
            else:
                self._send(404, b"epub not found")
        else:
            self._send(404, b"not found")


def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def main():
    ip = lan_ip()
    print("=" * 52)
    print("青崖雪 手机阅读服务已启动")
    print("本机地址: http://%s:%d" % (ip, PORT))
    print("手机（同一Wi-Fi）浏览器打开上面地址即可阅读")
    print("新章节发布后，页面会自动检测，点一下即可刷新")
    print("按 Ctrl+C 停止服务")
    print("=" * 52)
    srv = ThreadingHTTPServer(("0.0.0.0", PORT), Handler)
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n服务已停止")
        srv.server_close()


if __name__ == "__main__":
    main()

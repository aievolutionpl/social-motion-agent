"""Serve one review and its ratings on loopback, with seekable MP4 responses."""
import json
import re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit

import studio_core as core
import style_feedback


def make_server(folder, key, port=0):
    directory, manifest = style_feedback.collection(folder, key)
    videos = {"/" + v["file"]: v["file"] for v in manifest["variants"]}

    class Review(BaseHTTPRequestHandler):
        def send_json(self, status, data, head=False):
            body = json.dumps(data, ensure_ascii=False).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            if not head:
                self.wfile.write(body)

        def local_host(self):
            port = self.server.server_port
            return self.headers.get("Host", "") in (f"localhost:{port}", f"127.0.0.1:{port}")

        def do_POST(self):
            origin = self.headers.get("Origin")
            if not self.local_host() or (origin and origin != "http://" + self.headers["Host"]):
                return self.send_json(403, {"error": "Local review only"})
            if self.path != "/feedback":
                return self.send_error(404)
            if self.headers.get_content_type() != "application/json":
                return self.send_error(415)
            try:
                size = int(self.headers.get("Content-Length", "0"))
                if not 0 < size <= 32000:
                    return self.send_error(413)
                body = json.loads(self.rfile.read(size))
                if not isinstance(body, dict):
                    raise ValueError("Expected an object")
                result = style_feedback.save(folder, key, body["ratings"], "html")
            except (ValueError, KeyError, TypeError, OSError) as error:
                return self.send_json(400, {"error": str(error)})
            self.send_json(200, result)

        def do_HEAD(self):
            self.serve(True)

        def do_GET(self):
            self.serve(False)

        def serve(self, head):
            if not self.local_host():
                return self.send_error(403)
            path = urlsplit(self.path).path
            if path == "/feedback":
                return self.send_json(200, {"gallery": key, "ratings": style_feedback.current(folder, manifest)}, head)
            if path in ("/", "/index.html"):
                name, mime = "index.html", "text/html; charset=utf-8"
            elif path in videos:
                name, mime = videos[path], "video/mp4"
            else:
                return self.send_error(404)
            source = core.local(directory, name)
            size = source.stat().st_size
            start, end = 0, size - 1
            requested = self.headers.get("Range")
            if requested:
                match = re.fullmatch(r"bytes=(\d*)-(\d*)", requested)
                if not match or not any(match.groups()):
                    return self.send_error(416)
                left, right = match.groups()
                if left:
                    start = int(left)
                    end = min(end, int(right)) if right else end
                else:
                    start = max(0, size - int(right))
                if not 0 <= start <= end < size:
                    self.send_response(416)
                    self.send_header("Content-Range", f"bytes */{size}")
                    self.end_headers()
                    return
            self.send_response(206 if requested else 200)
            self.send_header("Content-Type", mime)
            self.send_header("X-Content-Type-Options", "nosniff")
            self.send_header("Accept-Ranges", "bytes")
            if requested:
                self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
            remaining = end - start + 1
            self.send_header("Content-Length", str(remaining))
            self.end_headers()
            if not head:
                with source.open("rb") as stream:
                    stream.seek(start)
                    while remaining:
                        chunk = stream.read(min(remaining, 128 * 1024))
                        if not chunk:
                            break
                        try:
                            self.wfile.write(chunk)
                        except (BrokenPipeError, ConnectionResetError):
                            break
                        remaining -= len(chunk)
    return ThreadingHTTPServer(("127.0.0.1", port), Review)


def run(folder, key, port):
    with make_server(folder, key, port) as server:
        print(f"http://127.0.0.1:{server.server_port}/", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            pass

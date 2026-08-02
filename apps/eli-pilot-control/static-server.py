#!/usr/bin/env python3
"""A tiny static file server for the pilot control panel.

This is intentionally simple and placeholder-only. It is suitable for local previewing
of the static deployment scaffold without introducing extra dependencies.
"""

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import os


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=os.path.dirname(__file__), **kwargs)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8080"))
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Serving pilot control panel on http://0.0.0.0:{port}")
    server.serve_forever()

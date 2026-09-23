#!/usr/bin/env python3
"""Serve the FPS demo on this computer without cloud hosting or extra packages."""

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import sys


DEMO_DIRECTORY = Path(__file__).resolve().parent
HOST = "127.0.0.1"


def port_number(value):
    try:
        port = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("Port must be a number.") from error
    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError("Port must be between 1 and 65535.")
    return port


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=port_number, default=8080,
                        help="Local port (default: 8080).")
    args = parser.parse_args()

    required = ("index.html", "style.css", "app.js", "engine.js", "scene.js",
                "vendor/three.js")
    missing = [name for name in required if not (DEMO_DIRECTORY / name).is_file()]
    if missing:
        print("Missing demo files: " + ", ".join(missing), file=sys.stderr)
        print("Keep the complete prototype folder together.", file=sys.stderr)
        return 1

    handler = partial(SimpleHTTPRequestHandler, directory=str(DEMO_DIRECTORY))
    try:
        server = ThreadingHTTPServer((HOST, args.port), handler)
    except OSError as error:
        print(f"Could not start http://{HOST}:{args.port}: {error}", file=sys.stderr)
        print("If the port is occupied, stop the other server or choose --port 8081.",
              file=sys.stderr)
        return 1

    with server:
        print("Adaptive Normandy Battlefield Simulation", flush=True)
        print(f"Open: http://{HOST}:{args.port}", flush=True)
        print("This address works on this computer only.", flush=True)
        print("Reviewers need a copy of this folder and must run this script locally.",
              flush=True)
        print("Keep this terminal open. Press Ctrl+C to stop.", flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print("\nDemo server stopped.", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

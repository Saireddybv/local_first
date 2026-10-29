import argparse
import socket
import threading
import webbrowser
import uvicorn
from .server import create_app

def main():
    parser = argparse.ArgumentParser(description="Local First: Files, Audio and Clip")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--folder", help="Folder shared with approved devices")
    parser.add_argument("--address", help="Laptop LAN IP to put in the QR code")
    parser.add_argument("--cert", help="Trusted TLS certificate PEM (for phone camera/microphone)")
    parser.add_argument("--key", help="TLS private key PEM")
    args = parser.parse_args()
    if bool(args.cert) != bool(args.key):
        parser.error("Provide both --cert and --key")
    ip = args.address
    if not ip:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
                sock.connect(("192.0.2.1", 80))
                ip = sock.getsockname()[0]
        except OSError:
            ip = "127.0.0.1"
    app = create_app(args.folder)
    scheme = "https" if args.cert else "http"
    app.state.public_url = f"{scheme}://{ip}:{args.port}"
    url = f"{scheme}://127.0.0.1:{args.port}/admin/{app.state.admin}"
    print(f"Local First: {app.state.public_url} | Files: {app.state.folder}")
    print("Close this window or press Ctrl+C to stop the server.")
    threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    uvicorn.run(app, host="0.0.0.0", port=args.port, access_log=False, ssl_certfile=args.cert, ssl_keyfile=args.key, ws_max_size=65536)

if __name__ == "__main__":
    main()

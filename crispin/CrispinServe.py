import json
import os
import threading
import time
import subprocess
from http.server import BaseHTTPRequestHandler, HTTPServer

from dotenv import dotenv_values

from crispin.CrispinAPI import get_kickstart, post_kickstart
from crispin.CrispinIPXE import generate_menu


class CrispinServer(BaseHTTPRequestHandler):
    ipxe_menu = ""
    ipxe_dir = ""

    def __init__(self, *args, cookbook_dir=None, hostname=None, ipxe_dir=None, **kwargs):
        self.cookbook_dir = cookbook_dir
        self.hostname = hostname
        self.ipxe_dir = ipxe_dir
        super().__init__(*args, **kwargs)

    def send_json_error(self, code, message):
        self.send_response(code)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        self.wfile.write(bytes(json.dumps({"error": message}), "utf-8"))

    def do_GET(self):
        if self.path.startswith("/crispin/get/"):
            answer_name = self.path.split("/")[-1]
            try:
                kickstart = get_kickstart(answer_name, self.cookbook_dir)
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(bytes(kickstart, "utf-8"))
            except FileNotFoundError as e:
                self.send_json_error(404, str(e))
            except Exception as e:
                self.send_json_error(500, str(e))
        elif self.path == "/autoexec.ipxe":
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(bytes(self.ipxe_menu, "utf-8"))
        elif self.path.endswith(("/vmlinuz", "/initrd.img")):
            safe_path = os.path.abspath(os.path.join(self.ipxe_dir, self.path.lstrip('/')))
            if not safe_path.startswith(os.path.abspath(self.ipxe_dir)):
                self.send_json_error(403, "Forbidden")
                return

            try:
                with open(safe_path, "rb") as f:
                    self.send_response(200)
                    self.send_header("Content-type", "application/octet-stream")
                    self.end_headers()
                    self.wfile.write(f.read())
            except FileNotFoundError:
                self.send_json_error(404, "File not found")
        else:
            self.send_json_error(404, "Not Found")

    def do_POST(self):
        if self.path.startswith("/crispin/get/"):
            recipe_name = self.path.split("/")[-1]
            try:
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                kickstart = post_kickstart(recipe_name, post_data, self.cookbook_dir)
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(bytes(kickstart, "utf-8"))
            except FileNotFoundError as e:
                self.send_json_error(404, str(e))
            except ValueError as e:
                self.send_json_error(400, str(e))
            except Exception as e:
                self.send_json_error(500, str(e))
        else:
            self.send_json_error(404, "Not Found")

def start_standalone_tftp(root_dir, port=6969):
    # Ensure root_dir is absolute
    root_dir = os.path.abspath(root_dir)
    
    # We use 'in.tftpd' which is the standard Linux TFTP server daemon.
    # --listen: Run as a standalone daemon (not via inetd)
    # --address: Bind to all IPs on your custom port
    # --secure: Changes the root to the specified directory for safety
    # --user: Changes the user to tftp user for security.
    # NOTE: User option requires binary capabilities
    # setcap 'cap_setuid,cap_setgid,cap_sys_chroot+ep' /usr/sbin/in.tftpd
    cmd = [
        "in.tftpd",
        "--listen",
        "--address", f"0.0.0.0:{port}",
        "--secure",
        "--user", "tftp",
        root_dir
    ]

    print(f"[*] Launching TFTP on port {port}...")
    print(f"[*] Serving files from: {root_dir}")

    try:
        # Start the process. We don't need sudo because the port is > 1024
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Check if it died immediately (e.g., binary not found)
        time.sleep(1)
        # Need to poll the proc to get the return code
        proc.poll()
        if proc.returncode != 0:
            print(proc.__dict__)
            stderr = proc.stderr.read().decode()
            print(f"[!] Server failed to start: {stderr}. Exit Code: {proc.returncode}")
        else:
            proc.wait()
    except FileNotFoundError:
        print("[!] Error: 'in.tftpd' not found. Install it with 'sudo apt install tftpd-hpa'")

def run(server_class=HTTPServer, handler_class=CrispinServer, port=9000, cookbook_dir=None, ipxe_dir=None):
    config = dotenv_values(".env")
    hostname = config.get("HOSTNAME", "localhost")

    if cookbook_dir is None:
        raise ValueError("cookbook_dir must be provided")
    if ipxe_dir is None:
        raise ValueError("ipxe_dir must be provided")
    
    # Start TFTP server in a separate thread
    print("Starting in.tftpd on port 6969...")
    tftp_thread = threading.Thread(target=start_standalone_tftp, args=(ipxe_dir, 6969), daemon=True)
    tftp_thread.start()
    handler_class.ipxe_menu = generate_menu(cookbook_dir, hostname)
    handler_class.ipxe_dir = ipxe_dir

    def handler_wrapper(*args, **kwargs):
        return handler_class(*args, cookbook_dir=cookbook_dir, hostname=hostname, ipxe_dir=ipxe_dir, **kwargs)

    server_address = ('', port)
    httpd = server_class(server_address, handler_wrapper)
    print(f"Starting httpd on port {port}...")
    httpd.serve_forever()


if __name__ == "__main__":
    # This is for testing purposes only
    import tempfile
    from pathlib import Path

    with tempfile.TemporaryDirectory() as tmpdir:
        cookbook_dir = Path(tmpdir)
        (cookbook_dir / "answers").mkdir()
        (cookbook_dir / "recipes").mkdir()
        (cookbook_dir / "templates").mkdir()
        run(cookbook_dir=cookbook_dir)

import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from crispin.CrispinAPI import get_kickstart, post_kickstart

class CrispinServer(BaseHTTPRequestHandler):
    def __init__(self, *args, cookbook_dir=None, **kwargs):
        self.cookbook_dir = cookbook_dir
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

def run(server_class=HTTPServer, handler_class=CrispinServer, port=9000, cookbook_dir=None):
    if cookbook_dir is None:
        raise ValueError("cookbook_dir must be provided")

    def handler_wrapper(*args, **kwargs):
        return handler_class(*args, cookbook_dir=cookbook_dir, **kwargs)

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

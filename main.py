from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
import mimetypes
import pathlib
import json
import os
from datetime import datetime
from jinja2 import Environment, FileSystemLoader

class HttpHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message.html':
            self.send_html_file('message.html')
        elif pr_url.path == '/read':
            env = Environment(loader=FileSystemLoader('read'))
            template = env.get_template('messages.html')
            DATA_FILE = "storage/data.json"
            messages = {}
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, "r") as f:
                    messages = json.load(f)
            output = template.render(messages=messages)
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(output.encode('utf-8'))
        else:
            file_path = pathlib.Path().joinpath(pr_url.path[1:])
            if file_path.exists():
                self.send_static()
            else:
                self.send_html_file('error.html', 404)

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as f:
            self.wfile.write(f.read())

    def send_static(self):
        self.send_response(200)
        mt = mimetypes.guess_type(self.path)
        self.send_header("Content-type", mt[0] if mt[0] else "text/plain")
        self.end_headers()
        with open(f'.{self.path}', 'rb') as f:
            self.wfile.write(f.read())

    def do_POST(self):
        if self.path == '/message':
            size = int(self.headers['Content-Length'])
            data = self.rfile.read(size)
            data_parse = urllib.parse.unquote_plus(data.decode())
            data_dict = {key: value for key, value in [el.split('=') for el in data_parse.split('&')]}
            timestamp = str(datetime.now())
            message = {
                "username": data_dict.get("username"),
                "message": data_dict.get("message")
            }
            DATA_FILE = "storage/data.json"
            if not os.path.exists(DATA_FILE):
                with open(DATA_FILE, "w") as f:
                    json.dump({}, f)
            with open(DATA_FILE, "r") as f:
                messages = json.load(f)
            messages[timestamp] = message
            with open(DATA_FILE, "w") as f:
                json.dump(messages, f, indent=2)
            self.send_response(302)
            self.send_header('Location', '/')
            self.end_headers()

def run():
    server = HTTPServer(('', 3000), HttpHandler)
    print("Server running on port 3000...")
    server.serve_forever()

if __name__ == '__main__':
    run()
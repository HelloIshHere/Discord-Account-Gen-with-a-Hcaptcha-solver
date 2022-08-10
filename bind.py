from http.server import HTTPServer, SimpleHTTPRequestHandler
import socket
from contextlib import closing
import ssl

from jinja2 import Environment, PackageLoader, select_autoescape
env = Environment(
    loader=PackageLoader("bind"),
    autoescape=select_autoescape()
)

class PythonServer(SimpleHTTPRequestHandler):
    """Python HTTP Server that handles GET and POST requests"""
    def do_GET(self):
        if self.path == '/':
            template = env.get_template("index.html")
            file = template.render()
            self.send_response(200, "OK")
            self.end_headers()
            self.wfile.write(bytes(file, "utf-8"))

IP = '127.0.0.1'

# PORT = 9120
PORT = 22003
print(PORT)

httpd = HTTPServer((IP, PORT), SimpleHTTPRequestHandler)
httpd.socket = ssl.wrap_socket (
    httpd.socket, server_side=True,
    certfile='cert/ssl_cert.pem',keyfile="cert/ssl_key.pem")

httpd.get_request

print("Server start at: https://{}:{}".format(IP, PORT))
httpd.serve_forever()
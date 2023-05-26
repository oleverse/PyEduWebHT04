import mimetypes
import os.path
import socket
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import UDPServer, BaseRequestHandler


class CustomHTTPRequestHandler(BaseHTTPRequestHandler):
    ERROR_HTML_FILE = 'error.html'

    def do_GET(self):
        request_url = urllib.parse.urlparse(self.path)
        file_name, status = self.resolve_route(request_url.path)
        self.send_file(file_name, status)

    @staticmethod
    def has_extension(file_path):
        return file_path.split('.')[-1].isalpha()

    def get_route_path(self, route_path):
        if route_path == '/':
            return 'index.html'
        elif self.has_extension(route_path):
            return route_path[1:]
        else:
            return f"{route_path[1:]}.html"

    def resolve_route(self, route_path):
        status = 200
        file_path = self.get_route_path(route_path)

        if not (file_path and os.path.isfile(file_path)):
            file_path, status = self.ERROR_HTML_FILE, 404

        return file_path, status

    def send_file(self, file_name, status=200):
        self.send_response(status)
        mime_type = mimetypes.guess_type(file_name)
        self.send_header('Content-Type', mime_type[0] if mime_type else 'text/plain')
        self.end_headers()

        with open(file_name, 'rb') as html_file:
            self.wfile.write(html_file.read())


class CustomUDPHandler(BaseRequestHandler):
    def handle(self) -> None:
        data = self.request[0].strip()
        print(f"Received data: {data} from: {self.client_address[0]}")


def run_web_server(server_class=HTTPServer, handler_class=CustomHTTPRequestHandler):
    server_address = ('', 3000)
    web_server = server_class(server_address, handler_class)

    (web_server_thread := threading.Thread(target=web_server.serve_forever)).start()

    return web_server, web_server_thread


def run_udp_server(server_class=UDPServer, handler_class=CustomUDPHandler):
    server_address = ('', 5000)
    udp_server = server_class(server_address, handler_class)

    (udp_server_thread := threading.Thread(target=udp_server.serve_forever)).start()

    return udp_server, udp_server_thread


def run():
    global is_udp_server_active

    web_server, web_server_thread = run_web_server()
    udp_server, udp_server_thread = run_udp_server()

    try:
        for thread in web_server_thread, udp_server_thread:
            thread.join()
    except KeyboardInterrupt:
        print("Trying to stop all threads...")
        udp_server.shutdown()
        web_server.shutdown()


if __name__ == "__main__":
    is_udp_server_active = True
    run()

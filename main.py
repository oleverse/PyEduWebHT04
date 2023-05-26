import os.path
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler


class CustomHTTPRequestHandler(BaseHTTPRequestHandler):
    ERROR_HTML_FILE = 'error.html'

    def do_GET(self):
        request_url = urllib.parse.urlparse(self.path)
        if request_url.path == '/':
            file_name, status = self.get_file_with_status('index.html')
        else:
            file_name, status = self.get_file_with_status(f'{request_url.path[1:]}.html')

        self.send_html_file(file_name, status)

    def get_file_with_status(self, file_name):
        if os.path.isfile(file_name):
            return file_name, 200
        else:
            return self.ERROR_HTML_FILE, 404

    def send_html_file(self, file_name, status=200):
        self.send_response(status)

        self.send_header('Content-Type', 'text/html')
        self.end_headers()

        with open(file_name, 'rb') as html_file:
            self.wfile.write(html_file.read())


def run(server_class=HTTPServer, handler_class=CustomHTTPRequestHandler):
    server_address = ('', 3000)
    http = server_class(server_address, handler_class)

    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


if __name__ == "__main__":
    run()

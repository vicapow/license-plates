from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import io
from LicensePlateExtractor import LicensePlateExtractor, LICENSE_DATA_PATH, FRAME_DATA_PATH
from args import parse_args
from PIL import Image

# TO test
# curl -X POST -H "Content-Type: image/jpeg" --data-binary "@example_1.jpg" http://localhost:8004


def createHandler(args):
    plate_extractor = LicensePlateExtractor(args)

    class MyRequestHandler(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

        def _send_response(self, status_code, response_text):
            self.send_response(status_code)
            self.send_header('Content-type', 'text/plain')
            self.end_headers()
            self.wfile.write(response_text.encode('utf-8'))

        def do_POST(self):
            content_type = self.headers.get('Content-Type')
            if content_type == 'image/jpeg':
                content_length = int(self.headers.get('Content-Length'))
                image_data = self.rfile.read(content_length)
                img = Image.open(io.BytesIO(image_data))
                plate_extractor.extract_and_save(img)
                # You can process the image data here.
                # For simplicity, we'll just return a response with the length of the received image data.
                response_text = f"Received image with {len(image_data)} bytes"
                self._send_response(200, response_text)
            else:
                self._send_response(
                    400, f"Unsupported content type: {content_type}")
    return MyRequestHandler


def run(server_class=HTTPServer, handler_class=None, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Starting server on port {port}")
    httpd.serve_forever()


if __name__ == '__main__':
    args = parse_args()
    run(handler_class=createHandler(args), port=args.port)

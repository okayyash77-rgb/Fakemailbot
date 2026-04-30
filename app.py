import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import bot

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")
    def log_message(self, format, *args):
        pass

def run_server():
    server = HTTPServer(("0.0.0.0", 8080), Handler)
    server.serve_forever()

if __name__ == "__main__":
    t = threading.Thread(target=run_server)
    t.daemon = True
    t.start()
    bot.main()

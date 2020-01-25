import socket
from flask import Flask
from common_utils import retreive_screenshot
from threading import Thread

app = Flask(__name__, template_folder='template')


@app.route('/server')
def get_server():
    sock=socket.socket()
    print("Socket successfully created")
    port=8000
    sock.bind(('127.0.0.1', port))
    print("socket binded to %s" % (port))
    sock.listen(5)
    print("socket is listening")
    try:
        while True:
            conn, addr=sock.accept()
            print('Got connection from', addr)
            conn.send('Thank you for connecting'.encode())
            thread=Thread(target=retreive_screenshot, args=(conn,))
            thread.start()
    finally:
        sock.close()


if __name__ == '__main__':
    app.run(port=5001)

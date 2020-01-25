import socket
from flask import Flask, render_template
from common_utils import recvall
from zlib import decompress
import pygame

app=Flask(__name__, template_folder='template')

WIDTH=1366
HEIGHT=768


@app.route('/client')
def get_client():
    pygame.init()
    screen=pygame.display.set_mode((WIDTH, HEIGHT))
    clock=pygame.time.Clock()
    watching=True
    sock=socket.socket()
    port=8000
    sock.connect(('', port))
    print(sock.recv(1024))

    try:
        while watching:
            print(pygame.event.get())
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print(event)
                    watching=False
                    break
            size_len=int.from_bytes(sock.recv(1), byteorder='big')
            print(size_len)
            # size = int.from_bytes(sock.recv(size_len), byteorder='big')
            size=int.from_bytes(recvall(sock, size_len), byteorder='big')
            pixels=decompress(recvall(sock, size))
            # Create the Surface from raw pixels
            img=pygame.image.fromstring(pixels, (WIDTH, HEIGHT), 'RGB')

            # Display the picture
            screen.blit(img, (0, 0))
            pygame.display.flip()
            clock.tick(60)
    finally:
        sock.close()


if __name__ == '__main__':
    app.run(port=5002)

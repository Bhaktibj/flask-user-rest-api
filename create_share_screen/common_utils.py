import mss
from zlib import compress
from mss import mss

WIDTH=1366
HEIGHT=768


def retreive_screenshot(conn):
    with mss(display=':0') as sct:
        # The region to capture
        rect={'top': 0, 'left': 0, 'width': WIDTH, 'height': HEIGHT}

        while 'recording':
            # Capture the screen
            img=sct.grab(rect)
            # Tweak the compression level here (0-9)
            # obj = lzma.LZMACompressor()
            pixels=compress(img.rgb, 6)
            # pixels = obj.flush()
            # Send the size of the pixels length
            size=len(pixels)
            size_len=(size.bit_length() + 7) // 8
            conn.send(bytes([size_len]))

            # Send the actual pixels length
            size_bytes=size.to_bytes(size_len, 'big')
            conn.send(size_bytes)
            # Send pixels
            conn.sendall(pixels)


def recvall(conn, length):
    """ Retreive all pixels. """

    buf=b''
    while len(buf) < length:
        data=conn.recv(length - len(buf))
        if not data:
            return data
        buf+=data
    return buf

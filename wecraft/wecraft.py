from datetime import datetime
from functools import reduce
from serial import Serial
from select import select

SCALE = 9360/12


class WeCraft:

    def __init__(self, tty):
        self._conn = Serial(tty, 115200)

    def _send_bytes(self, data):
        self._conn.write(b''.join([
            b'\xfe\xfe\xfe\x68',
            data,
            bytes([reduce(lambda a, b: (a + b) % 0x100, data), 0x16])
        ]))

    def move(self, x, y, cut=False):
        """
        Move trolley to given coordinates.

        x:   Trolley position. Increasing numbers move trolley rightwards.
        y:   Feed position. Increasing numbers feed more material from tray.
        cut: Whether this is a cutting move or a positioning move.
        """
        bc = bytes([cut])
        bx = int(x*SCALE).to_bytes(4, 'little', signed=True)
        by = int(y*SCALE).to_bytes(4, 'little', signed=True)
        self._send_bytes(bc + bx + by)

    def home(self):
        """Home trolley position and align with left edge of material."""
        self._send_bytes(b'\x0a')

    def zero(self):
        """Treat current trolley and feed position as x=0, y=0."""
        self._send_bytes(b'\x0c')

    def load(self):
        """Feed material from tray and move trolley to bottom-left corner."""
        self._send_bytes(b'\x0e')


def main():
    """
    Allows spying on traffic between a cutting machine and an application running in WINE.

    Use with `socat -d -d pty,raw,echo=0 pty,raw,echo=0`.
    Change `input_tty` to point to one end of the tunnel.
    Symbolically link the other end of the tunnel to `~/.wine/dosdevices/com1`.
    """

    wecraft_tty = '/dev/ttyUSB0'
    wecraft = WeCraft(wecraft_tty)

    input_tty = '/dev/pts/4'
    input_conn = open(input_tty, 'rb+', buffering=0)

    rlist = [wecraft._conn, input_conn]
    wlist = [wecraft._conn, input_conn]

    print(f"Forwarding {input_tty} <-> {wecraft_tty} ...")

    while True:
        r, w, _ = select(rlist, wlist, [])

        if input_conn in r and wecraft._conn in w:
            buf = input_conn.read()
            wecraft._conn.write(buf)
            print(f"{datetime.now()} > {buf.hex()}")

        if wecraft._conn in r and input_conn in w:
            buf = wecraft._conn.read()
            input_conn.write(buf)
            print(f"{datetime.now()} < {buf.hex()}")


if __name__ == "__main__":
    main()


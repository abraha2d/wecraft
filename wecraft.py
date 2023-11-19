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

    def move_to(self, x, y, blade_down=False):
        mb = bytes([blade_down])
        mx = int(x*SCALE).to_bytes(4, 'little', signed=True)
        my = int(y*SCALE).to_bytes(4, 'little', signed=True)
        self._send_bytes(mb + mx + my)

    def find_home(self):
        self._send_bytes(b'\x0a')

    def set_zero(self):
        self._send_bytes(b'\x0c')

    def load_stock(self):
        self._send_bytes(b'\x0e')


def main():
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


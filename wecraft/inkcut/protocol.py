from functools import reduce

from inkcut.device.plugin import DeviceProtocol
from twisted.internet.defer import Deferred

BUFFER: bytes = b''
INFLIGHT: list[tuple[int, Deferred]] = []


class ECraftProtocol(DeviceProtocol):
    inkcut_scale = 1 / 90
    ecraft_scale = 780
    scale = ecraft_scale * inkcut_scale

    def connection_made(self):
        self.write(b'\x0e')
        self.write(b'\x0c')

    def set_pen(self, p):
        raise NotImplementedError

    def set_force(self, f):
        raise NotImplementedError

    def set_velocity(self, v):
        raise NotImplementedError

    def move(self, x, y, z, absolute=True):
        print(f"\n ------\n| MOVE {x=} {y=} {z=}\n ------\n")
        bc = bytes([z])
        bx = int(x * self.scale).to_bytes(4, 'little', signed=True)
        by = int(y * self.scale).to_bytes(4, 'little', signed=True)
        return self.write(bc + bx + by)

    def write(self, data):
        global INFLIGHT
        INFLIGHT.append((data[0], Deferred()))

        super().write(b''.join([
            b'\xfe\xfe\xfe\x68',
            data,
            bytes([reduce(lambda a, b: (a + b) % 0x100, data), 0x16]),
        ]))

        return INFLIGHT[-1][1]

    def data_received(self, _data):
        global BUFFER, INFLIGHT
        BUFFER += _data

        while b'\x16' in BUFFER:
            split = BUFFER.find(b'\x16')
            data = BUFFER[:split+1]
            BUFFER = BUFFER[split+1:]

            assert data[:4] == b'\xfe\xfe\xfe\x68'
            assert data[-2] == reduce(lambda a, b: (a + b) % 0x100, data[4:-2])
            assert data[-1] == 0x16

            payload = data[4:-2]
            assert payload[0] & 0xf == INFLIGHT[0][0]

            if payload[1] == 1:
                i = INFLIGHT.pop(0)
                i[1].callback(None)

    def finish(self):
        return self.move(0, 13 / self.inkcut_scale, 0)

"""
    Disassembler for GalaxyScript bytecode.

    The MIT License (MIT)

    Copyright (c) 2015 Joel Hoener <athre0z@zyantific.com>

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:
    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.
    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
"""

from __future__ import print_function, division

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tables import decode_unk, opcodes

class EncodedInsn(object):
    def __init__(self, raw):
        if type(raw) not in (int, long) or raw > 0xFFFFFFFF or raw < 0:
            raise ValueError('invalid raw instruction')
        self.raw = raw

    def __getitem__(self, item):
        if isinstance(item, slice):
            assert 0 <= item.start <= 32
            assert 0 <= item.stop <= 32
            if item.step is not None:
                raise NotImplementedError('stepping is not implemented')
            return (((2 ** (item.stop - item.start) - 1) << item.start) & self.raw) >> item.start
        raise NotImplementedError()

    def __repr__(self):
        return 'EncodedInsn(raw=0x{:08X})'.format(self.raw)


class DecodedInsn(object):
    def __init__(self):
        self.mnem = None
        self.info = None
        self.opcode = None
        self.ops = None

    def textual(self):
        return self.mnem.ljust(16) + ' ' + ', '.join([op.textual() for op in self.ops])

    def __repr__(self):
        return 'DecodedInsn(mnem="{}", ops={})'.format(self.mnem, repr(self.ops))


class InsnDecoder(object):
    def __init__(self, encoded_insn):
        self.enc = encoded_insn
        self.dec = DecodedInsn()

    def decode(self):
        self._dec_opcode()
        self._dec_operands()
        return self.dec

    def _dec_opcode(self):
        self.dec.opcode = self.enc[26:32]
        try:
            self.dec.mnem = opcodes[self.dec.opcode][0]
            self.dec.info = opcodes[self.dec.opcode][2]
        except KeyError:
            self.dec.mnem = 'ud_{:02X}'.format(self.dec.opcode)

    def _dec_operands(self):
        try:
            decoder = opcodes[self.dec.opcode][1]
        except IndexError:
            decoder = decode_unk
        self.dec.ops = decoder(self.enc)


def main():
    with open('gscodeseg.gsvm', 'rb') as f:
        input = bytearray(f.read())

    import struct
    import time

    start = time.time()
    with open('disas.gsvmasm', 'w') as f:
        for cur_offs in xrange(0, len(input), 4):
            f.write(InsnDecoder(EncodedInsn(
                struct.unpack('<I', input[cur_offs:cur_offs + 4])[0])
            ).decode().textual() + '\n')
    print('Disassembling took {} seconds.'.format(time.time() - start))

if __name__ == '__main__':
    main()

#!/usr/bin/env python

import sys


def blksec(offs):
    """Get offset in sector, block, and byte given a total offset."""
    sec, soffs = divmod(offs, Sector.N_BLOCKS * Block.N_BYTES)
    blk, boffs = divmod(soffs, Block.N_BYTES)
    return (sec, blk, boffs)


def hexstr(list_of_ints):
    return ' '.join("%02x" % x for x in list_of_ints)


class Block(list):

    N_BYTES = 16

    def is_interesting(self):
        for byte in self:
            if byte != 0:
                return True

    @classmethod
    def iparse(cls, itr):
        bytes_ = []
        for _ in range(cls.N_BYTES):
            bytes_.append(ord(next(itr)))
        bytes_.extend(bytes_)
        return cls(bytes_)

    def __str__(self):
        return hexstr(self)


class Sector(object):

    N_BLOCKS = 4
    KEY_BLOCK = 3

    def __init__(self, blocks):
        self.blocks = blocks

    def key_a(self):
        return self.blocks[self.KEY_BLOCK][0:6]

    def key_b(self):
        return self.blocks[self.KEY_BLOCK][10:16]

    def access_bits(self):
        return self.blocks[self.KEY_BLOCK][6:10]

    def is_interesting(self):
        for i, block in enumerate(self.blocks):
            if i != self.KEY_BLOCK:
                if block.is_interesting():
                    return True
        return False

    def __getitem__(self, index):
        return self.blocks[index]

    def __str__(self):
        # TODO: Interpret the access bits.
        s = "Accessbits: %s\n" % hexstr(self.access_bits())
        s += "Key A: %s\n" % hexstr(self.key_a())
        s += "Key B: %s\n" % hexstr(self.key_b())
        for i, block in enumerate(self.blocks):
            if i != self.KEY_BLOCK and block.is_interesting():
                s += "Block %d: %s\n" % (i, block)
        return s

    @classmethod
    def iparse(cls, itr):
        blocks = []
        for _ in range(cls.N_BLOCKS):
            blocks.append(Block.iparse(itr))
        return cls(blocks)


class MFDump(object):

    N_SEC = 16

    def __init__(self, sectors):
        self.sectors = sectors

    def nuid(self):
        return self.sectors[0][0][0:4]

    def __str__(self):
        s = "NUID: %s\n" % hexstr(self.nuid())
        for i, sector in enumerate(self.sectors):
            if sector.is_interesting():
                s += "Sector %02d\n" % i
                s += str(sector) + "\n"
        return s[0:-1]

    @classmethod
    def iparse(cls, itr):
        sectors = []
        for _ in range(cls.N_SEC):
            sectors.append(Sector.iparse(itr))
        return cls(sectors)


class Fiter(object):
    def __init__(self, path):
        self.f = open(path, 'rb')

    def __iter__(self):
        return self

    def next(self):
        return self.f.read(1)


def _main():
    # print "Sector: %d\nBlock: %d\nByte: %d" % blksec(int(sys.argv[1], 16))
    dumpfile = sys.argv[1]
    d = MFDump.iparse(Fiter(dumpfile))
    print d


if __name__ == '__main__':
    _main()

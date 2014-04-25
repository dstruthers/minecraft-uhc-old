import struct, zlib
import nbt
from StringIO import StringIO

class RegionFile:
    '''Representation of Minecraft region file format'''
    # See: http://minecraft.gamepedia.com/Region_file_format

    def __init__(self, filepath):
        self.fp = open(filepath, 'r')
        self.chunk_info = []
        for i in range(0, 1024):
            data = self.fp.read(4)
            offset = struct.unpack('>I', '\0' + data[0:3])[0]
            sector_count = struct.unpack('>B', data[3])[0]
            self.chunk_info.append((offset, sector_count))

        for i in range(0, 1024):
            data = self.fp.read(4)
            mtime = struct.unpack('>I', data)
            self.chunk_info[i] = self.chunk_info[i] + mtime

        self.chunks = []
        for (offset, sector_count, timestamp) in self.chunk_info:
            if (offset < 2): continue # Skip empty chunks

            self.fp.seek(offset * 4096)
            data_length = struct.unpack('>I', self.fp.read(4))[0]
            compression_type = self.fp.read(1)
            chunk_data = self.fp.read(data_length - 1)
            if compression_type == '\x01': # Unused in practice
                raise Exception('Found gzip-compressed chunk data!')
            elif compression_type == '\x02':
                data = nbt.parse(StringIO(zlib.decompress(chunk_data)))
                self.chunks.append(data)

import os, struct, subprocess, zlib
from StringIO import StringIO

class MinecraftServer:
    """Encapsulates a running Minecraft server"""

    def __init__(self, minecraft_dir, minecraft_jar, java_opts = ''):
        self.process = None
        self.minecraft_dir = minecraft_dir
        self.minecraft_jar = minecraft_jar
        self.java_opts = java_opts

    def start(self):
        """Start the Minecraft server"""
        os.chdir(self.minecraft_dir)
        self.process = subprocess.Popen(['java', '-jar', self.minecraft_jar],
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE)

    def stop(self):
        """Stop the Minecraft server"""
        if self.process:
            self.process.stdin.write('/stop\n')
                                        
    def is_running(self):
        """Returns True if server is running"""
        self.process.poll()
        return self.process.returncode == None

    def returncode(self):
        """Return code of stopped server, or None if server is still running"""
        self.process.poll()
        return self.process.returncode

    def readline(self):
        """Read a line of server output"""
        return self.process.stdout.readline()

    def write(self, input):
        """Write to server's stdin"""
        self.process.stdin.write(input)

# NBT Types
# Source: http://minecraft.gamepedia.com/NBT_Format
TAG_End = 0
TAG_Byte = 1
TAG_Short = 2
TAG_Int = 3
TAG_Long = 4
TAG_Float = 5
TAG_Double = 6
TAG_ByteArray = 7
TAG_String = 8
TAG_List = 9
TAG_Compound = 10
TAG_IntArray = 11

def parse_nbt(nbt_data):
    """Parse decompressed NBT data"""

    def tag_to_class(tag):
        if tag == TAG_End: return NBTEnd
        if tag == TAG_Byte: return NBTByte
        if tag == TAG_Short: return NBTShort
        if tag == TAG_Int: return NBTInt
        if tag == TAG_Long: return NBTLong
        if tag == TAG_Float: return NBTFloat
        if tag == TAG_Double: return NBTDouble
        if tag == TAG_ByteArray: return NBTByteArray
        if tag == TAG_String: return NBTString
        if tag == TAG_List: return NBTList
        if tag == TAG_Compound: return NBTCompound
        if tag == TAG_IntArray: return NBTIntArray

    def parse_payload(cls, stream):
        if cls == NBTByte:
            return struct.unpack('>b', stream.read(1))[0]
        elif cls == NBTShort:
            return struct.unpack('>h', stream.read(2))[0]
        elif cls == NBTInt:
            return struct.unpack('>i', stream.read(4))[0]
        elif cls == NBTLong:
            return struct.unpack('>q', stream.read(8))[0]
        elif cls == NBTFloat:
            return struct.unpack('>f', stream.read(4))[0]
        elif cls == NBTDouble:
            return struct.unpack('>d', stream.read(8))[0]
        elif cls == NBTByteArray:
            num_bytes = parse_payload(NBTInt, stream)
            bytes = []
            for i in range(0, num_bytes):
                bytes.append(struct.unpack('>b', stream.read(1))[0])
            return bytes
        elif cls == NBTString:
            # WARNING: Not Unicode aware!
            length = parse_payload(NBTShort, stream)
            return stream.read(length)
        elif cls == NBTList:
            tag_id = parse_payload(NBTByte, stream)
            size = parse_payload(NBTInt, stream)
            cls = tag_to_class(tag_id)
            elements = []
            for i in range(0, size):
                elements.append(parse_payload(cls, stream))
            return (cls, elements)
        elif cls == NBTCompound:
            parsed = None
            elements = []
            while parsed.__class__ != NBTEnd:
                parsed = parse(stream)
                elements.append(parsed)
            return elements
        else:
            raise Exception('Cannot parse class: %r' % cls)

    def parse (stream):
        tag = ord(stream.read(1))
        if tag == TAG_End:
            return NBTEnd()

        name_length = struct.unpack('>H', stream.read(2))[0]
        name = stream.read(name_length)
    
        if tag == TAG_Byte:
            byte = parse_payload(NBTByte, stream)
            return NBTByte(name, byte)

        elif tag == TAG_Short:
            s = parse_payload(NBTShort, stream)
            return NBTShort(name, s)

        elif tag == TAG_Int:
            i = parse_payload(NBTInt, stream)
            return NBTInt(name, i)

        elif tag == TAG_Long:
            l = parse_payload(NBTLong, stream)
            return NBTLong(name, l)

        elif tag == TAG_Float:
            f = parse_payload(NBTFloat, stream)
            return NBTFloat(name, f)

        elif tag == TAG_Double:
            d = parse_payload(NBTDouble, stream)
            return NBTDouble(name, d)

        elif tag == TAG_ByteArray:
            bytes = parse_payload(NBTByteArray, stream)
            return NBTByteArray(name, bytes)

        elif tag == TAG_String:
            s = parse_payload(NBTString, stream)
            return NBTString(name, s)

        elif tag == TAG_List:
            cls, elements = parse_payload(NBTList, stream)
            return NBTList(name, cls, elements)

        elif tag == TAG_Compound:
            elements = parse_payload(NBTCompound, stream)
            return NBTCompound(name, elements)

        elif tag == TAG_IntArray:
            size = parse_payload(NBTInt, stream)
            elements = []
            for i in range(0, size):
                elements.append(parse_payload(NBTInt, stream))
            return NBTIntArray(name, elements)

        else:
            raise Exception('Cannot parse tag: %d' % tag)

    return parse(StringIO(nbt_data))


class NBTEnd: pass

class NBTByte:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class NBTShort:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class NBTInt:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class NBTLong:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class NBTFloat:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class NBTDouble:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class NBTByteArray:
    def __init__(self, name, elements):
        self.name = name
        self.elements = elements

class NBTString:
    def __init__(self, name, value):
        self.name = name
        self.value = value

class NBTList:
    def __init__(self, name, type, elements):
        self.name = name
        self.type = type
        self.elements = elements
        
class NBTCompound:
    def __init__(self, name, elements):
        self.name = name
        self.elements = elements

class NBTIntArray:
    def __init__(self, name, elements):
        self.name = name
        self.elements = elements
    
class RegionFile:
    """Representation of Minecraft region file format"""
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
                self.chunks.append(parse_nbt(zlib.decompress(chunk_data)))
            
class Chunk:
    """Representation of Minecraft chunk"""

    def __init__(self, chunk_data):
        self.chunk_data = chunk_data

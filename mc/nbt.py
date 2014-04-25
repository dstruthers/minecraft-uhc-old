import struct

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

def parse(handle):
    '''Parse decompressed NBT data'''
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
        raise Exception('Cannot convert unknown tag to class: %d' % tag)

    def parse_payload(cls, handle):
        if cls == NBTByte:
            return struct.unpack('>b', handle.read(1))[0]
        elif cls == NBTShort:
            return struct.unpack('>h', handle.read(2))[0]
        elif cls == NBTInt:
            return struct.unpack('>i', handle.read(4))[0]
        elif cls == NBTLong:
            return struct.unpack('>q', handle.read(8))[0]
        elif cls == NBTFloat:
            return struct.unpack('>f', handle.read(4))[0]
        elif cls == NBTDouble:
            return struct.unpack('>d', handle.read(8))[0]
        elif cls == NBTByteArray:
            num_bytes = parse_payload(NBTInt, handle)
            bytes = []
            for i in range(0, num_bytes):
                bytes.append(struct.unpack('>b', handle.read(1))[0])
            return bytes
        elif cls == NBTString:
            # WARNING: Not Unicode aware!
            length = parse_payload(NBTShort, handle)
            return handle.read(length)
        elif cls == NBTList:
            tag_id = parse_payload(NBTByte, handle)
            size = parse_payload(NBTInt, handle)
            cls = tag_to_class(tag_id)
            elements = []
            for i in range(0, size):
                elements.append(parse_payload(cls, handle))
            return (cls, elements)
        elif cls == NBTCompound:
            parsed = None
            elements = []
            while parsed.__class__ != NBTEnd:
                parsed = parse(handle)
                elements.append(parsed)
            return elements
        elif cls == NBTIntArray:
            size = parse_payload(NBTInt, handle)
            elements = []
            for i in range(0, size):
                elements.append(parse_payload(NBTInt, handle))
            return elements
        else:
            raise Exception('Cannot parse class: %r' % cls)

    tag = ord(handle.read(1))
    if tag == TAG_End:
        return NBTEnd()

    name_length = struct.unpack('>H', handle.read(2))[0]
    name = handle.read(name_length)

    if tag == TAG_List:
        cls, elements = parse_payload(NBTList, handle)
        return NBTList(name, cls, elements)
    else:
        cls = tag_to_class(tag)
        value = parse_payload(cls, handle)
        return cls(name, value)

class NBTBase:
    '''Base class providing default constructor used by many NBT types'''
    def __init__(self, name, value):
        self.name = name
        self.value = value
class NBTMultiValueBase:
    '''Base class providing default constructor used by most NBT types
       that are multi-value'''
    def __init__(self, name, elements):
        self.name = name
        self.elements = elements
class NBTEnd: pass
class NBTByte(NBTBase): pass
class NBTShort(NBTBase): pass
class NBTInt(NBTBase): pass
class NBTLong(NBTBase): pass
class NBTFloat(NBTBase): pass
class NBTDouble(NBTBase): pass
class NBTString(NBTBase): pass
class NBTByteArray(NBTMultiValueBase): pass
class NBTCompound(NBTMultiValueBase): pass
class NBTIntArray(NBTMultiValueBase): pass
class NBTList:
    def __init__(self, name, type, elements):
        self.name = name
        self.type = type
        self.elements = elements

import enum
import io
from . import binary_io

class File:
    def __init__(self):
        self._name_array = []
        self._string_array = []
        self._path_array = []
        self.root = None

    def load_raw(self, raw):
        # Open a big-endian binary reader on the stream.
        with binary_io.BinaryReader(raw) as reader:
            reader.endianness = ">"
            header = Header.from_file(reader)
            # Read the name array, holding strings referenced by index for the name of other nodes.
            reader.seek(header.name_array_offset)
            self._name_array = self._read_node(reader)
            # Read the optional string array, holding strings referenced by index in string nodes.
            if header.string_array_offset:
                reader.seek(header.string_array_offset)
                self._string_array = self._read_node(reader)
            # Read the optional path array, holding paths referenced by index in path nodes.
            if header.path_array_offset:
                reader.seek(header.path_array_offset)
                self._path_array = self._read_node(reader)
            # Read the root node.
            reader.seek(header.root_offset)
            self.root = self._read_node(reader)
        return self

    def load_root(self, root):
        pass

    def save_raw(self, raw):
        with binary_io.BinaryWriter(raw) as writer:
            writer.endianness = ">"
            # Write the header.
            writer.write_raw_string("BY")
            writer.write_uint16(0x0001)

    def _read_node(self, reader, node_type=None):
        # Read the node type if it has not been provided yet.
        node_type_given = bool(node_type)
        if not node_type_given:
            node_type = reader.read_byte()
        if NodeType.Array <= node_type <= NodeType.PathArray:
            # Get the length of arrays.
            old_pos = None
            if node_type_given:
                # If the node type was given, the array value is read from an offset.
                offset = reader.read_uint32()
                old_pos = reader.tell()
                reader.seek(offset)
            else:
                reader.seek(-1, io.SEEK_CUR)
            length = reader.read_uint32() & 0x00FFFFFF
            if   node_type == NodeType.Array:       value = self._read_array(reader, length)
            elif node_type == NodeType.Dictionary:  value = self._read_dictionary(reader, length)
            elif node_type == NodeType.StringArray: value = self._read_string_array(reader, length)
            elif node_type == NodeType.PathArray:   value = self._read_path_array(reader, length)
            else: raise AssertionError("Unknown node type " + str(node_type) + ".")
            # Seek back to the previous position if this was a value positioned at an offset.
            if old_pos:
                reader.seek(old_pos)
            return value
        else:
            # Read the following uint32 representing the value directly.
            if   node_type == NodeType.StringIndex: return self._read_string(reader)
            elif node_type == NodeType.PathIndex:   return self._read_path(reader)
            elif node_type == NodeType.Boolean:     return self._read_boolean(reader)
            elif node_type == NodeType.Integer:     return self._read_integer(reader)
            elif node_type == NodeType.Float:       return self._read_float(reader)
            else: raise AssertionError("Unknown node type " + str(node_type) + ".")

    def _read_array(self, reader, length):
        # Read the element types of the array.
        node_types = reader.read_bytes(length)
        # Read the elements, which begin after a padding to the next 4 bytes.
        reader.seek(-reader.tell() % 4, io.SEEK_CUR)
        value = []
        for i in range(0, length):
            value.append(self._read_node(reader, node_types[i]))
        return value

    def _read_dictionary(self, reader, length):
        value = {}
        # Read the elements of the dictionary.
        for i in range(0, length):
            idx_and_type = reader.read_uint32()
            node_name_index = idx_and_type >> 8 & 0xFFFFFFFF
            node_type = idx_and_type & 0x000000FF
            node_name = self._name_array[node_name_index]
            value[node_name] = self._read_node(reader, node_type)
        return value

    def _read_string_array(self, reader, length):
        value = StringArray()
        node_offset = reader.tell() - 4  # String offsets are relative to the start of this node.
        # Read the element offsets.
        offsets = reader.read_uint32s(length)
        # Read the strings by seeking to their element offset and then back.
        old_position = reader.tell()
        for i in range(0, length):
            reader.seek(node_offset + offsets[i])
            value.append(reader.read_0_string())
        reader.seek(old_position)
        return value

    def _read_path_array(self, reader, length):
        value = PathArray()
        node_offset = reader.tell() - 4 # Path offsets are relative to the start of this node.
        # Read the element offsets.
        offsets = reader.read_uint32s(length + 1)
        # Read the paths by seeking to their element offset and then back.
        old_position = reader.tell()
        for i in range(0, length):
            reader.seek(node_offset + offsets[i])
            point_count = (offsets[i + 1] - offsets[i]) // 0x1C
            value.append(Path.from_file(reader, point_count))
        reader.seek(old_position)
        return value

    def _read_string(self, reader):
        return self._string_array[reader.read_uint32()]

    def _read_path(self, reader):
        return self._path_array[reader.read_uint32()]

    def _read_boolean(self, reader):
        return reader.read_uint32() != 0

    def _read_integer(self, reader):
        return reader.read_int32()

    def _read_float(self, reader):
        return reader.read_single()

class Header:
    def __init__(self):
        self.name_array_offset = None
        self.string_array_offset = None
        self.path_array_offset = None
        self.root_offset = None

    @staticmethod
    def from_file(reader):
        self = Header()
        if reader.read_raw_string(2) != "BY":
            raise AssertionError("Invalid BYAML header.")
        if reader.read_uint16() != 0x0001:
            raise AssertionError("Unsupported BYAML version.")
        self.name_array_offset = reader.read_uint32()
        self.string_array_offset = reader.read_uint32()
        self.path_array_offset = reader.read_uint32()
        self.root_offset = reader.read_uint32()
        return self

class NodeType(enum.IntEnum):
    StringIndex = 0xA0, # 160, mapped to str
    PathIndex   = 0xA1, # 161, mapped to Path
    Array       = 0xC0, # 192, mapped to []
    Dictionary  = 0xC1, # 193, mapped to {}
    StringArray = 0xC2, # 194, mapped to StringArray
    PathArray   = 0xC3, # 195, mapped to PathArray
    Boolean     = 0xD0, # 208, mapped to bool
    Integer     = 0xD1, # 209, mapped to int
    Float       = 0xD2  # 210, mapped to float

class Path:
    @staticmethod
    def from_file(reader, point_count):
        self = Path()
        self.points = []
        for i in range(0, point_count):
            self.points.append(PathPoint.from_file(reader))
        return self

    def __init__(self):
        self.points = None

    def __delitem__(self, key):
        del self.points[key]

    def __getitem__(self, item):
        return self.points[item]

    def __setitem__(self, key, value):
        self.points[key] = value

    def __len__(self):
        return len(self.points)

    def __iter__(self):
        return iter(self.points)

    def __repr__(self):
        return str(self)

    def __str__(self):
        return str(self.points)

class PathPoint:
    @staticmethod
    def from_file(reader):
        self = PathPoint()
        self.position = reader.read_vector_3d()
        self.normal = reader.read_vector_3d()
        self.unknown = reader.read_uint32()
        return self

    def __init__(self):
        self.position = None
        self.normal = None
        self.unknown = None

class Array:
    def __delitem__(self, key):
        del self._elements[key]

    def __getitem__(self, item):
        return self._elements[item]

    def __init__(self, element_type):
        self._element_type = element_type
        self._elements = []

    def __iter__(self):
        return iter(self._elements)

    def __len__(self):
        return len(self._elements)

    def __repr__(self):
        return str(self._elements)

    def __setitem__(self, key, value):
        if self._check_type(value):
            self._elements[key] = value

    def __str__(self):
        return str(self._elements)

    def append(self, x):
        if self._check_type(x):
            self._elements.append(x)

    def _check_type(self, x):
        if isinstance(x, self._element_type):
            return True
        else:
            raise TypeError("Expected "+ self._element_type.__name__ + ", not " + type(x).__name__)

class StringArray(Array):
    def __init__(self):
        super().__init__(str)

class PathArray(Array):
    def __init__(self):
        super().__init__(Path)

import enum
import io
import mathutils
from . import binary_io

class File:
    def __init__(self):
        self._name_array = None
        self._string_array = None
        self._path_array = None
        self.root = None

    def load_raw(self, raw):
        # Open a big-endian binary reader on the stream.
        with binary_io.BinaryReader(raw) as reader:
            reader.endianness = ">"
            header = Header.load(reader)
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

    def save_raw(self, raw):
        # Prepare the node name, string and path arrays.
        names = []
        strings = []
        paths = []
        self._prepare_export(self.root, names, strings, paths)
        names = list(set(names))
        strings = list(set(strings))
        names.sort()
        strings.sort()
        self._name_array = StringArray(names)
        self._string_array = StringArray(strings)
        self._path_array = PathArray(paths)
        # Write the file.
        with binary_io.BinaryWriter(raw) as writer:
            writer.endianness = ">"
            # Write the header.
            writer.write_raw_string("BY")
            writer.write_uint16(0x0001)
            name_array_offset = writer.reserve_offset()
            string_array_offset = writer.reserve_offset()
            path_array_offset = writer.reserve_offset()
            root_offset = writer.reserve_offset()
            # Write the main nodes.
            self._write_value_contents(writer, name_array_offset, self._name_array)
            if len(self._string_array):
                self._write_value_contents(writer, string_array_offset, self._string_array)
            else:
                writer.write_uint32(0)
            if len(self._path_array):
                self._write_value_contents(writer, path_array_offset, self._path_array)
            else:
                writer.write_uint32(0)
            self._write_value_contents(writer, root_offset, self.root)

    # ---- Read ----

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
            if   node_type == NodeType.StringIndex: return self._read_string_index(reader)
            elif node_type == NodeType.PathIndex:   return self._read_path_index(reader)
            elif node_type == NodeType.Boolean:     return self._read_boolean(reader)
            elif node_type == NodeType.Integer:     return self._read_integer(reader)
            elif node_type == NodeType.Float:       return self._read_float(reader)
            else: raise AssertionError("Unknown node type " + str(node_type) + ".")

    def _read_string_index(self, reader):
        return self._string_array[reader.read_uint32()]

    def _read_path_index(self, reader):
        return self._path_array[reader.read_uint32()]

    def _read_array(self, reader, length):
        # Read the element types of the array.
        node_types = reader.read_bytes(length)
        # Read the elements, which begin after a padding to the next 4 bytes.
        reader.align(4)
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
            length = (offsets[i + 1] - offsets[i]) // 0x1C
            value.append(self._read_path(reader, length))
        reader.seek(old_position)
        return value

    def _read_path(self, reader, length):
        value = Path()
        for i in range(0, length):
            value.append(self._read_path_point(reader))
        return value

    def _read_path_point(self, reader):
        value = PathPoint()
        value.position = mathutils.Vector(reader.read_singles(3))
        value.normal = mathutils.Vector(reader.read_singles(3))
        value.unknown = reader.read_uint32()
        return value

    def _read_boolean(self, reader):
        return reader.read_uint32() != 0

    def _read_integer(self, reader):
        return reader.read_int32()

    def _read_float(self, reader):
        return reader.read_single()

    # ---- Write ----

    def _prepare_export(self, value, names, strings, paths):
        if isinstance(value, str):
            strings.append(value)
        elif isinstance(value, Path):
            paths.append(value)
        elif isinstance(value, list):
            for val in value:
                self._prepare_export(val, names, strings, paths)
        elif isinstance(value, dict):
            for key, val in sorted(value.items()): # Dictionaries need to be sorted.
                names.append(key)
                self._prepare_export(val, names, strings, paths)

    def _write_value(self, writer, value):
        # Only reserve and return an offset for the complex value contents, write simple or main values directly.
        if   isinstance(value, str):         self._write_string_index(writer, value)
        elif isinstance(value, Path):        self._write_path_index(writer, value)
        elif isinstance(value, list):        return writer.reserve_offset()
        elif isinstance(value, dict):        return writer.reserve_offset()
        elif isinstance(value, StringArray): self._write_string_array(writer, value)
        elif isinstance(value, PathArray):   self._write_path_array(writer, value)
        elif isinstance(value, bool):        self._write_boolean(writer, value)
        elif isinstance(value, int):         self._write_integer(writer, value)
        elif isinstance(value, float):       self._write_float(writer, value)
        else: raise TypeError("Expected BYAML compatible value type, not " + type(value).__name__)

    def _write_value_contents(self, writer, offset, value):
        # Satisfy the offset to the complex value which must be 4-byte aligned.
        writer.align(4)
        writer.satisfy_offset(offset)
        # Write the value contents.
        if   isinstance(value, list):        self._write_array(writer, value)
        elif isinstance(value, dict):        self._write_dictionary(writer, value)
        elif isinstance(value, StringArray): self._write_string_array(writer, value)
        elif isinstance(value, PathArray):   self._write_path_array(writer, value)
        else: raise TypeError("Expected complex value type, not " + type(value).__name__)

    def _write_type_and_length(self, writer, node_type, length):
        value = node_type << 24
        value |= length
        writer.write_uint32(value)

    def _write_string_index(self, writer, value):
        writer.write_uint32(self._string_array.index(value))

    def _write_path_index(self, writer, value):
        writer.write_uint32(self._path_array.index(value))

    def _write_array(self, writer, value):
        self._write_type_and_length(writer, NodeType.Array, len(value))
        # Write the element types.
        for element in value:
            writer.write_byte(NodeType.get_type(element))
        # Write the elements, which begin after a padding to the next 4 bytes.
        writer.align(4)
        offsets = []
        for element in value:
            offsets.append(self._write_value(writer, element))
        # Write the contents of complex nodes, and satisfy the offsets.
        for offset, element in zip(offsets, value):
            if offset:
                self._write_value_contents(writer, offset, element)

    def _write_dictionary(self, writer, value):
        self._write_type_and_length(writer, NodeType.Dictionary, len(value))
        # Write the key-value pairs.
        offsets = []
        for key, val in sorted(value.items()): # Dictionaries need to be sorted.
            # Get the index of the key string in the file's name array and the type of the value.
            key_index = self._name_array.index(key)
            val_type = NodeType.get_type(val)
            writer.write_uint32(key_index << 8 | val_type)
            # Write the elements.
            offsets.append(self._write_value(writer, val))
        # Write the value contents.
        for offset, val in zip(offsets, sorted(value.items())): # Dictionaries need to be sorted.
            if offset:
                self._write_value_contents(writer, offset, val[1]) # Stupid solution to access value of now-tuples.

    def _write_string_array(self, writer, value):
        writer.align(4)
        self._write_type_and_length(writer, NodeType.StringArray, len(value))
        # Write the offsets to the strings, where the last one points to the end of the last string.
        offset = 4 + 4 * (len(value) + 1) # Relative to node start + all uint32 offsets.
        for string in value:
            writer.write_uint32(offset)
            offset += len(string) + 1
        writer.write_uint32(offset)
        # Write the 0-terminated strings.
        for string in value:
            writer.write_0_string(string)

    def _write_path_array(self, writer, value):
        writer.align(4)
        self._write_type_and_length(writer, NodeType.PathArray, len(value))
        # Write the offsets to the paths, where the last one points to the end of the last path.
        offset = 4 + 4 * (len(value) + 1)  # Relative to node start + all uint32 offsets.
        for path in value:
            writer.write_uint32(offset)
            offset += len(path) * 28 # 28 bytes are required for a single point.
        writer.write_uint32(offset)
        # Write the paths.
        for path in value:
            self._write_path(writer, path)

    def _write_path(self, writer, path):
        for point in path:
            self._write_path_point(writer, point)

    def _write_path_point(self, writer, point):
        writer.write_singles(point.position)
        writer.write_singles(point.normal)
        writer.write_uint32(point.unknown)

    def _write_boolean(self, writer, value):
        writer.write_uint32(1 if value else 0)

    def _write_integer(self, writer, value):
        writer.write_int32(value)

    def _write_float(self, writer, value):
        writer.write_single(value)

class Header:
    def __init__(self):
        self.name_array_offset = None
        self.string_array_offset = None
        self.path_array_offset = None
        self.root_offset = None

    @staticmethod
    def load(reader):
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

    @staticmethod
    def get_type(node):
        if   isinstance(node, str):         return NodeType.StringIndex
        elif isinstance(node, Path):        return NodeType.PathIndex
        elif isinstance(node, list):        return NodeType.Array
        elif isinstance(node, dict):        return NodeType.Dictionary
        elif isinstance(node, StringArray): return NodeType.StringArray
        elif isinstance(node, PathArray):   return NodeType.PathArray
        elif isinstance(node, bool):        return NodeType.Boolean
        elif isinstance(node, int):         return NodeType.Integer
        elif isinstance(node, float):       return NodeType.Float
        else: raise TypeError("Expected BYAML compatible node type, not " + type(node).__name__)

class Array:
    def __delitem__(self, key):
        del self._elements[key]

    def __eq__(self, other):
        if isinstance(other, self.__class__) and len(other) == len(self):
            for element, other_element in zip(self, other):
                if element != other_element:
                    return False
        return True

    def __getitem__(self, item):
        return self._elements[item]

    def __init__(self, element_type, elements=None):
        self._element_type = element_type
        self._elements = []
        if elements:
            self.extend(elements)

    def __iter__(self):
        return iter(self._elements)

    def __len__(self):
        return len(self._elements)

    def __ne__(self, other):
        return not self.__eq__(other)

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

    def extend(self, x):
        for elem in x:
            self._check_type(elem)
            self.append(elem)

    def index(self, x):
        self._check_type(x)
        return self._elements.index(x)

    def _check_type(self, x):
        if isinstance(x, self._element_type):
            return True
        else:
            raise TypeError("Expected "+ self._element_type.__name__ + ", not " + type(x).__name__)

class StringArray(Array):
    def __init__(self, elements=None):
        super().__init__(str, elements)

class PathArray(Array):
    def __init__(self, elements=None):
        super().__init__(Path, elements)

class Path(Array):
    def __init__(self):
        super().__init__(PathPoint)

class PathPoint:
    def __eq__(self, other):
        return isinstance(other, self.__class__)\
            and self.position == other.position\
            and self.normal == other.normal\
            and self.unknown == other.unknown

    def __init__(self):
        self.position = None
        self.normal = None
        self.unknown = None

    def __ne__(self, other):
        return not self.__eq__(other)

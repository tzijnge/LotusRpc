from typing import Any, Dict

class LrpcVar(object):
    def __init__(self, raw) -> None:
        self.raw = raw
        self.__pack_type: Dict[str, str] = {
            'uint8_t': 'B',
            'int8_t': 'b',
            'uint16_t': 'H',
            'int16_t': 'h',
            'uint32_t': 'I',
            'int32_t': 'i',
            'uint64_t': 'Q',
            'int64_t': 'q',
            'float': 'f',
            'double': 'd',
            'bool': '?'
        }

        if 'count' not in self.raw:
            self.raw['count'] = 1
        if 'base_type_is_struct' not in self.raw:
            self.raw['base_type_is_struct'] = False
        if 'base_type_is_enum' not in self.raw:
            self.raw['base_type_is_enum'] = False

    def name(self):
        return self.raw['name']

    def base_type(self) -> str:
        return self.raw['type'].strip('@')

    def field_type(self):
        t = self.base_type()
        if self.base_type_is_string():
            t = f'etl::string<{self.string_size()}>'

        if self.is_optional():
            return f'etl::optional<{t}>'

        if self.is_array():
            s = self.array_size()
            return f'etl::array<{t}, {s}>'

        return t

    def return_type(self):
        t = self.base_type()

        if self.base_type_is_string():
            t = f'etl::string<{self.string_size()}>'

        if self.is_optional():
            return f'etl::optional<{t}>'

        if self.is_array():
            return f'etl::array<{t}, {self.array_size()}>'

        return t

    def param_type(self):
        if self.base_type_is_string():
            t = 'etl::string_view'
        else:
            t = self.base_type()

        if self.is_array():
            return f'const etl::span<const {t}>&'
        elif self.is_optional():
            return f'const etl::optional<{t}>&'
        else:
            if self.base_type_is_struct() or self.base_type_is_string():
                return f'const {t}&'
            else:
                return t

    def read_type(self):
        if self.base_type_is_string():
            if self.is_fixed_size_string():
                s = self.string_size()
                t = f'etl::string<{s}>'
            else:
                t = 'etl::string_view'
        else:
            t = self.base_type()

        if self.is_array():
            return f'etl::array<{t}, {self.array_size()}>'
        elif self.is_optional():
            return f'etl::optional<{t}>'
        else:
            return t

    def write_type(self):
        t = self.base_type()

        if self.base_type_is_string():
            t = f'etl::string<{self.string_size()}>'

        if self.is_array():
            return f'etl::array<{t}, {self.array_size()}>'
        
        if self.is_optional():
            return f'etl::optional<{t}>'

        return t

    def base_type_is_custom(self) -> bool:
        return '@' in self.raw['type']

    def base_type_is_struct(self) -> bool:
        return self.raw['base_type_is_struct']

    def base_type_is_enum(self) -> bool:
        return self.raw['base_type_is_enum']

    def base_type_is_integral(self) -> bool:
        return self.base_type() in ['uint8_t', 'uint16_t', 'uint32_t', 'uint64_t', 'int8_t', 'int16_t', 'int32_t', 'int64_t']

    def base_type_is_float(self) -> bool:
        return self.base_type() in ['float', 'double']

    def base_type_is_bool(self) -> bool:
        return self.base_type() == 'bool'

    def base_type_is_string(self) -> bool:
        return self.base_type().startswith('string')

    def is_struct(self) -> bool:
        if self.is_array():
            return False
        if self.is_optional():
            return False

        return self.base_type_is_struct()

    def is_optional(self) -> bool:
        count = self.raw['count']
        return isinstance(count, str) and count == '?'

    def is_array(self) -> bool:
        if self.is_optional():
            return False

        return self.raw['count'] > 1

    def is_array_of_strings(self) -> bool:
        return self.is_array() and self.base_type_is_string()

    def is_string(self) -> bool:
        if self.is_array():
            return False

        if self.is_optional():
            return False

        return self.base_type_is_string()

    def is_auto_string(self) -> bool:
        return self.base_type() == 'string'
    
    def is_fixed_size_string(self) -> bool:
        return self.base_type_is_string() and not self.is_auto_string()

    def string_size(self) -> int:
        if self.is_auto_string():
            return -1

        return int(self.base_type().strip('string_'))

    def array_size(self) -> int:
        if self.is_optional():
            return -1

        return int(self.raw['count'])

    def pack_type(self) -> str:
        return self.__pack_type[self.base_type()]

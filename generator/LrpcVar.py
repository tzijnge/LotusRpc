class LrpcVar(object):
    def __init__(self, raw) -> None:
        self.raw = raw
        if 'count' not in self.raw:
            self.raw['count'] = 1

    def name(self):
        return self.raw['name']

    def base_type(self):
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

        if self.is_string():
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
        if self.is_string():
            return f'etl::istring'

        t = self.base_type()
        if self.is_array():
            return f'etl::array<{t}, {self.array_size()}>'
        
        if self.is_optional():
            return f'etl::optional<{t}>'

        return t

    def base_type_is_custom(self):
        return '@' in self.raw['type']

    def base_type_is_struct(self):
        return self.raw['base_type_is_struct']

    def base_type_is_enum(self):
        return self.raw['base_type_is_enum']

    def base_type_is_integral(self):
        return self.base_type() in ['uint8_t', 'uint16_t', 'uint32_t', 'uint64_t', 'int8_t', 'int16_t', 'int32_t', 'int64_t']

    def base_type_is_string(self):
        return self.base_type().startswith('string_')

    def is_struct(self):
        if self.is_array():
            return False
        if self.is_optional():
            return False

        return self.base_type_is_struct()

    def is_optional(self):
        count = self.raw['count']
        return isinstance(count, str) and count == '?'

    def is_array(self):
        if self.is_optional():
            return False

        return self.raw['count'] > 1

    def is_array_of_strings(self):
        return self.is_array() and self.base_type_is_string()

    def is_string(self):
        if self.is_array():
            return False

        if self.is_optional():
            return False

        return self.base_type_is_string()

    def is_auto_string(self):
        return self.base_type() == 'string_auto'
    
    def is_fixed_size_string(self):
        return self.base_type_is_string() and not self.is_auto_string()

    def string_size(self):
        if self.is_auto_string():
            return -1

        return int(self.base_type().strip('string_'))

    def array_size(self):
        if self.is_optional():
            return -1

        return int(self.raw['count'])

    def required_includes(self):
        includes = set()

        if self.base_type_is_integral():
            includes.update({'<stdint.h>'})

        if self.base_type_is_custom():
            includes.update({f'"{self.base_type()}.hpp"'})

        if self.base_type_is_string():
            includes.update({'<etl/string.h>', '<etl/string_view.h>'})

        if self.is_array():
            includes.update({'<etl/span.h>'})

        if self.is_optional():
            includes.update({'<etl/optional.h>'})

        return includes
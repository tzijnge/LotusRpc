class LrpcVar(object):
    def __init__(self, raw, structs) -> None:
        self.structs = structs
        self.raw = raw
        self.raw['type'] = self.raw['type'].strip('@')
        if 'count' not in self.raw:
            self.raw['count'] = 1

    def name(self):
        return self.raw['name']

    def field_type(self):
        t = self.raw['type']
        if self.is_string():
            t = f'etl::string<{self.string_size()}>'

        if self.is_optional():
            return f'etl::optional<{t}>'

        if self.is_array():
            s = self.array_size()
            return f'etl::array<{t}, {s}>'

        return t

    def return_type(self):
        t = 'etl::string_view' if self.is_string() else self.raw['type']

        if self.is_optional():
            return f'etl::optional<{t}>'

        if self.is_array():
            return f'etl::span<const {t}>'

        return t

    def param_type(self):
        if self.is_string():
            t = 'const etl::string_view&'
        elif self.is_struct():
            t = 'const ' + self.raw['type'] + '&'
        else:
            t = self.raw['type']

        if self.is_optional():
            return f'const etl::optional<{t}>&'

        if self.is_array():
            return f'const etl::span<const {t}>&'

        return t

    def read_type(self):
        return 'etl::string_view' if self.is_string() else self.raw['type']

    def write_type(self):
        t = 'etl::string_view' if self.is_string() else self.raw['type']

        if self.is_array():
            return f'const {t}'

        return t

    def is_struct(self):
        if self.is_array():
            return False

        if self.is_optional():
            return False

        struct_names = [s['name'] for s in self.structs]
        return self.raw['type'] in struct_names

    def is_optional(self):
        return self.raw['count'] == '*'

    def is_array(self):
        if self.is_optional():
            return False

        return self.raw['count'] > 1

    def is_array_of_strings(self):
        return self.is_array() and self.__base_type_is_string()

    def is_string(self):
        if self.is_array():
            return False

        if self.is_optional():
            return False

        return self.__base_type_is_string()

    def is_auto_string(self):
        return self.raw['type'] == 'string_auto'

    def string_size(self):
        if self.is_auto_string():
            return -1

        return int(self.raw['type'].strip('string_'))

    def array_size(self):
        if self.is_optional():
            return -1

        return int(self.raw['count'])

    def required_includes(self):
        if self.is_array_of_strings():
            return {'<etl/string_view.h>', '<etl/span.h>'}

        if self.is_array():
            return {'<etl/span.h>'}

        if self.is_string():
            return {'<etl/string_view.h>'}

        return {}

    def __base_type_is_string(self):
        return self.raw['type'].startswith('string_')
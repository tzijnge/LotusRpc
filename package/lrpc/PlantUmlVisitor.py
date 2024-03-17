from lrpc.LrpcVisitor import LrpcVisitor
from lrpc.core import *
from contextlib import contextmanager

def in_color(t: str, c: str):
    return f'<color:{c}>{t}</color>'

class FunctionStringBuilder(object):
    def __init__(self, max_function_id: int) -> None:
        self.param_strings = list()
        self.return_strings = list()
        self.function_name = ''
        self.function_id = ''
        self.id_width = len(str(max_function_id))

    def add_function(self, function: LrpcFun) -> None:
        self.function_name = function.name()
        self.function_id = f'{function.id()}'.rjust(self.id_width)

    def add_param(self, param: LrpcVar) -> None:
        self.param_strings.append(var_string(param))

    def add_return(self, ret: LrpcVar) -> None:
        self.return_strings.append(var_string(ret))

def var_string(p: LrpcVar) -> str:
    t = in_color(p.base_type(), 'DarkCyan')
    if p.base_type_is_string():
        if p.is_auto_string():
            t = in_color('string', 'DarkCyan')
        else:
            t = in_color('string', 'DarkCyan') + '<' + in_color(f'{p.string_size()}', 'ForestGreen') + '>'

    if p.is_optional():
        t = in_color('optional', 'DarkCyan') + f'<{t}>'

    if p.is_array():
        t = in_color('array', 'DarkCyan') + f'<{t}, ' + in_color(p.array_size(), 'ForestGreen') + '>'

    return t + ' ' + in_color(p.name(), 'CornflowerBlue')

def enum_field_string(e: LrpcEnumField) -> str:
    name = in_color(e.name(), 'CornflowerBlue')
    id = in_color(e.id(), 'ForestGreen')
    return f'{name} = {id}'

def const_string(p: LrpcConstant) -> str:
    t = in_color(p.cpp_type(), 'DarkCyan')
    n = in_color(p.name(), 'CornflowerBlue')
    return t + ' ' + n
    
class PumlFile(object):
    def __init__(self, filename: str) -> None:
        self.text = '@startmindmap\n'
        self.filename = filename

    def write(self, t: str) -> None:
        self.text += t

    @contextmanager
    def font(self, f: str):
        self.write(f'<font:{f}>')
        yield
        self.write('</font>')

    @contextmanager
    def color(self, c: str):
        self.write(f'<color:{c}>')
        yield
        self.write('</color>')

    @contextmanager
    def size(self, s: str):
        self.write(f'<size:{s}>')
        yield
        self.write('</size>')

    @contextmanager
    def bold(self):
        self.write('**')
        yield
        self.write('**')

    @contextmanager
    def enclosed_in(self, open: str, close: str):
        self.write(open)
        yield
        self.write(close)

    def icon(self, i: str) -> None:
        self.write(f'<&{i}>')

    def legend(self, items, size: int) -> None:
        self.write('legend left\n')

        for (color, icon, text) in items:
            with self.size(size):
                with self.color(color):
                    self.icon(icon)
                self.write(' ' + text)

            self.write('\n')

        self.write('endlegend\n')

    def block(self, name: str, background: str, level: int, icon: str = None) -> None:
        indent = '*' * level
        self.write(f'{indent}[#{background}]: ')
        if icon:
            self.icon(icon)
            self.write(' ')

        with self.bold():
            self.write(name)

        self.write('\n----')

    def list_item(self, text: str, level: int = 1, font: str = None) -> None:
        indent = '*' * level
        if level != 0:
            indent += ' '
        self.write(f'\n{indent}')
        if font:
            with self.font(font):
                self.write(text)
        else:
            self.write(text)

    def list_end(self) -> None:
        self.write(';\n')

    def dump_to_file(self) -> None:
        self.write('\n@endmindmap')
        with open(self.filename, 'w') as file:
            file.write(self.text)
    
    def function_string(self, fsb: FunctionStringBuilder) -> None:
        with self.font('monospaced'):
            with self.enclosed_in('[', ']'):
                with self.color('Orange'):
                    self.write(f'{fsb.function_id}')
                    self.write(' ')
                    self.icon('transfer')
            with self.bold():
                self.write(fsb.function_name)
            with self.color('Magenta'):
                self.write('(')
            self.write(', '.join(fsb.param_strings))
            with self.color('Magenta'):
                self.write(')')
            with self.color('Orange'):
                self.icon('arrow-right')
            with self.color('Magenta'):
                self.write(' (')
            self.write(', '.join(fsb.return_strings))
            with self.color('Magenta'):
                self.write(')')

class PlantUmlVisitor(LrpcVisitor):
    def __init__(self, output: str) -> None:
        self.output = output
        self.fsb = None
        self.puml = None
        self.max_function_id = 0
        
        self.enum_fields = list()
        self.enum_indent = 2
        self.enum_indent_max = 7
        self.enum_fields_max = 10
        self.struct_indent = 2
        
        self.struct_indent_max = 7
        self.struct_fields = list()
        self.struct_fields_max = 10
        
        self.constants = list()
        self.const_items_max = 10

    def visit_lrpc_def(self, lrpc_def: LrpcDef):
        self.puml = PumlFile(f'{self.output}/{lrpc_def.name()}.puml')

        self.puml.block(lrpc_def.name(), 'Yellow', level=1)
        self.puml.list_item(f'Namespace: {lrpc_def.namespace()}', level=0)
        self.puml.list_item(f'RX buffer size: {lrpc_def.rx_buffer_size()}', level=0)
        self.puml.list_item(f'TX Buffer size: {lrpc_def.tx_buffer_size()}', level=0)
        self.puml.list_end()
    
    def visit_lrpc_def_end(self):
        self.puml.write('\n')

        legend_items = [
            ['Yellow', 'medical-cross', 'Server'],
            ['PeachPuff', 'medical-cross', 'Services'],
            ['Blue', 'medical-cross', 'Structs'],
            ['PaleGreen', 'medical-cross', 'Enums'],
            ['Pink', 'medical-cross', 'Constants'],
            ['Black', 'external-link', 'External'],
            ['Black', 'transfer', 'Two-way function'],
        ]
        self.puml.legend(legend_items, 20)

        self.puml.dump_to_file()

    def visit_lrpc_constants(self):
        self.puml.block('Constants', 'Pink', 2)
        self.constants = list()

    def visit_lrpc_constant(self, constant: LrpcConstant):
        self.constants.append(constant)

    def visit_lrpc_constants_end(self):
        const_strings = [const_string(c) for c in self.constants[0:self.const_items_max]]
        if len(self.constants) > self.const_items_max:
            const_strings.append('...')

        for c in const_strings:
            self.puml.list_item(c, font='monospaced')

        self.puml.list_end()

    def visit_lrpc_enum(self, enum: LrpcEnum):
        icon = 'external-link' if enum.is_external() else None
        self.puml.block(enum.name(), 'PaleGreen', self.enum_indent, icon)

    def visit_lrpc_enum_end(self):
        enum_field_strings = [enum_field_string(ef) for ef in self.enum_fields[0:self.enum_fields_max]]
        if len(self.enum_fields) > self.enum_fields_max:
            enum_field_strings.append('...')

        for s in enum_field_strings:
            self.puml.list_item(s, font='monospaced')
        
        self.puml.list_end()
        
        self.enum_indent = self.enum_indent + 1
        if self.enum_indent > self.enum_indent_max:
            self.enum_indent = 2

    def visit_lrpc_enum_field(self, field: LrpcEnumField):
        self.enum_fields.append(field)

    def visit_lrpc_function(self, function: LrpcFun):
        self.fsb = FunctionStringBuilder(self.max_function_id)
        self.fsb.add_function(function)
        
    def visit_lrpc_function_end(self):
        self.puml.write('***_ ')
        self.puml.function_string(self.fsb)
        self.puml.write('\n')
    
    def visit_lrpc_function_param(self, param: LrpcVar):
        self.fsb.add_param(param)
    
    def visit_lrpc_function_param_end(self):
        return super().visit_lrpc_function_param_end()
    
    def visit_lrpc_function_return(self, ret: LrpcVar):
        self.fsb.add_return(ret)

    def visit_lrpc_function_return_end(self):
         return super().visit_lrpc_function_return_end()

    def visit_lrpc_service(self, service: LrpcService):
        self.puml.block(service.name(), 'PeachPuff', 2)
        self.puml.list_item(f'ID: {service.id()}', level=0)
        self.puml.list_end()

        self.max_function_id = max([f.id() for f in service.functions()])

    def visit_lrpc_service_end(self):
        return super().visit_lrpc_service_end()
    
    def visit_lrpc_struct(self, struct: LrpcStruct):
        self.struct_fields = list()
        icon = 'external-link' if struct.is_external() else None
        self.puml.block(struct.name(), 'lightblue', self.struct_indent, icon)

    def visit_lrpc_struct_end(self):
        struct_field_strings = [var_string(sf) for sf in self.struct_fields[0:self.struct_fields_max]]
        if len(self.struct_fields) > self.struct_fields_max:
            struct_field_strings.append('...')

        for s in struct_field_strings:
            self.puml.list_item(s, font='monospaced')
        
        self.puml.list_end()
        
        self.struct_indent = self.struct_indent + 1
        if self.struct_indent > self.struct_indent_max:
            self.struct_indent = 2

    def visit_lrpc_struct_field(self, field: LrpcVar):
        self.struct_fields.append(field)
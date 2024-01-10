class LrpcConstant(object):
    def __init__(self, raw) -> None:
        self.raw = raw
        self.__init_cpp_type()
        self.__init_local()

    def __init_cpp_type(self):
        if "cppType" not in self.raw:
            if isinstance(self.value(), int):
                self.raw["cppType"] = "int32_t"
            if isinstance(self.value(), float):
                self.raw["cppType"] = "float"
            if isinstance(self.value(), bool):
                self.raw["cppType"] = "bool"

    def __init_local(self):
        if "local" not in self.raw:
            self.raw["local"] = False

    def name(self):
        return self.raw['name']

    def value(self):
        return self.raw['value']
    
    def local(self):
        return self.raw['local']

    def cpp_type(self):
        return self.raw['cppType']

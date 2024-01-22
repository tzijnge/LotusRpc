from LrpcStruct import LrpcStruct

def test_minimal_notation():
  s = {
    "name": "MyStruct",
    "fields": [
      {"name": "f1", "type": "uint64_t"},
      {"name": "f2", "type": "bool"},
    ]
    }
  
  struct = LrpcStruct(s)

  assert(struct.name() == "MyStruct")
  assert(struct.is_external() == False)
  assert(struct.external_file() == None)
  assert(struct.external_namespace() == None)

  fields = struct.fields()
  assert(len(fields) == 2)
  assert(fields[0].name() == "f1")
  assert(fields[0].base_type() == "uint64_t")
  assert(fields[1].name() == "f2")
  assert(fields[1].base_type() == "bool")

def test_external():
  s = {
    "name": "MyStruct",
    "fields": [ {"name": "f1", "type": "uint64_t"} ],
    "external": "path/to/enum.hpp"
    }
  
  struct = LrpcStruct(s)

  assert(struct.name() == "MyStruct")
  assert(struct.is_external() == True)
  assert(struct.external_file() == "path/to/enum.hpp")
  assert(struct.external_namespace() == None)

def test_external_with_namespace():
  s = {
    "name": "MyStruct",
    "fields": [ {"name": "f1", "type": "uint64_t"} ],
    "external": "path/to/enum.hpp",
    "external_namespace": "path::to",
    }
  
  struct = LrpcStruct(s)

  assert(struct.name() == "MyStruct")
  assert(struct.is_external() == True)
  assert(struct.external_file() == "path/to/enum.hpp")
  assert(struct.external_namespace() == "path::to")
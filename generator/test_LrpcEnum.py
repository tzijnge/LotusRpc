from LrpcEnum import LrpcEnum
import yaml

def test_full_notation():
  e = {
    "name": "MyEnum1",
    "fields": [
      {"name": "f1", "id": 111},
      {"name": "f2", "id": 222},
    ]
    }
  
  enum = LrpcEnum(e)

  assert(enum.name() == "MyEnum1")
  fields = enum.fields()
  assert(len(fields) == 2)
  assert(fields[0].name() == "f1")
  assert(fields[0].id() == 111)
  assert(fields[1].name() == "f2")
  assert(fields[1].id() == 222)

def test_short_notation():
  e = {
    "name": "MyEnum2",
    "fields": [ "f1", "f2" ]
    }
  
  enum = LrpcEnum(e)

  assert(enum.name() == "MyEnum2")
  fields = enum.fields()
  assert(len(fields) == 2)
  assert(fields[0].name() == "f1")
  assert(fields[0].id() == 0)
  assert(fields[1].name() == "f2")
  assert(fields[1].id() == 1)
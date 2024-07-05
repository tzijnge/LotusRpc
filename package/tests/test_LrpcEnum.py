from lrpc.core import LrpcEnum
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

def test_not_external():
  e = {
    "name": "MyEnum2",
    "fields": [ "f1", "f2" ],
    }
  
  enum = LrpcEnum(e)
  assert(enum.is_external() == False)
  assert(enum.external_file() == None)

def test_external():
  e = {
    "name": "MyEnum2",
    "fields": [ "f1", "f2" ],
    "external": "a/b/c/d.hpp"
    }
  
  enum = LrpcEnum(e)
  assert(enum.name() == "MyEnum2")
  assert(enum.is_external() == True)
  assert(enum.external_file() == "a/b/c/d.hpp")
  assert(enum.external_namespace() == None)

def test_external_with_namespace():
  e = {
    "name": "MyEnum2",
    "fields": [ "f1", "f2" ],
    "external": "a/b/c/d.hpp",
    "external_namespace": "ext"
    }
  
  enum = LrpcEnum(e)
  assert(enum.name() == "MyEnum2")
  assert(enum.is_external() == True)
  assert(enum.external_file() == "a/b/c/d.hpp")
  assert(enum.external_namespace() == "ext")


def test_omitted_id():
  e = {
    "name": "MyEnum1",
    "fields": [
      {"name": "f1"},
      {"name": "f2"},
      {"name": "f3", "id": 222},
      {"name": "f4"},
    ]
    }
  
  enum = LrpcEnum(e)

  assert(enum.name() == "MyEnum1")
  fields = enum.fields()
  assert(len(fields) == 4)
  assert(fields[0].name() == "f1")
  assert(fields[0].id() == 0)
  assert(fields[1].name() == "f2")
  assert(fields[1].id() == 1)
  assert(fields[2].name() == "f3")
  assert(fields[2].id() == 222)
  assert(fields[3].name() == "f4")
  assert(fields[3].id() == 223)

def test_field_id():
  e = {
    "name": "MyEnum1",
    "fields": [
      {"name": "f1", "id": 111},
      {"name": "f2", "id": 222},
    ]
    }
  
  enum = LrpcEnum(e)

  assert(enum.field_id('f1') == 111)
  assert(enum.field_id('f2') == 222)
  assert(enum.field_id('f3') is None)
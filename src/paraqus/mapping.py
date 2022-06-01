# -*- coding: utf-8 -*-
"""
Mappers used in Paraqus.

"""

# Todo: Are dicts good enough? Do we really need this? -> possible remove this module...
class Mapper(dict):
    """
    A mapper derived from a dictionary.
    
    The Mapper raises clearer error messages when a key is missing.
    
    """
    def __setitem__(self, key, value):
        super(Mapper, self).__setitem__(key, value)
    
    def __getitem__(self, key):
        return super(Mapper, self).__getitem__(key)

    def __missing__(self, key):
        msg = "Key '{}' is missing in mapper.".format(key)
        raise KeyError(msg)
        


# # Mapper for data types used in vtk files
# VTK_TYPE_MAPPER = Mapper({"int8":    "Int8",
#                           "uint8":   "UInt8",
#                           "int16":   "Int16",
#                           "uint16":  "UInt16",
#                           "int32":   "Int32",
#                           "uint32":  "UInt32",
#                           "int64":   "Int64",
#                           "uint64":  "UInt64",
#                           "float32": "Float32",
#                           "float64": "Float64"
#                           })


# # Mapper for binary data types
# BINARY_TYPE_MAPPER = Mapper({"int8": "b",
#                              "uint8": "B",
#                              "int16": "h",
#                              "uint16": "H",
#                              "int32": "i",
#                              "uint32": "I",
#                              "int64": "q",
#                              "uint64": "Q",
#                              "float32": "f",
#                              "float64": "d"
#                              })


# # Mapper for the header size in case of packed binary data
# BINARY_HEADER_SIZE_MAPPER = Mapper({"uint32": 4,
#                                     "uint64": 8})

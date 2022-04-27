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
        
# TODO: shouldnt the ABQ_CONN_MAPPER live in the abaqus submodule?

# Mapper for Abaqus connectivity lists
# 3:  First-order line (2-node)
# 4:  Second-order line (3-node)
# 5:  First-order tri (3-node)
# 9:  First-order quad (4-node)
# 10: First-order tet (4-node)
# 12: First-order hex (8-node)
# 13: First-order prism (6-node)
# 14: First-order pyramid (5-node)
# 22: Second-order tri (6-node)
# 23: Second-order quad (8-node)
# 24: Second-order tet (10-node)
# 25: Second-order hex (20-node)
# 26: Second-order prism (15-node)
# 28: Bi-quadratic quad (9-node)
ABQ_CONN_MAPPER = Mapper({3:  [1,2],
                          4:  [1,3,2],
                          5:  [1,2,3],
                          9:  [1,2,3,4],
                          10: [1,2,3,4],
                          12: [1,2,3,4,5,6,7,8],
                          13: [1,2,3,4,5,6],
                          14: [1,2,3,4,5],
                          22: [1,2,3,4,5,6],
                          23: [1,2,3,4,5,6,7,8],
                          24: [1,2,3,4,5,6,7,8,9,10],
                          25: [1,2,3,4,5,6,7,8,9,10,11,12,
                               13,14,15,16,17,18,19,20],
                          26: [1,2,3,4,5,6,7,8,9,10,11,12,13,14,15],
                          28: [1,2,3,4,5,6,7,8,9]
                          })


# Mapper for data types used in vtk files
VTK_TYPE_MAPPER = Mapper({"int8":    "Int8",
                          "uint8":   "UInt8",
                          "int16":   "Int16",
                          "uint16":  "UInt16",
                          "int32":   "Int32",
                          "uint32":  "UInt32",
                          "int64":   "Int64",
                          "uint64":  "UInt64",
                          "float32": "Float32",
                          "float64": "Float64"
                          })


# Mapper for binary data types
BINARY_TYPE_MAPPER = Mapper({"int8": "b",
                             "uint8": "B",
                             "int16": "h",
                             "uint16": "H",
                             "int32": "i",
                             "uint32": "I",
                             "int64": "q",
                             "uint64": "Q",
                             "float32": "f",
                             "float64": "d"
                             })


# Mapper for the header size in case of packed binary data
BINARY_HEADER_SIZE_MAPPER = Mapper({"uint32": 4,
                                    "uint64": 8})

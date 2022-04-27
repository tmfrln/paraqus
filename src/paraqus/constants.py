# -*- coding: utf-8 -*-
"""
Collection of constants defined for Paraqus.

The constants are derived from a custom type to make comparisons easierm e.g.
when user input is compared to constants.

"""

import sys

class ParaqusConstant(object):
    """
    A type for named constants.
    
    Parameters
    ----------
    name : str
        Name of the constant, used for comparisons.
        
    Attributes
    ----------
    name : str
        Name of the constant, used for comparisons.
        
    """
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return str(self.name)
    
    def __eq__(self, other):
        if not isinstance(other, ParaqusConstant):
            return str(self.name).upper() == str(other).upper()
        else:
            return self.name == other.name
        
    def __add__(self, other):
        return str(self.name) + str(other) 
    
    def __radd__(self, other):
        return str(other) + str(self.name)
    
    
# Define constants
UINT64 = ParaqusConstant("UINT64")
UINT32 = ParaqusConstant("UINT32")

BINARY = ParaqusConstant("BINARY")
ASCII = ParaqusConstant("ASCII")
BASE64 = ParaqusConstant("BASE64")
RAW = ParaqusConstant("RAW")
LITTLE_ENDIAN = ParaqusConstant("LittleEndian")
BIG_ENDIAN = ParaqusConstant("BigEndian")
BYTE_ORDER = LITTLE_ENDIAN if sys.byteorder == "little" else BIG_ENDIAN
BYTE_ORDER_CHAR = (ParaqusConstant("<") if BYTE_ORDER == LITTLE_ENDIAN 
                   else ParaqusConstant(">"))

ELEMENTS = ParaqusConstant("ELEMENTS")
NODES = ParaqusConstant("NODES")
WHOLE_ELEMENTS = ParaqusConstant("WHOLE_ELEMENTS")

USER = ParaqusConstant("USER")
ABAQUS = ParaqusConstant("ABAQUS")

SCALAR = ParaqusConstant("SCALAR")
VECTOR = ParaqusConstant("VECTOR")
TENSOR = ParaqusConstant("TENSOR")

MEAN = ParaqusConstant("MEAN")
ABSMAX = ParaqusConstant("ABSMAX")
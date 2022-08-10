# -*- coding: utf-8 -*-
#
#   Paraqus - A VTK exporter for FEM results.
#
#   Copyright (C) 2022, Furlan and Stollberg
#
#    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
"""
Collection of constants defined for Paraqus.

The constants are derived from a custom type to make comparisons easier, e.g.
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
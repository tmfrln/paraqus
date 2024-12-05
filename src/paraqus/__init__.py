# -*- coding: utf-8 -*-
#
#   Paraqus - A VTK exporter for FEM results.
#
#   Copyright (C) 2022, Furlan, Stollberg and Menzel
#
#    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.
"""
Export simulation results to VTK format.

"""
import os
import sys

# explicitly reexport the classes below
from paraqus.paraqusmodel import ParaqusModel as ParaqusModel
from paraqus.writers import AsciiWriter as AsciiWriter
from paraqus.writers import BinaryWriter as BinaryWriter
from paraqus.writers import CollectionWriter as CollectionWriter

TESTS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "tests")
sys.path.append(TESTS_PATH)
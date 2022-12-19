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
Example 01 - model creation

This example demonstrates how to create a ParaqusModel instance from scratch.
The model is then written to a vtu file.

"""
# # Uncomment this if you cannot add paraqus to the python path, and set
# # the paraqus source directory for your system
# import sys
# sys.path.append("...")

from paraqus import ParaqusModel, AsciiWriter, BinaryWriter

# specify node tags and corresponding coordinates (2d in this case)
node_tags = [1, 2, 3, 4, 5, 6, 7, 8]

node_coords = [[0, 0],
               [1, 0],
               [2, 0],
               [0, 1],
               [1, 1],
               [2, 1],
               [0.5, 1.5],
               [1.5, 1.5]]

# the element types are chosen based on the vtk specification, see e.g.
# https://vtk.org/wp-content/uploads/2015/04/file-formats.pdf
element_types = [9, 9, 5, 5, 5] # two quads, three triangles

# specify cell tags and the nodes of each cell
element_tags = [1, 2, 3, 4, 5]

connectivity = [[1, 2, 5, 4],
                [2, 3, 6, 5],
                [4, 5, 7],
                [5, 6, 8],
                [5, 8, 7]]


# name of the model - this will be the folder name for the vtu files
model_name = "example_model_01"

# name of the part - this will be the file name for the vtu files
part_name = "example_part_01"

# now we have everything we need to create an instance of ParaqusModel, which
# is the type used to store all model data in paraqus
model = ParaqusModel(element_tags,
                     connectivity,
                     element_types,
                     node_tags,
                     node_coords,
                     model_name=model_name,
                     part_name=part_name)


# create an instance of the AsciiWriter (i.e. the vtu files are human readable)
# we specify the output directory, where paraqus will create subfolders for the
# results
# writer = AsciiWriter(output_dir="vtu_examples")
writer = BinaryWriter(output_dir="vtu_examples")

# write the model to disk
writer.write(model)

# you can now use e.g. paraview to have a look at the vtu file

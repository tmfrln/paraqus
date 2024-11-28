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
Example 02 - field data

This example demonstrates how to add field data to ParaqusModels.

"""
# Uncomment this if you can not add paraqus to the Python path, and set
# the Paraqus source directory for your system
# import sys
# sys.path.append("...")

import numpy as np

from paraqus import ParaqusModel, AsciiWriter


# ======================================================================
#           we start by creating the same model as in example 1
# ======================================================================

# Specify node tags and corresponding coordinates (2d in this case)
node_tags = [1, 2, 3, 4, 5, 6, 7, 8]

node_coords = [[0, 0],
               [1, 0],
               [2, 0],
               [0, 1],
               [1, 1],
               [2, 1],
               [0.5, 1.5],
               [1.5, 1.5]]

# The element types are chosen based on the vtk specification, see e.g.
# https://vtk.org/wp-content/uploads/2015/04/file-formats.pdf
element_types = [9, 9, 5, 5, 5]  # Two quads, three triangles

# specify cell tags and the nodes of each cell
element_tags = [1, 2, 3, 4, 5]

connectivity = [[1, 2, 5, 4],
                [2, 3, 6, 5],
                [4, 5, 7],
                [5, 6, 8],
                [5, 8, 7]]


# Name of the model - this will be the folder name for the vtu files
model_name = "example_model_02"

# Name of the part - this will be the file name for the vtu files
part_name = "example_part_02"

# Now you have everything you need to create an instance of
# ParaqusModel, which is the type used to store all model data in
# Paraqus
model = ParaqusModel(element_tags,
                     connectivity,
                     element_types,
                     node_tags,
                     node_coords,
                     model_name=model_name,
                     part_name=part_name)


# ======================================================================
#             the part different from example 1 starts here :-)
# =======================================================================

# Create a field called u representing the displacement of each node
field_name = "u"
field_tags = node_tags  # Node tags, since we create a node field

# Prescribe x-displacements as 0
ux = np.zeros(len(node_tags))

# Prescribe the y-displacement as 20% of the distance to the origin for
# each node
uy = 0.2*np.linalg.norm(node_coords, axis=1)

# Combine ux and uy into a (number_of_nodes,2) array
field_values = np.vstack((ux, uy)).T

# Specify that you add a node field with vector values
field_position = "nodes"
field_type = "vector"

# Add the field to the model
model.add_field(field_name,
                field_tags,
                field_values,
                field_position,
                field_type)

# Now add a scalar element field called T (representing e.g. a
# temperature)
field_name = "T"
field_tags = element_tags  # these are now the element tags
field_values = [25., 25., 30., 30., 35.]

# Specify that you add an element field with scalar values
field_position = "elements"
field_type = "scalar"

# Add the field to the model
model.add_field(field_name,
                field_tags,
                field_values,
                field_position,
                field_type)


# Create an instance of the AsciiWriter (i.e. the vtu files are human
# readable)
writer = AsciiWriter(output_dir="vtu_examples")

# Write the model to disk
writer.write(model)


# If you open the .vtu file in ParaView, you can use the
# "warp by vector" filter to visualize the displacements

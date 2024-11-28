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
Example 04 - Grouping multiple .vtu files.

This example demonstrates how to combine multiple ParaqusModels which
describe different parts of the same model.

"""
# Uncomment this if you can not add paraqus to the Python path, and set
# the Paraqus source directory for your system
# import sys
# sys.path.append("...")

from paraqus import ParaqusModel, AsciiWriter, CollectionWriter

# Create two simple models that are not connected to each other,
# representing different objects in one model

node_tags_1 = [1, 2, 3, 4, 5, 6]
node_coords_1 = [[0, 0],
                 [1, 0],
                 [2, 0],
                 [0, 1],
                 [1, 1],
                 [2, 1]]

element_types_1 = [9, 9]  # Two quads
element_tags_1 = [1, 2]
connectivity_1 = [[1, 2, 5, 4],
                  [2, 3, 6, 5]]

model_name_1 = "example_model_04"
part_name_1 = "part_1"

model_1 = ParaqusModel(element_tags_1,
                       connectivity_1,
                       element_types_1,
                       node_tags_1,
                       node_coords_1,
                       model_name=model_name_1,
                       part_name=part_name_1)


# The second part looks like the first, but has different coordinates.
# note that the node and element numbers do not need to be unique across
# parts
node_tags_2 = [1, 2, 3, 4, 5, 6]
node_coords_2 = [[0, 2],
                 [1, 2],
                 [2, 2],
                 [0, 3],
                 [1, 3],
                 [2, 3]]

element_types_2 = [9, 9]  # Two quads
element_tags_2 = [1, 2]
connectivity_2 = [[1, 2, 5, 4],
                  [2, 3, 6, 5]]

model_name_2 = model_name_1
part_name_2 = "part_2"

model_2 = ParaqusModel(element_tags_2,
                       connectivity_2,
                       element_types_2,
                       node_tags_2,
                       node_coords_2,
                       model_name=model_name_2,
                       part_name=part_name_2)


# First create a writer, as you did before
vtu_writer = AsciiWriter(output_dir="vtu_examples")

# But now also create a CollectionWriter, which takes the writer as an
# argument (and uses it to write each file in the collection). The
# CollectionWriter is a context manager, which means it is used in a
# with statement as shown below:
collection_name = "example_model_04_combined"
with CollectionWriter(vtu_writer, collection_name) as collection_writer:
    collection_writer.write(model_1)
    collection_writer.write(model_2)


# The collection name replaces the model name of the ParaqusModels in
# the folder structure. In addition to the .vtu files for each
# individual part, a .pvd file is created. Opening this .pvd file in
# ParaView combines both parts in one view.

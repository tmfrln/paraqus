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
Example 05 - Grouping multiple vtu files for different times.

This example demonstrates how to work with time steps in paraqus.

"""
# Uncomment this if you can not add paraqus to the Python path, and set
# the Paraqus source directory for your system
# import sys
# sys.path.append("...")

import numpy as np

from paraqus import ParaqusModel, AsciiWriter, CollectionWriter


# ======================================================================
#           we start by creating the same model as in example 1
# ======================================================================

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
element_types = [9, 9, 5, 5, 5]  # Two quads, three triangles

# specify cell tags and the nodes of each cell
element_tags = [1, 2, 3, 4, 5]

connectivity = [[1, 2, 5, 4],
                [2, 3, 6, 5],
                [4, 5, 7],
                [5, 6, 8],
                [5, 8, 7]]

# name of the model - this will be the folder name for the vtu files
model_name = "example_model_05"

# name of the part - this will be the file name for the vtu files
part_name = "example_part_05"


# ======================================================================
#             the part different from example 1 starts here :-)
# ======================================================================

# Now loop over fake time steps and create a time-dependent displacement
# field. A new ParaqusModel is created for each time step. Since the
# .vtu files will be grouped, all of this happens within a with
# statement for the CollectionWriter

# Create a field called u representing the displacement of each node
field_name = "u"
field_tags = node_tags  # node tags, since we create a node field

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


# First create a writer, as we did before
vtu_writer = AsciiWriter(output_dir="vtu_examples")

collection_name = model_name
with CollectionWriter(vtu_writer, collection_name) as collection_writer:

    # Loop over time steps
    tmax = 2.
    for time in np.linspace(0, tmax, 21):
        # The only thing that changes in the base model is the optional
        # argument frame_time
        model = ParaqusModel(element_tags,
                             connectivity,
                             element_types,
                             node_tags,
                             node_coords,
                             model_name=model_name,
                             part_name=part_name,
                             frame_time=time)

        # Scale the displacement field and add the scaled field to the
        # model
        scale = time/tmax
        model.add_field(field_name,
                        field_tags,
                        field_values*scale,
                        field_position,
                        field_type)

        # now write the vtu file for this time step
        collection_writer.write(model)


# If you open the .pvd file in ParaView, the .vtu files for the
# individual models are interpreted as a time series and can be played
# as a video to visualize how the deformation changes over time

# Note that you should not change the generated folder structure within
# the parent folder 'example_model_05' to not break the links from the
# .pvd file to the associated .vtu files

# -*- coding: utf-8 -*-
"""
Example 03 - Node and element groups

This example demonstrates how node/element groups are specified.

"""
# # Uncomment this if you cannot add paraqus to the python path, and set
# # the paraqus source directory for your system
# import sys
# sys.path.append(".../paraqus/src")

from paraqus import ParaqusModel, AsciiWriter

# =============================================================================
#           we start by creating the same model as in example 1
# =============================================================================
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
model_name = "example_model_03"

# name of the part - this will be the file name for the vtu files
part_name = "example_part_03"

# now we have everything we need to create an instance of ParaqusModel, which
# is the type used to store all model data in paraqus
model = ParaqusModel(element_tags,
                     connectivity,
                     element_types,
                     node_tags,
                     node_coords,
                     model_name=model_name,
                     part_name=part_name)

# =============================================================================
#             the part different from example 1 starts here :-)
# =============================================================================

# it is often desirable to mark groups of nodes or elements, e.g. where
# boundary conditions are applied.
group_name = "nodes lower edge"
node_tags = [1,2,3]
model.add_node_group(group_name, node_tags)

group_name = "triangle elements"
element_tags = [3,4,5]
model.add_element_group(group_name, element_tags)

# the groups will be exported to the vtu files as indicator functions.
# for example, for the group "nodes lower edge", there will be a field
# "_group nodes lower edge", which takes the value 1 at all nodes in the group,
# and the value 0 on all other nodes.

# create an instance of the AsciiWriter (i.e. the vtu files are human readable)
writer = AsciiWriter(output_dir="vtu_examples")

# write the model to disk
writer.write(model)

# you can now use e.g. paraview to have a look at the vtu file and check that
# the groups can be visualized.

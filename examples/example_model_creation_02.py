# -*- coding: utf-8 -*-
"""
Example 02 - advanced model creation

This example demonstrates how to add field data to ParaqusModels.

"""
import numpy as np

from paraqus import ParaqusModel, AsciiWriter

# we start by creating the same model as in example 1

# specify node tags and corresponding coordinates (2d in this case)
node_tags = [1, 2, 3, 4, 5, 6, 7, 8]

# we use a numpy array for the coordinates now, because we want to process them
# later. In general, paraqus takes arguments as sequences and converts them to
# array internally anyways.
node_coords = np.array([[0, 0],
                        [1, 0],
                        [2, 0],
                        [0, 1],
                        [1, 1],
                        [2, 1],
                        [0.5, 1.5],
                        [1.5, 1.5]])

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
model_name = "example_model_02"

# name of the part - this will be the file name for the vtu files
part_name = "example_part_02"

# now we have everything we need to create an instance of ParaqusModel, which
# is the type used to store all model data in paraqus
model = ParaqusModel(element_tags,
                     connectivity,
                     element_types,
                     node_tags,
                     node_coords,
                     model_name=model_name,
                     part_name=part_name)

# the part different from example 1 starts here :-)

# we create a field called u representing the displacement of each node
field_name = "u"
field_tags = [1,2,3,4,5,6,7,8] # node tags, since we create a node field

# we prescribe x-displacements as 0
ux = np.zeros(len(node_tags))

# prescribe the y-displacement as 20% of the distance to the origin for each
# node
uy = 0.2*np.linalg.norm(node_coords, axis=1)

# combine ux and uy into a (number_of_nodes,2) array
field_values = np.vstack((ux, uy)).T

# specify that we add a node field with vector values
field_position = "nodes"
field_type = "vector"

# add the field to the model
model.add_field(field_name,
                field_tags,
                field_values,
                field_position,
                field_type)

# now we add a scalar element field called T (representing e.g. a temperature)
field_name = "T"
field_tags = [1,2,3,4,5] # these are now the element tags
field_values = [25., 25., 30., 30., 35.]

# specify that we add a node field with vector values
field_position = "elements"
field_type = "scalar"

# add the field to the model
model.add_field(field_name,
                field_tags,
                field_values,
                field_position,
                field_type)




# create an instance of the AsciiWriter (i.e. the vtu files are human readable)
# we specify the output directory and tell the writer to delete any old vtu
# files within the directory
writer = AsciiWriter(output_dir="vtu_examples",
                     clear_output_dir=True)

# write the model to disk
writer.write(model)

# if you open the vtu file in paraview, you can use the "warp by vector"
# filter to visualize the displacements

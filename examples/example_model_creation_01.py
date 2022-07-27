# -*- coding: utf-8 -*-
"""
Example 01 - model creation

This example demonstrates how to create a ParaqusModel instance from scratch.
The model is then written to a vtu file.

"""
from paraqus import ParaqusModel, AsciiWriter

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
# we specify the output directory and tell the writer to delete any old vtu
# files within the directory
writer = AsciiWriter(output_dir="vtu_examples",
                     clear_output_dir=True)

# write the model to disk
writer.write(model)

# you can now use e.g. paraview to have a look at the vtu file
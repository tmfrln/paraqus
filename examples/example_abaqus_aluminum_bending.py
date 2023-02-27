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
Export selected results from the aluminum bending example output database.

The model contains shell elements, including rigid elements and damage.
This example demonstrates how paraqus deals with these challenges.

Run this file in the Abaqus python interpreter. It is assumed that the
output dabase 'threepointbending_alextrusion.odb' is located in the current
work directory. Visit the paraqus documentation for a full description on how
to run the example before using this script to export results.

To create the output database for this example, execute the following
commands in the examples folder:
    abaqus fetch job=threepointbending_alextrusion.inp
    abaqus job=threepointbending_alextrusion parallel=domain domains=4 cpus=4 mp_mode=threads interactive

Caution: This might take a few minutes. If you machine has less than
4 CPUs, adjust the domains and cpus parameters.

The following pipeline can be used in Paraview to visualize the results:
- Apply deformation (Warp By Vector filter)
- Remove failed elements (Threshold filter based on STATUS variable > 0.5)
- Alternative: Threshold based on STATUS < 0.5 and invert (keeps the rigid bodies)
- Coloring according to the variable S_mides_absmax

"""
# # Uncomment this if you cannot add paraqus to the python path, and set
# # the paraqus source directory for your system
# import sys
# sys.path.append("...")

# we will use the ODBReader class to extract information from the odb
from paraqus.abaqus import ODBReader
from paraqus.writers import BinaryWriter

# set some constants based on the odb that will be exported
ODB_PATH = "threepointbending_alextrusion.odb" # path to the odb
MODEL_NAME = "Aluminum-Bending" # can be chosen freely
INSTANCE_NAMES = None # None will choose all instances
STEP_NAME = "Step-1" # name of the step that will be exported
FRAME_INDEX = -1 # export the last frame of the step

# create the reader
reader = ODBReader(odb_path=ODB_PATH,
                   model_name=MODEL_NAME,
                   instance_names=INSTANCE_NAMES,
                   )

# for shell elements, output is stored at different section points,
# representing different points along the element thickness. We can
# either export the results for a specified point, or use a reduction to
# obtain a field based on all section points.

# Note that the rigid elements do not have stress output - paraqus will
# fill the results for these elements with nans

# specify which fields will be exported
reader.add_field_export_request("S", # S = stress
                                invariant="mises", # export the von Mises norm
                                section_point_reduction='absmax', # reduction: use maximum absolute value
                                )

# same output, but only for one section point
reader.add_field_export_request("S",
                                invariant="mises",
                                section_point_number=1,
                                )

reader.add_field_export_request("U") # displacements
reader.add_field_export_request("STATUS") # indicates element failure

# add some element groups, representing different parts of the model
reader.add_set_export_request(set_name="P1_DOUBLECHAMBEREXTRUSION",
                              set_type="elements",
                              instance_name="PART-1-1")

reader.add_set_export_request(set_name="P2_PUNCH",
                              set_type="elements",
                              instance_name="PART-1-1")

reader.add_set_export_request(set_name="P3_LEFTSUPPORT",
                              set_type="elements",
                              instance_name="PART-1-1")

reader.add_set_export_request(set_name="P4_RIGHTSUPPORT",
                              set_type="elements",
                              instance_name="PART-1-1")

# create a writer that will write the exported results to a vtk file
vtu_writer = BinaryWriter("vtk_output_bending", clear_output_dir=True)

# loop over all instances and export the results
instance_models = list(reader.read_instances(step_name=STEP_NAME,
                                             frame_index=FRAME_INDEX))

# instance_models has length 1, since there is only 1 instance
vtu_writer.write(instance_models[0])

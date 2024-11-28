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
Export selected results from the aluminum bending example output
database. Datails on this example are available in the Abaqus Example
Problems Guide:

    Example Problems -> Dynamic Stress/Displacement Analyses -> Dynamic
    stress analysis -> Progressive failure analysis of thin-wall
    aluminum extrusion under quasi-static and dynamic loads

The model contains shell elements, including rigid elements and damage.
This example demonstrates how Paraqus deals with these challenges.

To create the output database for this example, set your current work
directory to the Paraqus examples folder and execute the following:
    abaqus fetch job=threepointbending_alextrusion.inp
    abaqus job=threepointbending_alextrusion parallel=domain domains=4 cpus=4 mp_mode=threads interactive

Caution: This might take a few minutes. If you machine has less than 4
CPUs, adjust the domains and cpus parameters.

After the file 'threepointbending_alextrusion.odb' has been created run
this script in the Abaqus Python interpreter via:
    abaqus cae noGUI=example_abaqus_aluminum_bending.py

The following pipeline can be used in ParaView to visualize the results:
- Apply deformation (Warp By Vector filter)
- Remove failed elements (Threshold filter based on STATUS
  variable > 0.5)
- Alternative: Threshold based on STATUS < 0.5 and invert (keeps the
  rigid bodies)
- Coloring according to the variable S_mides_absmax

"""
# Uncomment this if you can not add Paraqus to the Python path, and set
# the Paraqus source directory for your system
# import sys
# sys.path.append("...")

# You will use the OdbReader class to extract information from the ODB
from paraqus.abaqus import OdbReader
from paraqus.writers import BinaryWriter

# Set some constants based on the ODB that will be exported
ODB_PATH = "threepointbending_alextrusion.odb"  # Path to the ODB
MODEL_NAME = "Aluminum-Bending"  # Can be chosen freely
INSTANCE_NAMES = None  # None will choose all instances
STEP_NAME = "Step-1"  # Name of the step that will be exported
FRAME_INDEX = -1  # Export the last frame of the step

# Create the reader
reader = OdbReader(odb_path=ODB_PATH,
                   model_name=MODEL_NAME,
                   instance_names=INSTANCE_NAMES,
                   )

# For shell elements, output is stored at different section points,
# representing different points along the element thickness. You can
# either export the results for a specified point, or use a reduction to
# obtain a field based on all section points

# Note that the rigid elements do not have stress output - Paraqus will
# fill the results for these elements with NaNs

# Specify which fields will be exported
reader.add_field_export_request(
    "S",  # S = stress
    invariant="mises",  # Export the von Mises norm
    section_point_reduction="absmax",  # Reduction: max absolute value
    )

# Same output, but only for one section point
reader.add_field_export_request("S",
                                invariant="mises",
                                section_point_number=1,
                                )

reader.add_field_export_request("U")  # Displacements
reader.add_field_export_request("STATUS")  # Indicates element failure

# Add some element groups, representing different parts of the model
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

# Create a writer that will write the exported results to a .vtu file
vtu_writer = BinaryWriter("vtk_output_bending", clear_output_dir=True)

# Loop over all instances and export the results
for instance_model in reader.read_instances(step_name=STEP_NAME,
                                            frame_index=FRAME_INDEX):
    vtu_writer.write(instance_model)

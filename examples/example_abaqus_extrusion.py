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
Export selected results from the extrusion example output database.

Run this file in the Abaqus python interpreter. It is assumed that the
output dabase 'extrusion.odb' is located in the current work directory.
Visit the paraqus documentation for a full description on how to run
the example before using this script to export results.

To create the output database for this example, execute the following
commands in the examples folder:
    abaqus cae noGUI=run_example_abaqus_extrusion.py

The following pipeline can be used in Paraview to visualize the results:
- Apply deformation (Warp By Vector filter)
- Coloring according to the variable SDV1 or SDV11
- Play the results in "Real Time" mode in the Paraview Animation View.
  Since we export 100 time steps, a smooth animation of the process
  is available.

"""
# # Uncomment this if you cannot add paraqus to the python path, and set
# # the paraqus source directory for your system
# import sys
# sys.path.append("...")

# we will use the ODBReader class to extract information from the odb
from paraqus.abaqus import ODBReader
from paraqus.writers import BinaryWriter, CollectionWriter

print("EXPORT RUNNING...")

# set some constants based on the odb that will be exported
ODB_PATH = "extrusion.odb" # path to the odb
MODEL_NAME = "extrusion" # can be chosen freely
INSTANCE_NAMES = ["EXTRUDEINSTANCE", "MATRIXINSTANCE"] # which instances will be exported
STEP_NAME = "Step-1" # name of the step that will be exported

# the class ODBReader is used to export results from Abaqus odbs.
reader = ODBReader(odb_path=ODB_PATH,
                   model_name=MODEL_NAME,
                   instance_names=INSTANCE_NAMES,
                   )

# a fortran user material is used in the example. The following data is
# stored in the state dependent variables:
# SDV #  |             Description
#-------------------------------------------------
#    1   | Equivalent plastic strain
#  2-10  | Plastic part Fp of deformation gradient
#   11   | Norm of the deviatoric part of Fp

# an export request for the field 'SDV' requests all the internal
# variables.

# field export requests
reader.add_field_export_request("U", field_position="nodes")
reader.add_field_export_request("S", field_position="elements")

# we request only the scalar sdvs stored in position 1 and 11 to
# demonstrate the workflow
reader.add_field_export_request("SDV1", field_position="elements")
reader.add_field_export_request("SDV11", field_position="elements")

# create a writer that will write the exported results to a vtk file
vtu_writer = BinaryWriter("vtk_output_extrusion", clear_output_dir=True)


# We use a CollectionWriter and export all frames for this example
with CollectionWriter(vtu_writer, "extrusion") as writer:
    # extract number of frames from the odb
    FRAME_INDICES = list(range(reader.get_number_of_frames(STEP_NAME)))
    for i_frame, frame_index in enumerate(FRAME_INDICES):
        for instance_model in reader.read_instances(step_name=STEP_NAME,
                                                    frame_index=frame_index):
            writer.write(instance_model)

        print("    exporting frame %d of %d..." % (i_frame, len(FRAME_INDICES)))

print("*** FINISHED ***")


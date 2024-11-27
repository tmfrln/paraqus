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
Export selected results from the cylindrical billet example output database.
Datails on this example are available in the Abaqus Example Problems Guide:

    Example Problems -> Static Stress/Displacement Analysis -> Forming analyses
    -> Upsetting of a cylindrical billet: coupled temperature-displacement and
    adiabatic analysis

To create the output database for this example, set your current work directory
to the Paraqus examples folder and execute the following:
    abaqus fetch job=cylbillet_cax4rt_slow_dense.inp
    abaqus job=cylbillet_cax4rt_slow_dense interactive

After the file 'cylbillet_cax4rt_slow_dense.odb' has been created, run this
script in the Abaqus Python interpreter via:
    abaqus cae noGUI=example_abaqus_cylindrical_billet.py

The following pipeline can be used in ParaView to visualize the results:
- Apply deformation (Warp By Vector filter)
- Rotate model around z-axis by -90° (Transform filter)
- Reflect model at y-axis (Reflect filter)
- Rotate model around y-axis by 90° (Transform filter)
- Create a surface (Extract Surface filter)
- Revolve around z-axis (Rotational Extrusion filter)
- Extrapolate data from cells to point (Cell Data to Point Data filter)
- Coloring according to the variable TEMP

"""
# uncomment this if you can not add paraqus to the Python path, and set
# the Paraqus source directory for your system
# import sys
# sys.path.append("...")

# you will use the OdbReader class to extract information from the ODB
from paraqus.abaqus import OdbReader
from paraqus.writers import AsciiWriter

print("EXPORT RUNNING...")

# set some constants based on the ODB that will be exported
ODB_PATH = "cylbillet_cax4rt_slow_dense.odb"  # path to the ODB
MODEL_NAME = "Cylindrical-Billet"  # can be chosen freely
INSTANCE_NAMES = ["PART-1-1"]  # which instances will be exported
STEP_NAME = "Step-1"  # name of the step that will be exported
FRAME_INDEX = -1  # export the last frame of the step

# the class OdbReader is used to export results from Abaqus ODBs
reader = OdbReader(odb_path=ODB_PATH,
                   model_name=MODEL_NAME,
                   instance_names=INSTANCE_NAMES,
                   )

# start configuring the reader instance by specifying field outputs and
# node/element groups that will be exported. These must of course be
# available in the output database.

# field export requests
reader.add_field_export_request("U", field_position="nodes")
reader.add_field_export_request("PEEQ", field_position="elements")
reader.add_field_export_request("TEMP", field_position="elements")
reader.add_field_export_request("PE", field_position="elements")

# request some element sets, so you can have a closer look at these elements
reader.add_set_export_request("ESID", set_type="elements",
                              instance_name="PART-1-1")
reader.add_set_export_request("ETOP", set_type="elements",
                              instance_name="PART-1-1")

# create a writer that will write the exported results to a .vtu file
vtu_writer = AsciiWriter("vtk_output_billet", clear_output_dir=True)

# the method read_instances loops over all part instances for one
# point in time, and returns ParaqusModel instances for each of them.
# we put them in a list here, so they can be inspected, but it is more
# memory-efficient to use them one after another in a for loop (see
# following tutorials)
instance_models = list(reader.read_instances(step_name=STEP_NAME,
                                             frame_index=FRAME_INDEX))

# instance_models has length 1, since there is only 1 instance with a mesh
instance_model = instance_models[0]  # this is a ParaqusModel

# use the writer to write the file to disk
vtu_writer.write(instance_model)

print("*** FINISHED ***")
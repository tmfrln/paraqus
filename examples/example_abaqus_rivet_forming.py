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
Export selected results from the rivet forming example output database. Datails
on this example are available in the Abaqus Example Problems Guide:

    Example Problems -> Dynamic Stress/Displacement Analyses -> Eulerian and
    co-simulation analyses -> Rivet forming

This example is based on the Coupled Eulerian Lagrangian method, i.e.
a fluid-structure-interaction. Paraqus will just work for these elements
without any extra steps.

To create the output database for this example, set your current work directory
to the Paraqus examples folder and execute the following:
    abaqus fetch job=rivet_forming_cel.inp
    abaqus job=rivet_forming_cel parallel=domain domains=4 cpus=4 mp_mode=threads interactive

Caution: This might take up to an hour. If you machine has less than 4 CPUs,
adjust the domains and cpus parameters. If you want to test the features of
Paraqus but are not interested in the full result, you can change the step time
to only simulate part of the forming process. To do this, locate the following
section in the input file 'rivet_forming_cel.inp':

    *Step, name=Step-1, nlgeom=YES
    Displace dies
    *Dynamic, Explicit
    , 0.001

and change the value from 0.001 to a smaller one, e.g. 0.0001 to
simulate the first 10 % of the process.

After the file 'Rivet-Forming-CEL.odb' has been created, run this script in
the Abaqus Python interpreter via:
    abaqus cae noGUI=example_abaqus_rivet_forming.py

The following pipeline can be used in ParaView to visualize the results:
- Merging of the parallel files (CleantoGrid filter)
- Mapping of the volume fraction from element centers to nodes (CellDatatoPointData filter)
- Extraction of the isosurface representing the boundary of the rivet (Isovolume filter)
- Coloring according to the variable PEEQVAVG (choose in the menu for the last filter)

"""
# uncomment this if you can not add Paraqus to the Python Path, and set
# the Paraqus source directory for your system
# import sys
# sys.path.append("...")

# you will use the OdbReader class to extract information from the ODB
from paraqus.abaqus import OdbReader
from paraqus.writers import AsciiWriter, CollectionWriter

ODB_PATH = "rivet_forming_cel.odb"  # path to the ODB
MODEL_NAME = "Rivet-Forming-CEL"  # can be chosen freely
INSTANCE_NAMES = ["EULERIAN-1"]  # which instances will be exported
STEP_NAME = "Step-1"  # name of the step that will be exported
FRAME_INDICES = [1, -1]  # export the first and last frame of the step

# create the reader
reader = OdbReader(odb_path=ODB_PATH,
                   model_name=MODEL_NAME,
                   instance_names=INSTANCE_NAMES,
                   )

# which fields will be exported
# volume fraction of material 1
reader.add_field_export_request("EVF_ASSEMBLY_EULERIAN-1_MAT-1-1")
reader.add_field_export_request("PEEQVAVG")  # equiv. plastic strain

# create a writer that will write the exported results to a .vtu file
vtu_writer = AsciiWriter("vtk_output_rivet", clear_output_dir=True)

# the VTK format supports parallel files for large model, i.e. model
# information is split to multiple files. This makes the post-processing
# in ParaView faster. ParaView supports splitting your models into
# multiple .vtu files:
vtu_writer.number_of_pieces = 4

# use a CollectionWriter again to group all files
with CollectionWriter(vtu_writer, "Rivet Forming") as writer:
    for frame_index in FRAME_INDICES:
        # this is an example for a "large" model (even though it should
        # be far from filling up your RAM), therefore iterate over the
        # instance models without storing all of them in a list
        for instance_model in reader.read_instances(step_name=STEP_NAME,
                                                    frame_index=frame_index):
            writer.write(instance_model)
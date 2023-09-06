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
Export selected results from the cylindrical billet example output databases.

The FE simulation was stopped and resumed after a remeshing step,
leaving us with two odbs containing results for different points of time.

Run this file in the Abaqus python interpreter. It is assumed that the
output dabase 'cylbillet_cax4rt_slow_dense.odb' is located in the current
work directory. Visit the paraqus documentation for a full description on
how to run the example before using this script to export results.

To create the output database for this example, execute the following
commands in the examples folder:
    abaqus fetch job=billet_case1_std_coarse.inp
    abaqus fetch job=billet_case1_std_coarse_rez.inp
    abaqus fetch job=billet_coarse_elem.inp
    abaqus fetch job=billet_coarse_nodes.inp
    abaqus fetch job=billet_coarse_elem_rez.inp
    abaqus fetch job=billet_coarse_nodes_rez.inp
    abaqus job=billet_case1_std_coarse interactive
    abaqus job=billet_case1_std_coarse_rez oldjob=billet_case1_std_coarse interactive

The following pipeline can be used in Paraview to visualize the results:
- Apply deformation (Warp By Vector filter)
- Rotate model around z-axis by -90° (Transform filter)
- Reflect model at y-axis (Reflect filter)
- Rotate model around y-axis by 90° (Transform filter)
- Create a surface (Extract Surface filter)
- Revolve around z-axis (Rotational Extrusion filter)
- Extrapolate data from cells to point (Cell Data to Point Data filter)
- Coloring according to the variable S_mises

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
ODB_PATHS = ["billet_case1_std_coarse.odb",
             "billet_case1_std_coarse_rez.odb"] # path to the odb files
MODEL_NAME = "Cylindrical-Billet-Adaptive" # can be chosen freely
INSTANCE_NAMES = ["BILLET-1"] # which instances will be exported

# we will loop over these, each entry corresponds to one output database
STEP_NAMES = ["Step-1", "Step-1"] # name of the step that will be exported
FRAME_INDICES = [(0, -1), (1, -1)] # frame indices to export per odb

# create a writer that will write the exported results to a vtk file
# we use the BinaryWriter this time, creating more efficient but not
# human-readable files
vtu_writer = BinaryWriter("vtk_output_billet_adaptive", clear_output_dir=True)

# we use the CollectionWriter context manager to create a .pvd file for all
# time steps. This allows us to combine multiple files, representing
# different parts of the model at different times, into one representation
# in paraview. It also makes it possible to export videos based on time
# instead of just a sequence (useful if time steps are not spaced equally).
with CollectionWriter(vtu_writer, "Compression Test") as coll_writer:
    # start at time 0.0
    time_offset = 0.0

    # loop over the steps and frames in two different odbs
    for step, frames, odb in zip(STEP_NAMES, FRAME_INDICES, ODB_PATHS):
        # we create a new reader for each odb
        reader = ODBReader(odb_path=odb,
                           model_name=MODEL_NAME,
                           instance_names=INSTANCE_NAMES,
                           time_offset=time_offset
                           )

        # we always export the same results
        reader.add_field_export_request("U")
        reader.add_field_export_request("PEEQ")
        reader.add_field_export_request("S")
        reader.add_field_export_request("S", invariant="mises")
        reader.add_field_export_request("PE")

        # we export the first and last frame of the only step in both odbs
        for frame_index in frames:
            # remember that read_instances generates ParaqusModels for
            # each instance
            for instance_model in reader.read_instances(step_name=step,
                                                        frame_index=frame_index):
                # write the actual vtk file for the current time and
                # instance
                coll_writer.write(instance_model)

        # update the initial time for the next odb (because the results
        # of the second job start at time 0 again)
        time_offset = reader.get_frame_time(step, -1)

print("*** FINISHED ***")

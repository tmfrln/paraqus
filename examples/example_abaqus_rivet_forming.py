"""
Export selected results from the rivet forming example output database.

This example is based on the Coupled Eulerian Lagrangian method, i.e.
a fluid-structure-interaction. Paraqus will just work for these elements
without any extra steps.

Run this file in the Abaqus python interpreter. It is assumed that the
output dabase 'Rivet-Forming-CEL.odb' is located in the current work
directory. Visit the paraqus documentation for a full description on how to
run the example before using this script to export results.

To create the output database for this example, execute the following
commands in the examples folder:
    abaqus fetch job=rivet_forming_cel.inp
    abaqus job=Rivet-Forming-CEL parallel=domain domains=4 cpus=4 mp_mode=threads interactive

Caution: This might take up to an hour. If you machine has less than
4 CPUs, adjust the domains and cpus parameters.  If you want to test the
features of paraqus but are not interested in the full result, you can
change the step time to only simulate part of the forming process. To do
this, locate the following section in the input file:

    *Step, name=Step-1, nlgeom=YES
    Displace dies
    *Dynamic, Explicit
    , 0.001

and change the value from 0.001 to a smaller one, e.g. 0.0001 to
simulate the first 10% of the process.


The following pipeline can be used in Paraview to visualize the results:
- Merging of the parallel files (CleantoGrid filter)
- Mapping of the volume fraction from element centers to nodes (CellDatatoPointData filter)
- Extraction of the isosurface representing the boundary of the rivet (Isovolume filter)
- Coloring according to the variable PEEQVAVG (choose in the menu for the last filter)

"""
# # Uncomment this if you cannot add paraqus to the python path, and set
# # the paraqus source directory for your system
# import sys
# sys.path.append(".../paraqus/src")

# we will use the ODBReader class to extract information from the odb
from paraqus.abaqus import ODBReader
from paraqus.writers import AsciiWriter, CollectionWriter

ODB_PATH = "rivet_forming_cel.odb" # path to the odb
MODEL_NAME = "Rivet-Forming-CEL" # can be chosen freely
INSTANCE_NAMES = ["EULERIAN-1"] # which instances will be exported
STEP_NAME = "Step-1" # name of the step that will be exported
FRAME_INDICES = [1, -1] # export the first and last frame of the step

# create the reader
reader = ODBReader(odb_path=ODB_PATH,
                   model_name=MODEL_NAME,
                   instance_names=INSTANCE_NAMES,
                   )

# which fields will be exported
# volume fraction of material 1
reader.add_field_export_request("EVF_ASSEMBLY_EULERIAN-1_MAT-1-1")
reader.add_field_export_request("PEEQVAVG") # equiv. plastic strain

# create a writer that will write the exported results to a vtk file
vtu_writer = AsciiWriter("vtk_output", clear_output_dir=True)

# the vtk format supports parallel files for large model, i.e. model
# information is split to multiple files. This makes the post-processing
# in paraview faster. Paraview supports splitting your models into
# multiple vtk files:
vtu_writer.number_of_pieces = 4

# We use a CollectionWriter again to group all files:
with CollectionWriter(vtu_writer, "Rivet Forming") as writer:
    for frame_index in FRAME_INDICES:
        # this is an example for a "large" model (even though it should
        # be far from filling up your RAM), therefore we demonstrate how
        # to iterate over the instance models without storing all of
        # them in a list:
        for instance_model in reader.read_instances(step_name=STEP_NAME,
                                                    frame_index=frame_index):
            writer.write(instance_model)



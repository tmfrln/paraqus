"""
Export selected results from the cylindrical billet example output database.

Run this file in the Abaqus python interpreter. It is assumed that the
output dabase 'cylbillet_cax4rt_slow_dense.odb' is located in the current
work directory. Visit the paraqus documentation for a full description on
how to run the example before using this script to export results.

To create the output database for this example, execute the following
commands in the examples folder:
    abaqus fetch job=cylbillet_cax4rt_slow_dense.inp
    abaqus job=cylbillet_cax4rt_slow_dense interactive

The following pipeline can be used in Paraview to visualize the results:
- Apply deformation (Warp By Vector filter)
- Rotate model around z-axis by -90° (Transform filter)
- Reflect model at y-axis (Reflect filter)
- Rotate model around y-axis by 90° (Transform filter)
- Create a surface (Extract Surface filter)
- Revolve around z-axis (Rotational Extrusion filter)
- Extrapolate data from cells to point (Cell Data to Point Data filter)
- Coloring according to the variable TEMP

"""
# # Uncomment this if you cannot add paraqus to the python path, and set
# # the paraqus source directory for your system
# import sys
# sys.path.append(".../paraqus/src")

# we will use the ODBReader class to extract information from the odb
from paraqus.abaqus import ODBReader
from paraqus.writers import AsciiWriter

print("EXPORT RUNNING...")

# set some constants based on the odb that will be exported
ODB_PATH = "cylbillet_cax4rt_slow_dense.odb" # path to the odb
MODEL_NAME = "Cylindrical-Billet" # can be chosen freely
INSTANCE_NAMES = ["PART-1-1"] # which instances will be exported
STEP_NAME = "Step-1" # name of the step that will be exported
FRAME_INDEX = -1 # export the last frame of the step

# the class ODBReader is used to export results from Abaqus odbs.
reader = ODBReader(odb_path=ODB_PATH,
                   model_name=MODEL_NAME,
                   instance_names=INSTANCE_NAMES,
                   )

# we start configuring the reader instance by specifying field outputs
# and node/element groups that will be exported. These must of course be
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

# create a writer that will write the exported results to a vtk file
vtu_writer = AsciiWriter("vtk_output", clear_output_dir=True)

# the method read_instances loops over all part instances for one
# point in time, and returns ParaqusModel instances for each of them.
# we put them in a list here, so they can be inspected, but it is more
# memory-efficient to use them one after another in a for loop (see
# following tutorials)
instance_models = list(reader.read_instances(step_name=STEP_NAME,
                                             frame_index=FRAME_INDEX))

# instance_models has length 1, since there is only 1 instance with a mesh
instance_model = instance_models[0] # this is a ParaqusModel

# use the writer to write the file to disk
vtu_writer.write(instance_model)

print("*** FINISHED ***")

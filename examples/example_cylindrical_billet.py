"""
Export selected results from the cylindrical billet example output database.

Run this file in the Abaqus python interpreter. It is assumed that the 
output dabase 'cylbillet_cax4rt_slow_dense.odb' is located in the current
work directory. Visit the paraqus documentation for a full description on 
how to run the example before using this script to export results.

"""
# TODO: Add link to docs

# we will use the ODBReader class to extract information from the odb
from paraqus.abaqus import ODBReader
from paraqus.writers import BinaryWriter, AsciiWriter

print("EXPORT RUNNING...")

ODB_PATH = "cylbillet_cax4rt_slow_dense.odb" # path to the odb
MODEL_NAME = "Cylindrical-Billet" # can be chosen freely
INSTANCE_NAMES = ["Part-1-1"] # which instances will be exported
STEP_NAME = "Step-1" # name of the step that will be exported
FRAME_INDICES = [0, -1] # export the last frame of the step

# create the reader - this will not yet perform any "reading"
reader = ODBReader(odb_path=ODB_PATH,
                   model_name=MODEL_NAME,
                   instance_names=INSTANCE_NAMES,
                   )

reader.add_field_export_request("U", field_position="nodes")
reader.add_field_export_request("PEEQ", field_position="elements")
reader.add_field_export_request("TEMP", field_position="elements")
reader.add_field_export_request("PE", field_position="elements")

reader.add_set_export_request("ESID", set_type="elements", 
                              instance_name="PART-1-1")
reader.add_set_export_request("ETOP", set_type="elements", 
                              instance_name="PART-1-1")

# create a writer that will write the exported results to a vtk file
# vtu_writer = BinaryWriter("vtk_output", clear_output_dir=True)
vtu_writer = AsciiWriter("vtk_output", clear_output_dir=True)

# loop over all instances and export the results
vtu_writer.initialize_collection()

for frame_index in FRAME_INDICES:
    for instance_model in reader.read(step_name=STEP_NAME,
                                      frame_index=frame_index):
        vtu_writer.write(instance_model)

vtu_writer.finalize_collection()

print("*** FINISHED ***")
"""
Export selected results from the rivet forming example output database.

Run this file in the Abaqus python interpreter. It is assumed that the
output dabase 'Rivet-Forming-CEL.odb' is located in the current work
directory. Visit the paraqus documentation for a full description on how to
run the example before using this script to export results.


"""
# TODO: Add link to docs

# we will use the ODBReader class to extract information from the odb
from paraqus.abaqus import ODBReader
from paraqus.writers import AsciiWriter

ODB_PATH = "rivet_forming_cel.odb" # path to the odb
MODEL_NAME = "Rivet-Forming-CEL" # can be chosen freely
INSTANCE_NAMES = ["EULERIAN-1"] # which instances will be exported
STEP_NAME = "Step-1" # name of the step that will be exported
FRAME_INDICES = [1, -1] # export the last frame of the step

# create the reader - this will not yet perform any "reading"
reader = ODBReader(odb_path=ODB_PATH,
                   model_name=MODEL_NAME,
                   instance_names=INSTANCE_NAMES,
                   )

reader.add_field_export_request("EVF_ASSEMBLY_EULERIAN-1_MAT-1-1")
reader.add_field_export_request("PEEQVAVG")

# create a writer that will write the exported results to a vtk file
vtu_writer = AsciiWriter("vtk_output", clear_output_dir=True)

# divide each part instance into four separate files for fast processing in
# paraview
vtu_writer.number_of_pieces = 4

# loop over all instances and export the results
vtu_writer.initialize_collection()

for frame_index in FRAME_INDICES:
    for instance_model in reader.read_instances(step_name=STEP_NAME,
                                                frame_index=frame_index):
        vtu_writer.write(instance_model)

vtu_writer.finalize_collection()

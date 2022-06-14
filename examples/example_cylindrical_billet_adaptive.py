"""
Export selected results from the cylindrical billet example output database.

Run this file in the Abaqus python interpreter. It is assumed that the 
output dabase 'cylbillet_cax4rt_slow_dense.odb' is located in the current
work directory. Visit the paraqus documentation for a full description on 
how to run the example before using this script to export results.

"""
# TODO: Add link to docs

# # Uncomment this if you cannot add paraqus to the python path, and set
# # the paraqus source directory for your system
# import sys
# sys.path.append(".../paraqus/src")

# we will use the ODBReader class to extract information from the odb
from paraqus.abaqus import ODBReader
from paraqus.writers import BinaryWriter, AsciiWriter, CollectionWriter

print("EXPORT RUNNING...")

ODB_PATHS = ["billet_case1_std_coarse.odb",
             "billet_case1_std_coarse_rez.odb"] # path to the odb files
MODEL_NAME = "Cylindrical-Billet-Adaptive" # can be chosen freely
INSTANCE_NAMES = ["BILLET-1"] # which instances will be exported
STEP_NAME = "Step-1" # name of the step that will be exported
FRAME_INDICES = [(0, -1), (1, -1)] # frame indices to export per odb

# create a writer that will write the exported results to a vtk file
vtu_writer = BinaryWriter("vtk_output", clear_output_dir=True)
# vtu_writer = AsciiWriter("vtk_output", clear_output_dir=True)

# we use the CollectionWriter context manager to create a .pvd file for all
# time steps. This allows us to combine a large number of files, representing
# different parts of the model at different times, into one representation
# in paraview. It also makes it possible to export videos based on time
# instead of just a sequence (useful if time steps are not spaced equally).
with CollectionWriter(vtu_writer, "Compression Test") as writer:

    time_offset = 0
    for frames, odb in zip(FRAME_INDICES, ODB_PATHS):
        reader = ODBReader(odb_path=odb,
                           model_name=MODEL_NAME,
                           instance_names=INSTANCE_NAMES,
                           time_offset=time_offset
                           )
        
        reader.add_field_export_request("U")
        reader.add_field_export_request("PEEQ")
        reader.add_field_export_request("S")
        reader.add_field_export_request("S", invariant="mises")
        reader.add_field_export_request("PE")
    
        for frame_index in frames:
            for instance_model in reader.read_instances(step_name=STEP_NAME,
                                                        frame_index=frame_index):
                writer.write(instance_model)
                
        time_offset = reader.get_frame_time(STEP_NAME, frame_index)

print("*** FINISHED ***")
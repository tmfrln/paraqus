"""
Export selected results from the aluminum bending example output database.

Run this file in the Abaqus python interpreter. It is assumed that the
output dabase 'threepointbending_alextrusion.odb' is located in the current
work directory. Visit the paraqus documentation for a full description on how
to run the example before using this script to export results.


"""
# TODO: Add link to docs

# # Uncomment this if you cannot add paraqus to the python path, and set
# # the paraqus source directory for your system
# import sys
# sys.path.append(".../paraqus/src")

# we will use the ODBReader class to extract information from the odb
from paraqus.abaqus import ODBReader
from paraqus.writers import BinaryWriter

ODB_PATH = "threepointbending_alextrusion.odb" # path to the odb
MODEL_NAME = "Aluminum-Bending" # can be chosen freely
INSTANCE_NAMES = None # None will choose all instances
STEP_NAME = "Step-1" # name of the step that will be exported
FRAME_INDEX = -1 # export the last frame of the step

# create the reader - this will not yet perform any "reading"
reader = ODBReader(odb_path=ODB_PATH,
                   model_name=MODEL_NAME,
                   instance_names=INSTANCE_NAMES,
                   )

# specify which fields will be exported
reader.add_field_export_request("S", # S = stress
                                invariant="mises", # export the von Mises norm
                                # for each shell element, there are multiple
                                # field values at different section points,
                                # i.e. points along the shell thickness
                                # direction. Set this to 'mean' to average them,
                                # or to 'absmax' to export the value with the
                                # highest norm.
                                section_point_reduction='absmax',
                                )

reader.add_field_export_request("S", # S = stress
                                invariant="mises", # export the von Mises norm
                                # for each shell element, there are multiple
                                # field values at different section points,
                                # i.e. points along the shell thickness
                                # direction. Set this to 'mean' to average them,
                                # or to 'absmax' to export the value with the
                                # highest norm.
                                section_point_number=1,
                                )

reader.add_field_export_request("U")
reader.add_field_export_request("STATUS")


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

# create a writer that will write the exported results to a vtk file
vtu_writer = BinaryWriter("vtk_output", clear_output_dir=True)

# loop over all instances and export the results
instance_models = list(reader.read_instances(step_name=STEP_NAME,
                                             frame_index=FRAME_INDEX))

# instance_models has length 1, since there is only 1 instance
vtu_writer.write(instance_models[0])
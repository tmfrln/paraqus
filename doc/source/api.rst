API
===

The user interface of Paraqus is documented here. Classes/methods are only listed here if they are supposed to be used by the user of the program.

ParaqusModel
------------

.. automodule:: paraqus.ParaqusModel
   :members: add_field, add_node_group, add_element_group, split_model, get_fields_by_type, get_node_field, get_element_field

BinaryWriter/AsciiWriter
------------------------
We only document the BinaryWriter class here. The AsciiWriter class has the same API and writes binary instead of ascii files.

.. automodule:: paraqus.BinaryWriter
   :members: write


CollectionWriter
----------------

.. automodule:: paraqus.CollectionWriter
   :members: write

ODBReader
---------
The ODBReader class is only useable in the Abaqus python interpreter.

.. automodule:: paraqus.abaqus.ODBReader
   :members: add_field_export_request, add_set_export_request, add_surface_export_request, get_frame_time, read_instances


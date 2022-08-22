API
===

The user interface of Paraqus is documented here. Classes/methods are only listed here if they are supposed to be used by the user of the program.

ParaqusModel
------------

.. autoclass:: paraqus.ParaqusModel
   :members:

BinaryWriter/AsciiWriter
------------------------
We only document the BinaryWriter class here. The AsciiWriter class has the same API and writes binary instead of ascii files.

.. autoclass:: paraqus.BinaryWriter
   :members:
   :inherited-members:


CollectionWriter
----------------

.. autoclass:: paraqus.CollectionWriter
   :members:
   :inherited-members:

ODBReader
---------
The ODBReader class is only useable in the Abaqus python interpreter.

.. autoclass:: paraqus.abaqus.ODBReader
   :members:

API
===

The user interface of Paraqus is documented here. Classes/methods are only listed here if they are supposed to be used by the user of the program.

ParaqusModel
------------

.. autoclass:: paraqus.ParaqusModel
   :members:

Writers
-------

.. autoclass:: paraqus.AsciiWriter
   :members:
   :inherited-members:

.. autoclass:: paraqus.BinaryWriter
   :members:
   :inherited-members:
   :special-members: __init__

CollectionWriter
----------------

.. autoclass:: paraqus.CollectionWriter
   :members:
   :inherited-members:

ODBReader
---------
The ODBReader class is only useable in the Abaqus Python interpreter.

.. autoclass:: paraqus.abaqus.OdbReader
   :members:

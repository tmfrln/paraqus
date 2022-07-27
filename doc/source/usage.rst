Usage
=====

Usage with pure Python
----------------------

The general workflow for the usage of paraqus always includes the following steps:

- Create one or more ``ParaqusModel`` instances, representing the geometry and data that will be exported to vtk
- Create a writer for the desired file format (``AsciiWriter`` or ``BinaryWriter``)
- Optional: Create a ``CollectionWriter`` to connect vtk files based on multiple ``ParaqusModel`` instances, e.g. when they represent different time steps for the same model
- Write the vtk files to disk

Have a look at the pure python examples to learn how to create a ``ParaqusModel`` from scratch and how to write a vtu file based on it.

============================     ========
Example                          Contents
============================     ========
example_model_creation_01.py     - Creating a simple model
                                 - Exporting the model as a vtu file
----------------------------     --------
example_model_creation_02.py     - Adding field data to a model

example_model_creation_03.py     - Adding node and element groups to a model

example_model_creation_04.py     - Using a CollectionWriter to group multiple vtu files
                                   for different parts of the same model

example_model_creation_05.py     - Using a CollectionWriter to group multiple vtu files
                                   for different time steps

============================     ========

Usage with Abaqus
-----------------

When used to export models from Abaqus, the creation of the ``ParaqusModel`` instances is handled by the ``ODBReader`` class. The following steps do not change compared to the usage with pure python.

.. toctree::
   :maxdepth: 1

   example_cylindrical_billet
   example_aluminum_failure
   example_rivet_forming
   example_cylindrical_billet_adaptive


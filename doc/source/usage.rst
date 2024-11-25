Usage
=====

Usage with Python alone
-----------------------

The general workflow for the usage of Paraqus always includes the following steps:

- Create one or more ``ParaqusModel`` instances, representing the geometry and data that will be exported to *vtk*.
- Create a writer for the desired file format (``AsciiWriter`` or ``BinaryWriter``).
- Optional: create a ``CollectionWriter`` to connect *vtk* files based on multiple ``ParaqusModel`` instances, e.g. when they represent different time steps for the same model.
- Write the *vtk* files to disk.

Have a look at the pure Python examples (located in the subdirectory ``examples`` of Paraqus) to learn how to create a ``ParaqusModel`` from scratch and how to write a *vtk* file based on it.

===================================================================================================================     ==========================================================
Example                                                                                                                 Contents
===================================================================================================================     ==========================================================
`example_model_creation_01.py <https://github.com/tmfrln/paraqus/blob/main/examples/example_model_creation_01.py>`_     - Creating a simple model
                                                                                                                        - Exporting the model as a vtu file

`example_model_creation_02.py <https://github.com/tmfrln/paraqus/blob/main/examples/example_model_creation_02.py>`_     - Adding field data to a model

`example_model_creation_03.py <https://github.com/tmfrln/paraqus/blob/main/examples/example_model_creation_03.py>`_     - Adding node and element groups to a model

`example_model_creation_04.py <https://github.com/tmfrln/paraqus/blob/main/examples/example_model_creation_04.py>`_     - Using a CollectionWriter to group multiple vtu files
                                                                                                                          for different parts of the same model

`example_model_creation_05.py <https://github.com/tmfrln/paraqus/blob/main/examples/example_model_creation_05.py>`_     - Using a CollectionWriter to group multiple vtu files
                                                                                                                          for different time steps

===================================================================================================================     ==========================================================

Usage with Abaqus
-----------------

When used to export models from Abaqus, the creation of the ``ParaqusModel`` instances is handled by the ``ODBReader`` class. The following steps do not change compared to the usage with pure Python. The following examples demonstrate how to use Paraqus with Abaqus, and need a working Abaqus installation to run. 

In general, the Abaqus input files must be downloaded and an Abaqus analysis must be performed for each example. Detailed instructions can be found in the individual Python files. It is recommended to run the Abaqus analysis for each example, and then look at the output database to get a feel for the model. Only then should you go through the Python code and try to understand what each line does, being able to reference e.g. part names with the output database.

At the end of each of the Abaqus tutorials, an exemplary pipeline for Paraview is described to visualize the results.

=====================================================================================================================================================     ===============================================================================
Example                                           Contents
=====================================================================================================================================================     ===============================================================================
`example_abaqus_cylindrical_billet.py <https://github.com/tmfrln/paraqus/blob/main/examples/example_abaqus_cylindrical_billet.py>`_                       - Using an ODBReader to export results from an Abaqus odb.
                                                                                                                                                          - Exporting field outputs
                                                                                                                                                          - Exporting node and element groups

`example_abaqus_cylindrical_billet_adaptive.py <https://github.com/tmfrln/paraqus/blob/main/examples/example_abaqus_cylindrical_billet_adaptive.py>`_     - Using a CollectionWriter to combine exports from multiple output databases
                                                                                                                                                          - Specifying time offsets to store correct time values for each result

`example_abaqus_aluminum_bending.py <https://github.com/tmfrln/paraqus/blob/main/examples/example_abaqus_aluminum_bending.py>`_                           - Export of results for shell elements
                                                                                                                                                          - Fields that are not defined at all nodes/elements

`example_abaqus_rivet_forming <https://github.com/tmfrln/paraqus/blob/main/examples/example_abaqus_rivet_forming.py>`_                                    - CEL elements
                                                                                                                                                          - Large models, parallel *vtk* files

`example_abaqus_extrusion <https://github.com/tmfrln/paraqus/blob/main/examples/example_abaqus_extrusion.py>`_                                            - User materials
                                                                                                                                                          - Exporting large numbers of frames for video animations

=====================================================================================================================================================     ===============================================================================



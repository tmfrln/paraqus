Example application: Upsetting of a cylindrical billet
======================================================

This example demonstrates the Paraqus workflow for an axisymmetric problem including multiple element sets.

Running the example problem
---------------------------

The example is based on a thermo-mechanically coupled billet upsetting process simulation from the Abaqus example library. For a detailed description of the problem, we refer to the Abaqus documentation. To obtain the input file defining the problem, create a new folder in which you want to store the example files, and in that folder run the following command::

   abaqus fetch job=cylbillet_cax4rt_slow_dense.inp
   
Make sure the input file is in the folder, then run Abaqus to solve the problem and generate the output database. The command to run Abaqus could look like this::

   abq21 job=cylbillet_cax4rt_slow_dense interactive
   
Since this is just a small toy example it should only take some seconds for the solver to finish the job. A new file ``cylbillet_cax4rt_slow_dense.odb`` has been generated in your folder (besides a bunch of other files) that will be needed in the following.


Exporting the results to the vtk format
---------------------------------------

Start Abaqus CAE, and set the work directory to the folder you created in the beginning of this tutorial. Then execute the script ``example_cylindrical_billet.py`` (located in the ``examples`` folder). 
We will first create an instance of the ``ODBReader`` class. This class provides the interface to the output database. For each field that we wanto to export, we add a field export request via the method ``ODBReader.add_field_export_request()``.
In addition, we add some element sets via ``ODBReader.add_set_export_request()``. Later, this will allow us to have a closer look at the elements defined in these sets.
Then we create an instance of the ``BinaryWriter`` class, which is used to write data (extracted by the ``ODBReader``) to a binary-encoded vtk file. 
Finally, we call ``ODBReader.read()``. This method returns an iterator, which yields a ``ParaqusModel`` for each part instance in the output database. Therefore, we loop over the result, even when we only expect one model.
This also means that at any point in time, there exists only one ``ParaqusModel``, which is memory-efficient. In our example, we pass each of these models to the writer method ``write()``, which creates the vtk-file, before extracting the next model.

Look at what you have done!
---------------------------

Here will follow some instructions on how to visualize the results in Paraview.

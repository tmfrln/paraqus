Example application: Upsetting of a cylindrical billet with mesh-to-mesh solution mapping
=========================================================================================

This example demonstrates the Paraqus workflow for a problem with remeshing and mesh-to-mesh solution mapping.

Running the example problem
---------------------------

This example is based on the same billet upsetting process simulation we have seen before but extended by a remeshing step with mesh-to-mesh solution mapping in Abaqus/Standard. 
Hence, the problem will result in two different odb-files that will be merged into one single pvd-file in the course of this tutorial. 
Again, to obtain the input file defining the problem, navigate to a folder where you want to store the example files (a new folder is recommended), and in that folder run the following commands::

   abaqus fetch job=billet_case1_std_coarse.inp
   abaqus fetch job=billet_case1_std_coarse_rez.inp
   abaqus fetch job=billet_coarse_elem.inp
   abaqus fetch job=billet_coarse_nodes.inp
   abaqus fetch job=billet_coarse_elem_rez.inp
   abaqus fetch job=billet_coarse_nodes_rez.inp

Make sure the input files are in the folder, then run Abaqus to solve the problem and generate the output database. The commands to run Abaqus could look like this::

   abaqus job=billet_case1_std_coarse interactive
   abaqus job=billet_case1_std_coarse_rez oldjob=billet_case1_std_coarse interactive
	
As you might expect from the problem's name, the mesh is quite coarse and running the simulation should only take some seconds.
The files ``billet_case1_std_coarse.odb`` and ``billet_case1_std_coarse_rez.odb`` have been generated in your folder (besides a bunch of other files) and will be converted into the vtk file format in the following.

Exporting the results to the vtk format
---------------------------------------

Start Abaqus CAE, and set the work directory to the folder where the simulation output database files are located. Then execute the script ``example_cylindrical_billet_adaptive.py`` (located in the ``examples`` folder). 
First we initialize a ``BinaryWriter``. If you prefer your vtu-files in ASCII format, you can easily switch to an ``AsciiWriter``. Since we want to merge multiple frames of multiple odb-files into one new file, we need a ``CollectionWriter`` in addition here, that works just like a context manager.
By looping over the different ODB-files we initialize an individual ``ODBReader`` for each of them. The parameter ``time_offset`` is needed to have a consecutive simulation time over all exported frames.
Now, as done in other tutorials before, we can generate our models and export them. Don't forget to update the ``time_offset`` after one odb-file has been processed.

Look at what you have done!
---------------------------

The exported vtu-files are located in an automatically created folder ``vtk_output/vtu``. In addition, the folder ``vtk_output`` contains a file ``Compression Test.pvd`` that can be openend in *Paraview*.

The visualisation pipeline looks as follows:

- Apply deformation (*Warp By Vector* filter)
- Rotate model around z-axis by -90° (*Transform* filter)
- Reflect model at y-axis (*Reflect* filter)
- Rotate model around y-axis by 90° (*Transform* filter)
- Create a surface (*Extract Surface* filter)
- Revolve around z-axis (*Rotational Extrusion* filter)
- Extrapolate data from cells to point (*Cell Data to Point Data* filter)
- Coloring according to the variable ``S_mises`` (choose in the menu for the last filter)

Output looks like this:

.. image:: /images/screenshot_cylindrical_billet_adaptive.png
  :width: 800
  :alt: Screenshot of the deformed billet from Paraview


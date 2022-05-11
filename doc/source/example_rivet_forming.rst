Example application: Rivet Forming
==================================

This example demonstrates the Paraqus workflow for a problem that includes different element types.

Running the example problem
---------------------------

The example is based on a problem *rivet forming* from the abaqus example manual. For a detailed description of the problem, we refer to the Abaqus documentation. To obtain the input file defining the problem, navigate to a folder where you want to store the example files (a new folder is recommended), and in that folder run the following command::

   abaqus fetch job=rivet_forming_cel.inp

Make sure the input file is in the folder, then run Abaqus to solve the problem and generate the output database. The command to run Abaqus could look like this::

   abq21 job=Rivet-Forming-CEL parallel=domain domains=8 cpus=8 mp_mode=threads interactive
	
Make sure not to use more domains/cpus than your machine actually has. Get a cup of coffee and proceed with this example after Abaqus finished solving the problem.

**Caution**: This is not a small toy example, so solving might take more than an hour on older machines/laptops. If you want to test the features of paraqus but are not interested in the full result, you can change the step time to only simulate part of the forming process. To do this, locate the following section in the input file::

   *Step, name=Step-1, nlgeom=YES
   Displace dies
   *Dynamic, Explicit
   , 0.001

and change the value from 0.001 to a smaller one, e.g. 0.0001 to simulate the first 10% of the process.


Exporting the results to the vtk format
---------------------------------------

Start Abaqus CAE, and set the work directory to the folder where the simulation output database ``Rivet-Forming-CEL.odb`` is located. Then execute the script ``example_rivet_forming.py`` (located in the ``examples`` folder). 
We will first create an instance of the ``ODBReader`` class. This class provides the interface to the output database. For each field that we wanto to export, we add a field export request via the method ``ODBReader.add_field_export_request()``.
Then we create an instance of the ``AsciiWriter`` class, which is used to write data (extracted by the ``ODBReader``) to a plain-text vtk file. 
Finally, we call ``ODBReader.read()``. This method returns an iterator, which yields a ``ParaqusModel`` for each part instance in the output database. Therefore, we loop over the result, even when we only expect one model.
This also means that at any point in time, there exists only one ``ParaqusModel``, which is memory-efficient. In our example, we pass each of these models to the writer method ``write()``, which creates the vtk-file, before extracting the next model.

**Note**: Paraview supports parallel files for *pieces* of a model. We are setting the attribute ``number_of_pieces`` of the writer to four, generating four separate files for each part instance. Each file contains a fourth of the instance.

The model has roughly 200,000 degrees of freedom - exporting should take about one minute.


Look at what you have done!
---------------------------

The exported vtu-file is located in an automatically created folder ``vtk_output``. The folder contains a subfolder ``rivel_forming_cel/vtu/EULERIAN-1_0_0`` (based on the odb and instance name). In this example, we will use *paraview* to visualize the exported results. 

Our goal is to visualize the equivalent plastic strain in the cylinder. Due to the nature of the CEL method, the cylinder geometry is represented by the isosurface ``material volume fraction = 0.5``. The corresponding Abaqus output is called ``EVF_ASSEMBLY_EULERIAN-1_MAT-1-1``, and is an element-based quantity.

The visualisation pipeline looks as follows:

- Merging of the parallel files (*CleantoGrid* filter)
- Mapping of the volume fraction from element centers to nodes (*CellDatatoPointData* filter)
- Extraction of the isosurface representing the boundary of the rivet (*Countour* filter)
- Coloring according to the variable ``PEEQVAVG`` (choose in the menu for the last filter)

Output looks like this:
![output for rivet forming examples](images/screenshot_example_rivet_forming.png)


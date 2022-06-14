Example application: Bending of an Aluminum Profile
===================================================

This example demonstrates how to work with shell elements.

Running the example problem
---------------------------

The example is based on the problem *Progressive failure analysis of thin-wall aluminum extrusion under quasi-static and dynamic loads* from the abaqus example manual. For a detailed description of the problem, we refer to the Abaqus documentation. To obtain the input file defining the problem, navigate to a folder where you want to store the example files (a new folder is recommended), and in that folder run the following command::

   abaqus fetch job=threepointbending_alextrusion.inp

Make sure the input file is in the folder, then run Abaqus to solve the problem and generate the output database. The command to run Abaqus could look like this::

   abq21 job=threepointbending_alextrusion parallel=domain domains=8 cpus=8 mp_mode=threads interactive
	
Make sure not to use more domains/cpus than your machine actually has. The example might take a little while to run - on an older Laptop with 2 cpus, it took us about 15 minutes to solve.


Structure of the output database
--------------------------------

**Part structure**

The structure of the example problem can be inspected in Abaqus CAE. Although the problem deals with contact between four different bodies (the aluminum extrusion, two rigid holders and a rigid punch), the output database contains only one part instance ``PART-1-1``. Instead of part instances, the odb contains node and element sets for each of the bodies, which are stored within the part instance.

**Element types**

The aluminum extrusion is represented by shell elements. At each integration point, these shell elements contain multiple *section points* at different positions along the element thickness. For example, if a beam element with one integration point is subjected to bending, the strain at the section points towards the bottom might be compressive, while stretching occurs towards the top. The odb contains values for section points 1 and 5 (representing the bottom and top surface of the shells).

**Damage variables**

The example demonstrates different damage models within Abaqus, which eventually lead to the deletion of elements upon failure. We will focus on the variable ``STATUS``, which is initially 1 for all elements, and takes the value 0 if an element fails. Note that failed elements are still contained in the odb, and might show excessive distortion. 


Exporting the results to the vtk format
---------------------------------------

Start Abaqus CAE, and set the work directory to the folder where the simulation output database ``threepointbending_alextrusion.odb`` is located. Then execute the script ``example_aluminum_bending.py`` (located in the ``examples`` folder). 
We will first create an instance of the ``ODBReader`` class. This class provides the interface to the output database. For each field that we wanto to export, we add a field export request via the method ``ODBReader.add_field_export_request()``. The fields that are exported in this example are the displacements (``U``), the element status (``STATUS``), and the stresses (``S``). There are two export requests for the stresses: The first demonstrates the export of the values associated with section point 1. The second export demonstrates the reduction of all section point values at each quadrature point by choosing the section point with the highest absolute value.

**Remark**: The vtk format sadly does not support the association of different values with the two sides of a surface. The intuitive visualization of the different section point values on the different element sides is therefore not possible.

Next, we add some set export requests to the reader via the method ``ODBReader.add_set_export_request()``. The sets that we are exporting are the element sets indicating which element is part of which body. Note that the element sets are stored in the part instance, and we need to pass the part instance name as an optional argument. For assembly-level sets, this argument is simply omitted.


Next, we create an instance of the ``BinaryWriter`` class, which is used to write data (extracted by the ``ODBReader``) to a binary vtu file. 
Finally, we call ``ODBReader.read()``. This method returns an iterator, which yields a ``ParaqusModel`` for each part instance in the output database. Therefore, we loop over the result, even when we only expect one model (as we do in this case).
This also means that at any point in time, there exists only one ``ParaqusModel``, which is memory-efficient. In our example, we pass each of these models to the writer method ``write()``, which creates the vtu-file, before extracting the next model.



Inspecting the result in ParaView
---------------------------------

The exported vtu-file is located in an automatically created folder ``vtk_output``. The folder contains a subfolder ``Aluminum-Bending/vtu/`` with a file ``PART-1-1_0_0.vtu`` (based on the odb and instance name). In this example, we will use *ParaView* to visualize the exported results. 

Coloring based on the indicator fields, e.g. ``_group_P1_DOUBLECHAMBEREXTRUSION``, makes the individual bodies visible (and demonstrates what exported element sets look like).

The deformed system can be visualized with the *WarpByVector* filter. Since we only exported a single node vector field (``U``), the displacement field will be chosen as the input automatically. 

There is an immediate problem visible with the deformed configuration: Some elements show very large deformations. Choosing the field ``STATUS`` to color the part makes it clear, that the problem is caused by the elements which were damaged to failure. Since the status variable only assumes values of 0 or 1, a *threshold* filter with a minimum value of 0.5 for the status variable is used to remove the failed elements from the view.

**Remark**: The threshold filter also removes the holders and the punch, since the damage variable is not defined on the rigid bodies. If you prefer to keep them visible, use a maximum of 0.5 for the status variable in the threshold filter, and choose the option ``Invert``.

We can now color the deformed extrusion by the stress values we exported. Note that the field ``S_mises_absmax`` is either the same or greater than the field ``S_mises_sp1``, which represents the values at one section point.

.. image:: /images/screenshot_example_aluminum_bending.png
  :width: 800
  :alt: Screenshot of the deformed aluminum profile, colored according to the maximum von Mises stress.


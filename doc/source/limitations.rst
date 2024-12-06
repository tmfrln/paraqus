Known limitations
=================

This section lists some known limitations of Paraqus and/or the visualisation with the VTK file format.

**Abaqus functionality that does not work with Paraqus**

- Abaqus uses surface tensors for some field outputs. These tensors are associated with element faces, and therefore not directly applicable to the geometry cells you export with Paraqus. For now, surface tensors are not supported.


**Stuff Paraview/VTK can not handle to the best of our knowledge**

- Paraview/VTK does not support different values for different sides of a surface cell. This means that you can not visualize e.g. the different values at the upper/lower side of shell elements in the same view.

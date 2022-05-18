Known limitations
=================

**Abaqus functionality that does not work with Paraqus**

- Abaqus uses surface tensors for some field outputs. These tensors are associated with element faces, and therefore not directly applicable to the geometry cells we export. For now, surface tensors are not supported by Paraqus.


**Stuff Paraview can not handle to the best of our knowledge**

- Paraview does not support different values for different sides of a surface cell. This means that we can not visualize e.g. the different values at the upper/lower side of shell elements in the same view.

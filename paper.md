---
title: 'Paraqus: Exporting Finite Element Simulation Results from Abaqus to VTK'
tags:
  - finite elements
  - visualisation
  - vtk
  - abaqus
authors:
  - name: Tim Furlan
    corresponding: true
    orcid: 0000-0002-3337-5891
    equal-contrib: true
    affiliation: 1
  - name: Jonathan Stollberg
    orcid: 0000-0001-8383-2109
    equal-contrib: true
    affiliation: 1
  - name: Andreas Menzel
    orcid: 0000-0002-7819-9254
    equal-contrib: true
    affiliation: "1,2"
affiliations:
 - name: Institute of Mechanics, Department of Mechanical Engineering, TU Dortmund University, Leonhard-Euler-Str. 5, 44227 Dortmund, Germany
   index: 1
 - name: Division of Solid Mechanics, Department of Construction Sciences, Lund University, P.O. Box 118, SE-22100 Lund, Sweden
   index: 2
date: 02 February 2022
bibliography: paper.bib

---

# Summary

The finite element (FE) method is the tool of choice for the solution of different types of partial differential equations in the various fields of physics, such as solid mechanics, heat transfer, and electromagnetics. Visualisation of results plays a crucial role in the interpretation and analysis of simulation results, especially when complex and advanced problems are considered. Paraqus is a Python package that exports simulation results from the commercial FE software Abaqus to the open VTK file format, allowing researchers to use tried and tested pipelines for the visualisation, and to exchange results in a format that is independent of the software they were created with. Paraqus is modular in structure, therefore the VTK exporting capability can be used independently of Abaqus, and exporters for other FE software can be added as well. The Paraqus documentation is available at <https://paraqus.readthedocs.io>.


# Statement of need

Abaqus is an example of a commercial FE software that is widely used in the academic engineering community. ScienceDirect shows more than 7000 articles tagged with the keyword "Abaqus" and published in 2022. Exporting simulation results to the VTK format serves two purposes: The data can be shared with other researchers and users without access to expensive software, and specialised open source software like Paraview can be used to create visualisations that would be tedious or impossible to generate in the post-processing module of Abaqus.

A script for the export from Abaqus data to VTK format was published in @odb2vtk under the name ``odb2vtk``. This script offers limited options to customise export data, and only supports a subset of the finite elements available in Abaqus. AbaPy is a Python package that is not aimed solely at post-processing, but also at the automatic creation of Abaqus simulations [@abapy]. While AbaPy offers the option to export field outputs to VTK format, the greater range of applications comes with increased complexity. Paraqus falls in between these existing options: It is organised as a package with a small and intuitive api, yet allows a broad range of customisation of the exports, and writes the more efficient binary version of the VTK format. It also offers options to group exports from multiple simulations, time steps, or bodies, using Paraview's .pvd files. Paraqus also performs exports noticeably faster than AbaPy for larger models.


# Acknowledgements

The authors are grateful to Isabelle Noll and Lennart Sobisch for beta-testing Paraqus and providing valuable feedback on the examples and documentation.

# Funding

Paraqus was developed in the context of two projects funded by the German Research Foundation (DFG) under project IDs 403857741 and 278868966, which is gratefully acknowledged.

# References



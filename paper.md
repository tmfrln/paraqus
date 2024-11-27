---
title: 'Paraqus: Exporting Finite Element Simulation Results from Abaqus to VTK'
tags:
  - finite elements
  - visualization
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

The finite element (FE) method is one of the approaches available for solving different types of partial differential equations in the various fields of physics, such as solid mechanics, heat transfer, and electromagnetics. Visualization and manipulation of results plays a crucial role in the interpretation and analysis of simulation results, especially when complex and advanced problems are considered. Paraqus is a Python package that exports simulation results from the commercial FE software Abaqus to the open VTK file format, allowing researchers to use tried and tested pipelines for the visualization, and to exchange results in a format that is independent of the software they were created with. Paraqus is modular in structure, therefore the VTK exporting capability can be used independently of Abaqus, and exporters for other FE software can be added as well. The Paraqus documentation is available at <https://paraqus.readthedocs.io>.

# Statement of need

Abaqus is an example of commercial FE software that is widely used in the academic engineering community. ScienceDirect shows more than 7000 articles tagged with the keyword "Abaqus" and published in 2022. Exporting simulation results to the VTK format serves two purposes: 
- the data can be shared with other researchers and users without access to expensive software, and 
- specialised open source software like ParaView can be used to create visualizations that would be tedious or impossible to generate in the post-processing module of Abaqus.

Some software packages similar to Paraqus have been released over the last years. However, these tools suffer from great limitations and are, therefore, not as versatile and straightforward as Paraqus. A script to export Abaqus results to VTK format was published in @odb2vtk under the name ``odb2vtk``. This script offers limited options to customize the export data, and supports only a subset of the finite elements available in Abaqus. *AbaPy* is a Python package that is not aimed solely at post-processing, but also at the automatic creation of Abaqus models and run of Abaqus simluations [@abapy]. Although *AbaPy* offers the option to export field outputs to VTK format, the wider range of applications comes with increased complexity. Paraqus falls between these existing options: it is organized as a package with a small and intuitive API, but allows a wide range of customization of exports, and writes the more efficient binary version of the VTK format. It also provides options to group exports from multiple simulations, time steps, or bodies, using ParaView Data (PVD) files. Furthermore, Paraqus performs exports noticeably faster than *AbaPy*, especially in case of large models.

# Contributions

**Tim Furlan:** Conceptualization; Software - Design, Implementation (focus on reading Abaqus ODB files), Documentation; Writing - Original Draft; Example generation. **Jonathan Stollberg:** Conceptualization; Software - Design, Implementation (focus on writing VTK files), Documentation; Writing - Original Draft; Example generation. **Andreas Menzel:** Conceptualization; Supervision - Project direction; Writing - Review & Editing; Example generation.

# Acknowledgements

The authors are grateful to Isabelle Noll and Lennart Sobisch for beta-testing Paraqus and providing valuable feedback on the examples and documentation.

# Funding

Paraqus was developed in the context of two projects funded by the German Research Foundation (DFG) under project IDs 403857741 and 278868966, which is gratefully acknowledged.

# References



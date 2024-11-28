# -*- coding: utf-8 -*-
#
#   Paraqus - A VTK exporter for FEM results.
#
#   Copyright (C) 2022, Furlan, Stollberg and Menzel
#
#    This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along with this program. If not, see https://www.gnu.org/licenses/.

"""
This script sets up a 2d example model for an extrusion process, and
performs the calculations in Abaqus. The material model is provided as
as separate Abaqus user material, i.e. a Fortran file. This example is
chosen to demonstrate the capability of Paraqus to export results based
on user materials.

The user material describes large-strain plasticity with isotropic
hardening. The details of the plasticity formulations are not discussed
at this point, since the example will work with pretty much any user
material. The only important information is the ordering of the
internal state variables (SDVs), which will be exported to the .vtu
file:

 SDV #  |             Description
-------------------------------------------------
    1   | Equivalent plastic strain
  2-10  | Plastic part Fp of deformation gradient
   11   | Norm of the deviatoric part of Fp

Special thanks go to Lennart Sobisch for contributing this example to
Paraqus.

Note: To run the example, make sure that the Fortran file
UMAT_VMPlasti_LargeStrain.f is present in the working directory!

To run this example, open a terminal in the example folder and type
    abaqus cae noGUI=run_example_abaqus_extrusion.py

Alternatively, you can also use the 'run script' menu item in Abaqus CAE
to run it. Make sure to set the correct working directory (see above).

"""
import os

from abaqus import *
from part import *
from material import *
from section import *
from assembly import *
from step import *
from mesh import *
from interaction import *
from load import *
import mesh
from job import *
import numpy as np


routineDir = r"example_abaqus_extrusion_umat.f"

assert os.path.isfile(routineDir), """Fortran subroutine file not found
 in the working directory. Change the working directory, or copy the
 file to the working directory you want to use."""


# Material definition
E = 210000.
nu = 0.3
q0 = 450
q_sat = 750
alpha_u = 0.06
h = 0.129


# Simulation time
time = 10

# Time increment
dtMax = 1e-1

lc_m = 3.
lc_e = 2.

# Load
disp = 50.

friction = 0.0

# Geometry
d0 = 35.0
d1 = 24.0
le = 60.0
l1 = 60.0
l2 = 92.1
lG = 152.1
radius = 20.0

# Job Name
jobName = "extrusion"

# Clear model
Mdb()

modelName = "extrusion"
mdb.models.changeKey(fromName="Model-1", toName=modelName)

model = mdb.models[modelName]

# ----------------------------------------------------------------------
#  Parts
# ----------------------------------------------------------------------

# Primary part
sketch = model.ConstrainedSketch(name="matrixSketch", sheetSize=200.)

sketch.sketchOptions.setValues(viewStyle=AXISYM)
sketch.ConstructionLine(point1=(0.0, -100.0), point2=(0.0, 100.0))
sketch.Line(point1=(d1/2.0, 0.0), point2=(d1/2, l1))
sketch.Line(point1=(d1/2, l1), point2=(d0/2, l2))
sketch.Line(point1=(d0/2, l2), point2=(d0/2, lG))
sketch.Line(point1=(d0/2, lG), point2=(d0/2+20., lG))
sketch.Line(point1=(d0/2+20., lG), point2=(d0/2+20., 0.0))
sketch.Line(point1=(d0/2+20.0, 0.0), point2=(d1/2, 0.0))

x0 = [d0/2, 0.0]
x1 = [d0/2, l1]
x2 = [d1/2, l2]
x3 = [d1/2, lG]

g = sketch.geometry
sketch.FilletByRadius(radius=radius,
                      curve1=g[4],
                      nearPoint1=(x1[0] + (x2[0]-x1[0])*0.75,
                                  x1[1] + (x2[1]-x1[1])*0.75),
                      curve2=g[5],
                      nearPoint2=(x2[0] + (x3[0]-x2[0])*0.25,
                                  x2[1] + (x3[1]-x2[1])*0.25))

sketch.FilletByRadius(radius=radius,
                      curve1=g[3],
                      nearPoint1=(x0[0] + (x1[0]-x0[0])*0.75,
                                  x0[1] + (x1[1]-x0[1])*0.75),
                      curve2=g[4],
                      nearPoint2=(x1[0] + (x2[0]-x1[0])*0.25,
                                  x1[1] + (x2[1]-x1[1])*0.25))

matrixPart = model.Part(name="matrixPart",
                        dimensionality=AXISYMMETRIC,
                        type=DEFORMABLE_BODY)
matrixPart.BaseShell(sketch=sketch)
del model.sketches["matrixSketch"]

sketch = model.ConstrainedSketch(name="extrudeSketch", sheetSize=200.0)
sketch.sketchOptions.setValues(viewStyle=AXISYM)
sketch.ConstructionLine(point1=(0.0, -100.0), point2=(0.0, 100.0))
sketch.Line(point1=(0.0, 0.0), point2=(d0/2-0.1, 0.0))
sketch.Line(point1=(d0/2-0.1, 0.0), point2=(d0/2-0.1, l1))
sketch.Line(point1=(d0/2-0.1, l1), point2=(0.0, l1))
sketch.Line(point1=(0.0, l1), point2=(0.0, 0.0))

extrudePart = model.Part(name="extrudePart",
                         dimensionality=AXISYMMETRIC,
                         type=DEFORMABLE_BODY)
extrudePart.BaseShell(sketch=sketch)
del model.sketches["extrudeSketch"]


matrixPart.Set(faces=matrixPart.faces, name="matrixCells")
extrudePart.Set(faces=extrudePart.faces, name="extrudeCells")

upperExtrudeFace = extrudePart.edges.findAt(((d0/4, le, 0.0),))
extrudePart.Set(edges=upperExtrudeFace, name="upperExtrudeFace")

leftExtrudeFace = extrudePart.edges.findAt(((0.0, le/2, 0),))
extrudePart.Set(edges=leftExtrudeFace, name="leftExtrudeFace")

rightExtrudeFace = extrudePart.edges.findAt(((d0/2-0.1, le/2, 0),))
extrudePart.Set(edges=rightExtrudeFace, name="rightExtrudeFace")

masterContactFace1 = matrixPart.edges.findAt(((d1/2, l1/2, 0),))
masterContactFace2 = matrixPart.edges.findAt(((x1[0] + (x2[0]-x1[0])*0.5,
                                               x1[1] + (x2[1]-x1[1])*0.5,
                                               0.),))
masterContactFace3 = matrixPart.edges.findAt(
    ((d0/2, x2[1] + (x3[1]-x2[1])*0.5, 0.),))
matrixPart.Set(edges=(masterContactFace1,
                      masterContactFace2,
                      masterContactFace3,
                      ),
               name="masterContactFace")


# ----------------------------------------------------------------------
#  Materials and Sections
# ----------------------------------------------------------------------

extrudeMat = model.Material(name="extrudeMaterial")
extrudeMat.Depvar(n=11)
extrudeMat.UserMaterial(type=MECHANICAL,
                        mechanicalConstants=(E, nu, q0, q_sat, alpha_u, h))


model.HomogeneousSolidSection(name="extrudeSection",
                              material="extrudeMaterial",
                              thickness=None)

extrudePart.SectionAssignment(region=extrudePart.sets["extrudeCells"],
                              sectionName="extrudeSection",
                              offset=0.0,
                              offsetType=MIDDLE_SURFACE,
                              offsetField="",
                              thicknessAssignment=FROM_SECTION)


matrixMat = model.Material(name="matrixMaterial")
matrixMat.Elastic(table=((1000000.0, 0.3), ))

model.HomogeneousSolidSection(name="matrixSection",
                              material="matrixMaterial",
                              thickness=None)

matrixPart.SectionAssignment(region=matrixPart.sets["matrixCells"],
                             sectionName="matrixSection",
                             offset=0.0,
                             offsetType=MIDDLE_SURFACE,
                             offsetField="",
                             thicknessAssignment=FROM_SECTION)

# ----------------------------------------------------------------------
#  Assembly
# ----------------------------------------------------------------------

assembly = model.rootAssembly

extrudeInstance = assembly.Instance(
    name="extrudeInstance", part=extrudePart, dependent=ON)
matrixInstance = assembly.Instance(
    name="matrixInstance", part=matrixPart, dependent=ON)
assembly.translate(instanceList=("extrudeInstance", ), vector=(0.0, 95.0, 0.0))

# ----------------------------------------------------------------------
#  Step
# ----------------------------------------------------------------------

step = model.StaticStep(name="Step-1",
                        previous="Initial",
                        initialInc=dtMax,
                        maxInc=dtMax,
                        maxNumInc=10000,
                        nlgeom=ON)

step.setValues(timePeriod=time)

model.fieldOutputRequests["F-Output-1"].setValues(variables=("S",
                                                             "PE",
                                                             "PEEQ",
                                                             "PEMAG",
                                                             "LE",
                                                             "U",
                                                             "RF",
                                                             "CF",
                                                             "CSTRESS",
                                                             "CDISP",
                                                             "SDV"))

model.fieldOutputRequests["F-Output-1"].setValues(numIntervals=time*10)

# ----------------------------------------------------------------------
#  Mesh
# ----------------------------------------------------------------------

elemType1 = mesh.ElemType(elemCode=CAX4, elemLibrary=STANDARD)
elemType2 = mesh.ElemType(elemCode=CAX3, elemLibrary=STANDARD)

matrixPart.setElementType(regions=matrixPart.sets["matrixCells"],
                          elemTypes=(elemType1, elemType2))

matrixPart.seedPart(size=lc_m,
                    deviationFactor=0.1,
                    minSizeFactor=0.1)

matrixPart.generateMesh()

extrudePart.setElementType(regions=extrudePart.sets["extrudeCells"],
                           elemTypes=(elemType1, elemType2))

extrudePart.seedPart(size=lc_e,
                     deviationFactor=0.1,
                     minSizeFactor=0.1)

extrudePart.generateMesh()

assembly.regenerate()

# ----------------------------------------------------------------------
# Boundary and initial conditions
# ----------------------------------------------------------------------

model.DisplacementBC(name="matrixFix",
                     createStepName="Step-1",
                     region=assembly.sets["matrixInstance.matrixCells"],
                     u1=0.0, u2=0.0, ur3=UNSET,
                     amplitude=UNSET,
                     fixed=OFF,
                     distributionType=UNIFORM,
                     fieldName="",
                     localCsys=None)

model.DisplacementBC(name="xFix",
                     createStepName="Step-1",
                     region=assembly.sets["extrudeInstance.leftExtrudeFace"],
                     u1=0.0, u2=UNSET, ur3=UNSET,
                     amplitude=UNSET,
                     fixed=OFF,
                     distributionType=UNIFORM,
                     fieldName="",
                     localCsys=None)


model.DisplacementBC(name="Load",
                     createStepName="Step-1",
                     region=assembly.sets["extrudeInstance.upperExtrudeFace"],
                     u1=UNSET, u2=-disp, ur3=UNSET,
                     amplitude=UNSET,
                     fixed=OFF,
                     distributionType=UNIFORM,
                     fieldName="",
                     localCsys=None)

# Contact

intProp = model.ContactProperty("IntProp-1")

intProp.NormalBehavior(pressureOverclosure=HARD, allowSeparation=ON,
                       constraintEnforcementMethod=DEFAULT)


intProp.TangentialBehavior(formulation=PENALTY, directionality=ISOTROPIC,
                           slipRateDependency=OFF, pressureDependency=OFF,
                           temperatureDependency=OFF, dependencies=0,
                           table=((friction, ), ), shearStressLimit=None,
                           maximumElasticSlip=FRACTION, fraction=0.005,
                           elasticSlipStiffness=None)

if friction == 0.0:
    intProp.tangentialBehavior.setValues(formulation=FRICTIONLESS)


model.ContactStd(name="Int-1", createStepName="Initial")
model.interactions["Int-1"].includedPairs.setValuesInStep(stepName="Initial",
                                                          useAllstar=ON)
(model.interactions["Int-1"].
 contactPropertyAssignments.appendInStep(stepName="Initial",
                                         assignments=((GLOBAL,
                                                       SELF,
                                                       "IntProp-1"),)))

# ----------------------------------------------------------------------
# Job
# ----------------------------------------------------------------------

job = mdb.Job(name=jobName,
              model="extrusion",
              description="",
              type=ANALYSIS,
              atTime=None,
              waitMinutes=0,
              waitHours=0,
              queue=None,
              memory=90,
              memoryUnits=PERCENTAGE,
              getMemoryFromAnalysis=True,
              explicitPrecision=SINGLE,
              nodalOutputPrecision=FULL,
              echoPrint=OFF,
              modelPrint=OFF,
              contactPrint=OFF,
              historyPrint=OFF,
              userSubroutine=routineDir,
              scratch="",
              resultsFormat=ODB,
              multiprocessingMode=DEFAULT,
              numCpus=1,
              numGPUs=0)

job.submit()

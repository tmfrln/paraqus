# -*- coding: utf-8 -*-

from abaqus import *
from abaqusConstants import *

import regionToolset
import math

# Open new model database
outputModel = Mdb()

modelName = 'modelTestInterface'

# Name the model
mdb.Model(name=modelName)

# Assign model and assembly to variables
model = mdb.models[modelName]
modelAssembly = model.rootAssembly

# Display assembly
session.viewports['Viewport: 1'].setValues(displayedObject=modelAssembly)


# Create an elastic material
import material
matElastic = model.Material(name='Elastic Material')
matElastic.Density(table=((0.0003,), ))
matElastic.Elastic(table=((70000.0, 0.3), ))

# Create a rectangular part
import sketch
import part

partSketch = model.ConstrainedSketch(name='Part Sketch',sheetSize=100.0)
partSketch.rectangle(point1=(0,0),point2=(1,1))
rectPart = model.Part(name='Rectangular Part', dimensionality=TWO_D_PLANAR,
                      type=DEFORMABLE_BODY)
rectPart.BaseShell(sketch=partSketch)


# Section Assignment
import section

elasticSection = model.HomogeneousSolidSection(
    name='Elastic Section',material='Elastic Material')

# Part region
regionElastic = regionToolset.Region(faces=rectPart.faces)

# Assign sections to regions
rectPart.SectionAssignment(
    region=regionElastic, sectionName='Elastic Section')

# Part set
edgeLeft = rectPart.edges.findAt(((0.0,0.5,0.0),))
rectPart.Set("Left Edge", edges=edgeLeft)

# Part surface
edgeRight = rectPart.edges.findAt(((1.0,0.5,0.0),))
rectPart.Surface("Right Edge", side1Edges=edgeRight)

# Assembly
import assembly

rectInstance = modelAssembly.Instance(name='Rectangular Instance',
    part=rectPart,dependent=ON)

# Mesh the part
import mesh

# Choose element type
elemType1 = mesh.ElemType(elemCode=CPS3, elemLibrary=STANDARD)
elemType2 = mesh.ElemType(elemCode=CPS4, elemLibrary=STANDARD)

meshFaces = rectPart.faces
meshRegion = regionToolset.Region(faces=meshFaces)

rectPart.setElementType(regions=meshRegion,elemTypes=(elemType1,elemType2))

elemSize = .5; # should create a 2x2 mesh
rectPart.seedPart(size=elemSize,constraint=FINER)
rectPart.setMeshControls(regions=rectPart.faces,technique=FREE)

rectPart.generateMesh()

# Step
import step

duration = 1
StepApplyForce = model.StaticStep(name='Apply Force',
    previous='Initial', description='Well, guess',
    nlgeom=OFF,timePeriod=duration)

Step2 = model.StaticStep(name='Another Step',
    previous='Apply Force', description='Well, guess',
    nlgeom=OFF,timePeriod=duration)

# Boundary conditions

# Inner edge fixed in r-direction
partLeftEdge = rectInstance.edges.findAt(((0.0,0.5,0.0),))
partLeftEdgeRegion = regionToolset.Region(edges=partLeftEdge)
BCLeftEdge = model.DisplacementBC(name='BC Left Edge',
    createStepName='Apply Force', region=partLeftEdgeRegion, u1=0.0)

# Bottom edge fixed in z-direction
partBottomEdge = rectInstance.edges.findAt(((0.5,0.0,0.0),))
partBottomEdgeRegion = regionToolset.Region(edges=partBottomEdge)
BCBottomEdge = model.DisplacementBC(name='BC Bottom Edge',
    createStepName='Apply Force', region=partBottomEdgeRegion, u2=0.0)
# Set for tests
modelAssembly.Set("Bottom Edge", edges=partBottomEdge)

# Force applied to top edge
partTopEdge = rectInstance.edges.findAt(((0.5,1.0,0.0),))
partTopEdgeSequence = (partTopEdge,) # Surfacetraction requires surface type
partTopEdgeRegion = modelAssembly.Surface(side1Edges=partTopEdgeSequence, name='Top Surface')

loadTraction = model.SurfaceTraction(name='Traction Top Edge',
    createStepName='Apply Force', region=partTopEdgeRegion, magnitude=10.0,
    directionVector=((0.0, 0.0, 0.0), (0.0, 1.0, 0.0)),
    distributionType=UNIFORM, field='', localCsys=None, traction=GENERAL)

# Output requests
model.FieldOutputRequest(name='FieldOut',
    createStepName='Apply Force', variables=('S', 'E', 'UT', 'COORD'),
    frequency=LAST_INCREMENT)


# Create Job
import job

jobElementTest = mdb.Job(name='element_test_current',     model=modelName,
    type=ANALYSIS, description='Uniform stress state in a rectangular body',
    numCpus=1, historyPrint=OFF)

jobElementTestOld = mdb.Job(name='element_test_old',     model=modelName,
    type=ANALYSIS, description='Uniform stress state in a rectangular body',
    numCpus=1, historyPrint=OFF)

jobElementTest.writeInput()

jobElementTestOld.writeInput()


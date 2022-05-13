# Spherical Indentation Identification Tool (SIIT)
from abaqus import mdb
from math import *
from abaqusConstants import *
from caeModules import *
from abaqus import session

def strsPstrn(elasModulus = 120000.0, yiled = 200.0, hardIndx = 0.1 ):
    print('the elasModulus is '+str(elasModulus)+', the yield stress is '+str(yiled)
           +', the hardIndx is '+str(hardIndx))
    sPstable = ()
    for i in range(200):
     
        pstrnTemp = float(i)/200.0        
        strsTemp = yiled*(1.0+elasModulus/yiled*pstrnTemp)**hardIndx         
        sPstable = sPstable + ((strsTemp, pstrnTemp),)
     
    return sPstable
    
def strsPstrnVoce(elasModulus = 120000.0, yiled = 200.0, AVoce = 200.0, mVoce = 20.0):
    print('the elasModulus is '+str(elasModulus)+', the yield stress is '+str(yiled)
          +', A is '+str(Avoce)+', m is '+str(mVoce))
    sPstable = ()
    for i in range(200):
     
        pstrnTemp = float(i)/200.0         
        strsTemp = yiled + AVoce*(1.0-exp(-mVoce*pstrnTemp))         
        sPstable = sPstable + ((strsTemp, pstrnTemp),)
     
    return sPstable   

def strsPstrnVocepp(elasModulus = 120000.0, yiled = 200.0, AVocepp = 200.0, mVocepp = 20.0,
                    Bpp = 200.0, Cpp = 200.0):
    print('the elasModulus is '+str(elasModulus)+', the yield stress is '+str(yiled)+', A is '
            +str(AVocepp)+', m is '+str(mVocepp)+', B is '+ str(Bpp)+', C is '+str(Cpp))
    sPstable = ()
    for i in range(200):
     
        pstrnTemp = float(i)/200.0         
        strsTemp = yiled + AVocepp*(1.0-exp(-mVocepp*pstrnTemp)) + Bpp*sqrt(pstrnTemp) + Cpp*pstrnTemp       
        sPstable = sPstable + ((strsTemp, pstrnTemp),)
     
    return sPstable   
    
    

def SIITFEM(indenterR = 0.5,penetration = -0.1, elasModulus = 120000.0,
            poission = 0.3, yiled = 200.0, hardIndx = 0.1, fricCoef = 0.0, 
            jobName = 'newInp', cpuNum = 1, meshSizeCoef = 5.0):

    # variables----------------------------------------------------------------------------------------
    indenterR = float(indenterR)
    penetration = float(penetration)
    elasModulus = float(elasModulus)
    poission = float(poission)
    yiled = float(yiled)
    hardIndx = float(hardIndx)
    fricCoef = float(fricCoef)
    cpuNum = int(cpuNum)
    meshSizeCoef = float(meshSizeCoef)
    
    matdimension = 5.0*indenterR
    meshsize = indenterR/meshSizeCoef
    sPstable = strsPstrn(elasModulus, yiled, hardIndx )
    mdb.Model(name='Model-SIIT', modelType=STANDARD_EXPLICIT)
    # biuld indenter part----------------------------------------------------------------------------------------
    s1 = mdb.models['Model-SIIT'].ConstrainedSketch(name='profile1',sheetSize=10.0)
    g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
    s1.ConstructionLine(point1=(0.0, -indenterR), point2=(0.0, indenterR))
    s1.FixedConstraint(entity=g[2])
    s1.ArcByCenterEnds(center=(0.0, indenterR), point1=(0.0, 0.0), point2=(indenterR, indenterR), 
        direction=COUNTERCLOCKWISE)
    p = mdb.models['Model-SIIT'].Part(name='indenter', dimensionality=AXISYMMETRIC, 
        type=ANALYTIC_RIGID_SURFACE)
    p = mdb.models['Model-SIIT'].parts['indenter']
    p.AnalyticRigidSurf2DPlanar(sketch=s1)
    s1.unsetPrimaryObject()
    p = mdb.models['Model-SIIT'].parts['indenter']
    v1, e, d1, n = p.vertices, p.edges, p.datums, p.nodes
    p.ReferencePoint(point=v1[1])

    # biuld material part----------------------------------------------------------------------------------------
    s = mdb.models['Model-SIIT'].ConstrainedSketch(name='__profile__', sheetSize=10.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.ConstructionLine(point1=(0.0, -matdimension), point2=(0.0, matdimension))
    s.FixedConstraint(entity=g[2])
    s.rectangle(point1=(0.0, 0.0), point2=(matdimension, matdimension))
    p = mdb.models['Model-SIIT'].Part(name='material', dimensionality=AXISYMMETRIC, 
        type=DEFORMABLE_BODY)
    p = mdb.models['Model-SIIT'].parts['material']
    p.BaseShell(sketch=s)
    s.unsetPrimaryObject()
    p = mdb.models['Model-SIIT'].parts['material']
    del mdb.models['Model-SIIT'].sketches['__profile__']

    # assemble----------------------------------------------------------------------------------------

    a = mdb.models['Model-SIIT'].rootAssembly
    a = mdb.models['Model-SIIT'].rootAssembly
    a.DatumCsysByThreePoints(coordSysType=CYLINDRICAL, origin=(0.0, 0.0, 0.0), 
        point1=(1.0, 0.0, 0.0), point2=(0.0, 0.0, -1.0))
    p = mdb.models['Model-SIIT'].parts['indenter']
    a.Instance(name='indenter-1', part=p, dependent=ON)
    p = mdb.models['Model-SIIT'].parts['material']
    a.Instance(name='material-1', part=p, dependent=ON)
    a = mdb.models['Model-SIIT'].rootAssembly
    a.translate(instanceList=('material-1', ), vector=(0.0, -matdimension, 0.0))

    # material----------------------------------------------------------------------------------------
    mdb.models['Model-SIIT'].Material(name='material')
    mdb.models['Model-SIIT'].materials['material'].Elastic(table=((elasModulus, poission), ))
    mdb.models['Model-SIIT'].materials['material'].Plastic(table=sPstable)
    mdb.models['Model-SIIT'].HomogeneousSolidSection(name='Section-1',material='material', thickness=None)
    p = mdb.models['Model-SIIT'].parts['material']
    f = p.faces
    faces = f[0:1]
    region = regionToolset.Region(faces=faces)
    p = mdb.models['Model-SIIT'].parts['material']
    p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)
        
    # step----------------------------------------------------------------------------------------
    mdb.models['Model-SIIT'].StaticStep(name='load', previous='Initial', 
        maxNumInc=100000, initialInc=1e-6, maxInc=0.1, minInc=1e-10, nlgeom=ON)

    mdb.models['Model-SIIT'].StaticStep(name='unload', previous='load', 
        maxNumInc=100000, initialInc=1e-6, maxInc=0.1, minInc=1e-10)
        
    # contact property----------------------------------------------------------------------------
    mdb.models['Model-SIIT'].ContactProperty('IntProp-1')
    mdb.models['Model-SIIT'].interactionProperties['IntProp-1'].TangentialBehavior(
        formulation=PENALTY, directionality=ISOTROPIC, slipRateDependency=OFF, 
        pressureDependency=OFF, temperatureDependency=OFF, dependencies=0, table=((
        fricCoef, ), ), shearStressLimit=None, maximumElasticSlip=FRACTION, 
        fraction=0.005, elasticSlipStiffness=None)
    mdb.models['Model-SIIT'].interactionProperties['IntProp-1'].NormalBehavior(
        pressureOverclosure=HARD, allowSeparation=ON, 
        constraintEnforcementMethod=DEFAULT)
        
    # contact definition----------------------------------------------------------------------------
    a = mdb.models['Model-SIIT'].rootAssembly
    s1 = a.instances['indenter-1'].edges
    side2Edges1 = s1[0:1]
    region1=regionToolset.Region(side2Edges=side2Edges1)
    a = mdb.models['Model-SIIT'].rootAssembly
    s1 = a.instances['material-1'].edges
    side1Edges1 = s1[2:3]
    region2=regionToolset.Region(side1Edges=side1Edges1)
    mdb.models['Model-SIIT'].SurfaceToSurfaceContactStd(name='Int-1', 
        createStepName='load', master=region1, slave=region2, sliding=FINITE, 
        thickness=ON, interactionProperty='IntProp-1', adjustMethod=NONE, 
        initialClearance=OMIT, datumAxis=None, clearanceRegion=None)

    #load----------------------------------------------------------------------------------------
    a = mdb.models['Model-SIIT'].rootAssembly
    r1 = a.instances['indenter-1'].referencePoints
    refPoints1=(r1[2], )
    region = regionToolset.Region(referencePoints=refPoints1)
    mdb.models['Model-SIIT'].DisplacementBC(name='BC-1', createStepName='load', 
        region=region, u1=0.0, u2=penetration, ur3=0.0, amplitude=UNSET, fixed=OFF, 
        distributionType=UNIFORM, fieldName='', localCsys=None)
    a = mdb.models['Model-SIIT'].rootAssembly
    r1 = a.instances['indenter-1'].referencePoints
    refPoints1=(r1[2], )
    region = regionToolset.Region(referencePoints=refPoints1)
    mdb.models['Model-SIIT'].DisplacementBC(name='BC-2', createStepName='load', 
        region=region, u1=0.0, u2=-penetration, ur3=0.0, amplitude=UNSET, fixed=OFF, 
        distributionType=UNIFORM, fieldName='', localCsys=None)
    mdb.models['Model-SIIT'].boundaryConditions['BC-1'].deactivate('unload')
    mdb.models['Model-SIIT'].boundaryConditions['BC-2'].move('load', 'unload')
    a = mdb.models['Model-SIIT'].rootAssembly
    e1 = a.instances['material-1'].edges
    edges1 = e1[0:1]
    region = regionToolset.Region(edges=edges1)
    mdb.models['Model-SIIT'].DisplacementBC(name='BC-3', createStepName='load', 
        region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF, 
        distributionType=UNIFORM, fieldName='', localCsys=None)

    #mesh----------------------------------------------------------------------------------------
    p = mdb.models['Model-SIIT'].parts['material']
    f = p.faces
    pickedRegions = f[0:1]
    p.setMeshControls(regions=pickedRegions, technique=STRUCTURED)
        
    elemType1 = mesh.ElemType(elemCode=CAX8, elemLibrary=STANDARD)
    elemType2 = mesh.ElemType(elemCode=CAX6M, elemLibrary=STANDARD)
    pickedRegionsSet =(pickedRegions, )
    p.setElementType(regions=pickedRegionsSet, elemTypes=(elemType1, elemType2))
        
    p = mdb.models['Model-SIIT'].parts['material']
    e = p.edges
    pickedEdges1 = e[1:3]
    pickedEdges2 = e[0:1]+e[3:4]
    p.seedEdgeByBias(biasMethod=SINGLE, end1Edges=pickedEdges1, 
        end2Edges=pickedEdges2, ratio=20.0, number=int(matdimension/meshsize), constraint=FINER)
    p = mdb.models['Model-SIIT'].parts['material']
    p.generateMesh()

    # output----------------------------------------------------------------------------------------
    mdb.models['Model-SIIT'].FieldOutputRequest(name='F-Output-1', 
        createStepName='load', variables=('U', 'RF'))
    mdb.models['Model-SIIT'].FieldOutputRequest(name='F-Output-2', 
        createStepName='unload', variables=('U', 'RF'))

    # writeinp----------------------------------------------------------------------------------------
    mdb.Job(name=jobName, model='Model-SIIT', description='', type=ANALYSIS, 
        atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=cpuNum, 
        numDomains=cpuNum,numGPUs=0)
    mdb.jobs[jobName].writeInput(consistencyChecking=OFF)
    # submit and wait for completion-----------------------------------------------------------------
    mdb.jobs[jobName].submit()
    mdb.jobs[jobName].waitForCompletion()


def SIITFEMVoce(indenterR = 0.5,penetration = -0.1, elasModulus = 120000.0,
                poission = 0.3, yiled = 200.0, AVoce = 200.0, mVoce = 20.0, 
                fricCoef = 0.0, jobName = 'newInp', cpuNum = 1, meshSizeCoef = 5.0):

    # variables----------------------------------------------------------------------------------------
    indenterR = float(indenterR)
    penetration = float(penetration)
    elasModulus = float(elasModulus)
    poission = float(poission)
    yiled = float(yiled)
    AVoce = float(AVoce)
    mVoce = float(mVoce)
    fricCoef = float(fricCoef)
    cpuNum = int(cpuNum)
    meshSizeCoef = float(meshSizeCoef)
    
    matdimension = 5.0*indenterR
    meshsize = indenterR/meshSizeCoef
    sPstable = strsPstrnVoce(elasModulus, yiled, AVoce, mVoce)
    mdb.Model(name='Model-SIIT', modelType=STANDARD_EXPLICIT)
    # biuld indenter part----------------------------------------------------------------------------------------
    s1 = mdb.models['Model-SIIT'].ConstrainedSketch(name='profile1',sheetSize=10.0)
    g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
    s1.ConstructionLine(point1=(0.0, -indenterR), point2=(0.0, indenterR))
    s1.FixedConstraint(entity=g[2])
    s1.ArcByCenterEnds(center=(0.0, indenterR), point1=(0.0, 0.0), point2=(indenterR, indenterR), 
        direction=COUNTERCLOCKWISE)
    p = mdb.models['Model-SIIT'].Part(name='indenter', dimensionality=AXISYMMETRIC, 
        type=ANALYTIC_RIGID_SURFACE)
    p = mdb.models['Model-SIIT'].parts['indenter']
    p.AnalyticRigidSurf2DPlanar(sketch=s1)
    s1.unsetPrimaryObject()
    p = mdb.models['Model-SIIT'].parts['indenter']
    v1, e, d1, n = p.vertices, p.edges, p.datums, p.nodes
    p.ReferencePoint(point=v1[1])

    # biuld material part----------------------------------------------------------------------------------------
    s = mdb.models['Model-SIIT'].ConstrainedSketch(name='__profile__', sheetSize=10.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.ConstructionLine(point1=(0.0, -matdimension), point2=(0.0, matdimension))
    s.FixedConstraint(entity=g[2])
    s.rectangle(point1=(0.0, 0.0), point2=(matdimension, matdimension))
    p = mdb.models['Model-SIIT'].Part(name='material', dimensionality=AXISYMMETRIC, 
        type=DEFORMABLE_BODY)
    p = mdb.models['Model-SIIT'].parts['material']
    p.BaseShell(sketch=s)
    s.unsetPrimaryObject()
    p = mdb.models['Model-SIIT'].parts['material']
    del mdb.models['Model-SIIT'].sketches['__profile__']

    # assemble----------------------------------------------------------------------------------------

    a = mdb.models['Model-SIIT'].rootAssembly
    a = mdb.models['Model-SIIT'].rootAssembly
    a.DatumCsysByThreePoints(coordSysType=CYLINDRICAL, origin=(0.0, 0.0, 0.0), 
        point1=(1.0, 0.0, 0.0), point2=(0.0, 0.0, -1.0))
    p = mdb.models['Model-SIIT'].parts['indenter']
    a.Instance(name='indenter-1', part=p, dependent=ON)
    p = mdb.models['Model-SIIT'].parts['material']
    a.Instance(name='material-1', part=p, dependent=ON)
    a = mdb.models['Model-SIIT'].rootAssembly
    a.translate(instanceList=('material-1', ), vector=(0.0, -matdimension, 0.0))

    # material----------------------------------------------------------------------------------------
    mdb.models['Model-SIIT'].Material(name='material')
    mdb.models['Model-SIIT'].materials['material'].Elastic(table=((elasModulus, poission), ))
    mdb.models['Model-SIIT'].materials['material'].Plastic(table=sPstable)
    mdb.models['Model-SIIT'].HomogeneousSolidSection(name='Section-1',material='material', thickness=None)
    p = mdb.models['Model-SIIT'].parts['material']
    f = p.faces
    faces = f[0:1]
    region = regionToolset.Region(faces=faces)
    p = mdb.models['Model-SIIT'].parts['material']
    p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)
        
    # step----------------------------------------------------------------------------------------
    mdb.models['Model-SIIT'].StaticStep(name='load', previous='Initial', 
        maxNumInc=100000, initialInc=0.01, maxInc=0.1, minInc=1e-10, nlgeom=ON)

    mdb.models['Model-SIIT'].StaticStep(name='unload', previous='load', 
        maxNumInc=100000, initialInc=0.001, maxInc=0.1, minInc=1e-10)
        
    # contact property----------------------------------------------------------------------------
    mdb.models['Model-SIIT'].ContactProperty('IntProp-1')
    mdb.models['Model-SIIT'].interactionProperties['IntProp-1'].TangentialBehavior(
        formulation=PENALTY, directionality=ISOTROPIC, slipRateDependency=OFF, 
        pressureDependency=OFF, temperatureDependency=OFF, dependencies=0, table=((
        fricCoef, ), ), shearStressLimit=None, maximumElasticSlip=FRACTION, 
        fraction=0.005, elasticSlipStiffness=None)
    mdb.models['Model-SIIT'].interactionProperties['IntProp-1'].NormalBehavior(
        pressureOverclosure=HARD, allowSeparation=ON, 
        constraintEnforcementMethod=DEFAULT)
        
    # contact definition----------------------------------------------------------------------------
    a = mdb.models['Model-SIIT'].rootAssembly
    s1 = a.instances['indenter-1'].edges
    side2Edges1 = s1[0:1]
    region1=regionToolset.Region(side2Edges=side2Edges1)
    a = mdb.models['Model-SIIT'].rootAssembly
    s1 = a.instances['material-1'].edges
    side1Edges1 = s1[2:3]
    region2=regionToolset.Region(side1Edges=side1Edges1)
    mdb.models['Model-SIIT'].SurfaceToSurfaceContactStd(name='Int-1', 
        createStepName='load', master=region1, slave=region2, sliding=FINITE, 
        thickness=ON, interactionProperty='IntProp-1', adjustMethod=NONE, 
        initialClearance=OMIT, datumAxis=None, clearanceRegion=None)

    #load----------------------------------------------------------------------------------------
    a = mdb.models['Model-SIIT'].rootAssembly
    r1 = a.instances['indenter-1'].referencePoints
    refPoints1=(r1[2], )
    region = regionToolset.Region(referencePoints=refPoints1)
    mdb.models['Model-SIIT'].DisplacementBC(name='BC-1', createStepName='load', 
        region=region, u1=0.0, u2=penetration, ur3=0.0, amplitude=UNSET, fixed=OFF, 
        distributionType=UNIFORM, fieldName='', localCsys=None)
    a = mdb.models['Model-SIIT'].rootAssembly
    r1 = a.instances['indenter-1'].referencePoints
    refPoints1=(r1[2], )
    region = regionToolset.Region(referencePoints=refPoints1)
    mdb.models['Model-SIIT'].DisplacementBC(name='BC-2', createStepName='load', 
        region=region, u1=0.0, u2=-penetration, ur3=0.0, amplitude=UNSET, fixed=OFF, 
        distributionType=UNIFORM, fieldName='', localCsys=None)
    mdb.models['Model-SIIT'].boundaryConditions['BC-1'].deactivate('unload')
    mdb.models['Model-SIIT'].boundaryConditions['BC-2'].move('load', 'unload')
    a = mdb.models['Model-SIIT'].rootAssembly
    e1 = a.instances['material-1'].edges
    edges1 = e1[0:1]
    region = regionToolset.Region(edges=edges1)
    mdb.models['Model-SIIT'].DisplacementBC(name='BC-3', createStepName='load', 
        region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF, 
        distributionType=UNIFORM, fieldName='', localCsys=None)

    #mesh----------------------------------------------------------------------------------------
    p = mdb.models['Model-SIIT'].parts['material']
    f = p.faces
    pickedRegions = f[0:1]
    p.setMeshControls(regions=pickedRegions, technique=STRUCTURED)
    p = mdb.models['Model-SIIT'].parts['material']
    e = p.edges
    pickedEdges1 = e[1:3]
    pickedEdges2 = e[0:1]+e[3:4]
    p.seedEdgeByBias(biasMethod=SINGLE, end1Edges=pickedEdges1, 
        end2Edges=pickedEdges2, ratio=20.0, number=int(matdimension/meshsize), constraint=FINER)
    p = mdb.models['Model-SIIT'].parts['material']
    p.generateMesh()

    # output----------------------------------------------------------------------------------------
    mdb.models['Model-SIIT'].FieldOutputRequest(name='F-Output-1', 
        createStepName='load', variables=('U', 'RF'))
    mdb.models['Model-SIIT'].FieldOutputRequest(name='F-Output-2', 
        createStepName='unload', variables=('U', 'RF'))

    # writeinp----------------------------------------------------------------------------------------
    mdb.Job(name=jobName, model='Model-SIIT', description='', type=ANALYSIS, 
        atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=cpuNum, 
        numGPUs=0)
    mdb.jobs[jobName].writeInput(consistencyChecking=OFF)
    # submit and wait for completion-----------------------------------------------------------------
    mdb.jobs[jobName].submit()
    mdb.jobs[jobName].waitForCompletion()
    

def SIITFEMVocepp(indenterR = 0.5,penetration = -0.1, elasModulus = 120000.0,
                poission = 0.3, yiled = 200.0, AVocepp = 200.0, mVocepp = 20.0, Bpp = 200.0, 
                Cpp = 200.0, fricCoef = 0.0, jobName = 'newInp', cpuNum = 1, meshSizeCoef = 5.0):

    # variables----------------------------------------------------------------------------------------
    indenterR = float(indenterR)
    penetration = float(penetration)
    elasModulus = float(elasModulus)
    poission = float(poission)
    yiled = float(yiled)
    AVocepp = float(AVocepp)
    mVocepp = float(mVocepp)
    Bpp = float(Bpp)
    Cpp = float(Cpp)
    fricCoef = float(fricCoef)
    cpuNum = int(cpuNum)
    meshSizeCoef = float(meshSizeCoef)
    
    matdimension = 5.0*indenterR
    meshsize = indenterR/meshSizeCoef
    sPstable = strsPstrnVocepp(elasModulus, yiled, AVocepp, mVocepp, Bpp, Cpp)
    mdb.Model(name='Model-SIIT', modelType=STANDARD_EXPLICIT)
    # biuld indenter part----------------------------------------------------------------------------------------
    s1 = mdb.models['Model-SIIT'].ConstrainedSketch(name='profile1',sheetSize=10.0)
    g, v, d, c = s1.geometry, s1.vertices, s1.dimensions, s1.constraints
    s1.ConstructionLine(point1=(0.0, -indenterR), point2=(0.0, indenterR))
    s1.FixedConstraint(entity=g[2])
    s1.ArcByCenterEnds(center=(0.0, indenterR), point1=(0.0, 0.0), point2=(indenterR, indenterR), 
        direction=COUNTERCLOCKWISE)
    p = mdb.models['Model-SIIT'].Part(name='indenter', dimensionality=AXISYMMETRIC, 
        type=ANALYTIC_RIGID_SURFACE)
    p = mdb.models['Model-SIIT'].parts['indenter']
    p.AnalyticRigidSurf2DPlanar(sketch=s1)
    s1.unsetPrimaryObject()
    p = mdb.models['Model-SIIT'].parts['indenter']
    v1, e, d1, n = p.vertices, p.edges, p.datums, p.nodes
    p.ReferencePoint(point=v1[1])

    # biuld material part----------------------------------------------------------------------------------------
    s = mdb.models['Model-SIIT'].ConstrainedSketch(name='__profile__', sheetSize=10.0)
    g, v, d, c = s.geometry, s.vertices, s.dimensions, s.constraints
    s.ConstructionLine(point1=(0.0, -matdimension), point2=(0.0, matdimension))
    s.FixedConstraint(entity=g[2])
    s.rectangle(point1=(0.0, 0.0), point2=(matdimension, matdimension))
    p = mdb.models['Model-SIIT'].Part(name='material', dimensionality=AXISYMMETRIC, 
        type=DEFORMABLE_BODY)
    p = mdb.models['Model-SIIT'].parts['material']
    p.BaseShell(sketch=s)
    s.unsetPrimaryObject()
    p = mdb.models['Model-SIIT'].parts['material']
    del mdb.models['Model-SIIT'].sketches['__profile__']

    # assemble----------------------------------------------------------------------------------------

    a = mdb.models['Model-SIIT'].rootAssembly
    a = mdb.models['Model-SIIT'].rootAssembly
    a.DatumCsysByThreePoints(coordSysType=CYLINDRICAL, origin=(0.0, 0.0, 0.0), 
        point1=(1.0, 0.0, 0.0), point2=(0.0, 0.0, -1.0))
    p = mdb.models['Model-SIIT'].parts['indenter']
    a.Instance(name='indenter-1', part=p, dependent=ON)
    p = mdb.models['Model-SIIT'].parts['material']
    a.Instance(name='material-1', part=p, dependent=ON)
    a = mdb.models['Model-SIIT'].rootAssembly
    a.translate(instanceList=('material-1', ), vector=(0.0, -matdimension, 0.0))

    # material----------------------------------------------------------------------------------------
    mdb.models['Model-SIIT'].Material(name='material')
    mdb.models['Model-SIIT'].materials['material'].Elastic(table=((elasModulus, poission), ))
    mdb.models['Model-SIIT'].materials['material'].Plastic(table=sPstable)
    mdb.models['Model-SIIT'].HomogeneousSolidSection(name='Section-1',material='material', thickness=None)
    p = mdb.models['Model-SIIT'].parts['material']
    f = p.faces
    faces = f[0:1]
    region = regionToolset.Region(faces=faces)
    p = mdb.models['Model-SIIT'].parts['material']
    p.SectionAssignment(region=region, sectionName='Section-1', offset=0.0, 
        offsetType=MIDDLE_SURFACE, offsetField='', 
        thicknessAssignment=FROM_SECTION)
        
    # step----------------------------------------------------------------------------------------
    mdb.models['Model-SIIT'].StaticStep(name='load', previous='Initial', 
        maxNumInc=100000, initialInc=0.01, maxInc=0.01, minInc=1e-10, nlgeom=ON)

    mdb.models['Model-SIIT'].StaticStep(name='unload', previous='load', 
        maxNumInc=100000, initialInc=0.001, maxInc=0.01, minInc=1e-10)
        
    # contact property----------------------------------------------------------------------------
    mdb.models['Model-SIIT'].ContactProperty('IntProp-1')
    mdb.models['Model-SIIT'].interactionProperties['IntProp-1'].TangentialBehavior(
        formulation=PENALTY, directionality=ISOTROPIC, slipRateDependency=OFF, 
        pressureDependency=OFF, temperatureDependency=OFF, dependencies=0, table=((
        fricCoef, ), ), shearStressLimit=None, maximumElasticSlip=FRACTION, 
        fraction=0.005, elasticSlipStiffness=None)
    mdb.models['Model-SIIT'].interactionProperties['IntProp-1'].NormalBehavior(
        pressureOverclosure=HARD, allowSeparation=ON, 
        constraintEnforcementMethod=DEFAULT)
        
    # contact definition----------------------------------------------------------------------------
    a = mdb.models['Model-SIIT'].rootAssembly
    s1 = a.instances['indenter-1'].edges
    side2Edges1 = s1[0:1]
    region1=regionToolset.Region(side2Edges=side2Edges1)
    a = mdb.models['Model-SIIT'].rootAssembly
    s1 = a.instances['material-1'].edges
    side1Edges1 = s1[2:3]
    region2=regionToolset.Region(side1Edges=side1Edges1)
    mdb.models['Model-SIIT'].SurfaceToSurfaceContactStd(name='Int-1', 
        createStepName='load', master=region1, slave=region2, sliding=FINITE, 
        thickness=ON, interactionProperty='IntProp-1', adjustMethod=NONE, 
        initialClearance=OMIT, datumAxis=None, clearanceRegion=None)

    #load----------------------------------------------------------------------------------------
    a = mdb.models['Model-SIIT'].rootAssembly
    r1 = a.instances['indenter-1'].referencePoints
    refPoints1=(r1[2], )
    region = regionToolset.Region(referencePoints=refPoints1)
    mdb.models['Model-SIIT'].DisplacementBC(name='BC-1', createStepName='load', 
        region=region, u1=0.0, u2=penetration, ur3=0.0, amplitude=UNSET, fixed=OFF, 
        distributionType=UNIFORM, fieldName='', localCsys=None)
    a = mdb.models['Model-SIIT'].rootAssembly
    r1 = a.instances['indenter-1'].referencePoints
    refPoints1=(r1[2], )
    region = regionToolset.Region(referencePoints=refPoints1)
    mdb.models['Model-SIIT'].DisplacementBC(name='BC-2', createStepName='load', 
        region=region, u1=0.0, u2=-penetration, ur3=0.0, amplitude=UNSET, fixed=OFF, 
        distributionType=UNIFORM, fieldName='', localCsys=None)
    mdb.models['Model-SIIT'].boundaryConditions['BC-1'].deactivate('unload')
    mdb.models['Model-SIIT'].boundaryConditions['BC-2'].move('load', 'unload')
    a = mdb.models['Model-SIIT'].rootAssembly
    e1 = a.instances['material-1'].edges
    edges1 = e1[0:1]
    region = regionToolset.Region(edges=edges1)
    mdb.models['Model-SIIT'].DisplacementBC(name='BC-3', createStepName='load', 
        region=region, u1=0.0, u2=0.0, ur3=0.0, amplitude=UNSET, fixed=OFF, 
        distributionType=UNIFORM, fieldName='', localCsys=None)

    #mesh----------------------------------------------------------------------------------------
    p = mdb.models['Model-SIIT'].parts['material']
    f = p.faces
    pickedRegions = f[0:1]
    p.setMeshControls(regions=pickedRegions, technique=STRUCTURED)
    p = mdb.models['Model-SIIT'].parts['material']
    e = p.edges
    pickedEdges1 = e[1:3]
    pickedEdges2 = e[0:1]+e[3:4]
    p.seedEdgeByBias(biasMethod=SINGLE, end1Edges=pickedEdges1, 
        end2Edges=pickedEdges2, ratio=20.0, number=int(matdimension/meshsize), constraint=FINER)
    p = mdb.models['Model-SIIT'].parts['material']
    p.generateMesh()

    # output----------------------------------------------------------------------------------------
    mdb.models['Model-SIIT'].FieldOutputRequest(name='F-Output-1', 
        createStepName='load', variables=('U', 'RF'))
    mdb.models['Model-SIIT'].FieldOutputRequest(name='F-Output-2', 
        createStepName='unload', variables=('U', 'RF'))

    # writeinp----------------------------------------------------------------------------------------
    mdb.Job(name=jobName, model='Model-SIIT', description='', type=ANALYSIS, 
        atTime=None, waitMinutes=0, waitHours=0, queue=None, memory=90, 
        memoryUnits=PERCENTAGE, getMemoryFromAnalysis=True, 
        explicitPrecision=SINGLE, nodalOutputPrecision=SINGLE, echoPrint=OFF, 
        modelPrint=OFF, contactPrint=OFF, historyPrint=OFF, userSubroutine='', 
        scratch='', resultsFormat=ODB, multiprocessingMode=DEFAULT, numCpus=cpuNum, 
        numGPUs=0)
    mdb.jobs[jobName].writeInput(consistencyChecking=OFF)
    # submit and wait for completion-----------------------------------------------------------------
    mdb.jobs[jobName].submit()
    mdb.jobs[jobName].waitForCompletion()


def SIITFEMPost(jobName = 'newInp', indenterR = 0.5):
    # postProcess-----------------------------------------------------------------------------------
    odb = session.openOdb(name=jobName+'.odb')
    NS=odb.rootAssembly.nodeSets.keys()
    RP=NS[1]
    session.viewports['Viewport: 1'].setValues(displayedObject=odb)
    loadDisp = session.xyDataListFromField(odb=odb, outputPosition=NODAL, variable=(('RF', 
               NODAL, ((COMPONENT, 'RF2'), )), ('U', NODAL, ((COMPONENT, 'U2'), )), ), 
               nodeSets=(RP, ))
    disp = range(len(loadDisp[0]))
    load = range(len(loadDisp[0]))
    timeStep = range(len(loadDisp[0]))
    for i in range(len(loadDisp[0])):
        disp[i] = loadDisp[1][i][1]
    for i in range(len(loadDisp[0])):
        load[i] = loadDisp[0][i][1]
    for i in range(len(loadDisp[0])):
        timeStep[i] = loadDisp[0][i][0]
        
    f1 = open('Lh_'+jobName+'.txt','a+')
    f1.writelines(['timeStep   ','disp    ','load'+'\n'])
    for i in range(len(loadDisp[0])):
        f1.writelines([str(timeStep[i])+'   ',str(disp[i])+'    ',str(load[i])+'\n'])
    f1.close()
    
    nds = mdb.models['Model-SIIT'].rootAssembly.instances['material-1'].nodes
    # getByBoundingBox function is to choose the node on the material surface near the indenter,
    # mdb.models['Model-SIIT'].rootAssembly.instances['material-1'].nodes[650] object
    #  it is a MeshNode object,surfnds[0].label is the node label this object corresponds to 
    surfnds = nds.getByBoundingBox(xMin = 0.0, xMax = 1.5*indenterR, yMin = -1e-5, yMax = 1e-5)   
    surfndsLable = range(len(surfnds))
    for i in range(len(surfnds)):
        surfndsLable[i] = str(surfnds[i].label)
    surfndsLable = tuple(surfndsLable)
    # extract the dispX of nodes labeled in surfndsLable    
    dispListX = session.xyDataListFromField(odb=odb, outputPosition=NODAL, variable=(('U', 
                   NODAL, ((COMPONENT, 'U1'), )), ), nodeLabels=(('MATERIAL-1', surfndsLable), )) 
                   
    dispListY = session.xyDataListFromField(odb=odb, outputPosition=NODAL, variable=(('U', 
                   NODAL, ( (COMPONENT, 'U2'), )), ), nodeLabels=(('MATERIAL-1', surfndsLable), )) 
                   
    finalCoordListX = range(len(surfnds))
    finalCoordListY = range(len(surfnds))
    initialCoordListX = range(len(surfnds))
    initialCoordListY = range(len(surfnds))
    # calculate the node coordinates after unloading  
    for i in range(len(surfnds)):
        finalCoordListX[i] = surfnds[i].coordinates[0] + dispListX[i][-1][1]                               
        
    for i in range(len(surfnds)):
        finalCoordListY[i] = surfnds[i].coordinates[1] + dispListY[i][-1][1]
        
    for i in range(len(surfnds)):
        initialCoordListX[i] = surfnds[i].coordinates[0]                          
        
    for i in range(len(surfnds)):
        initialCoordListY[i] = surfnds[i].coordinates[1] 
        
    f1 = open('UnldSrfNdsCrd_'+jobName+'.txt','a+')
    f1.writelines(['initialCoordListX   ','initialCoordListY    ',
                  'finalCoordListX  ','finalCoordListY'+'\n'])
    for i in range(len(surfnds)):
        f1.writelines([str(initialCoordListX[i])+'    ',str(initialCoordListY[i])+'    ',
                         str(finalCoordListX[i])+'    ',str(finalCoordListY[i])+'\n'])
    f1.close()
    
    session.odbs[jobName+'.odb'].close()
    
    return 
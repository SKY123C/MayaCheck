import maya.cmds as mc
import maya.OpenMaya as om
import pymel.core as pm
import random

layout = {2: [(0.25, 0.75), (0.2, 0.7), (0.3, 0.75), (0.75, 0.75), (0.7, 0.8), (0.25, 0.25), (0.3, 0.3), (0.75, 0.25),
              (0.8, 0.25)]}
uvDict = {}
obj = pm.PyNode("pSphere1").__apimdagpath__()

mesh = om.MFnMesh(obj)

uArray = om.MFloatArray()
vArray = om.MFloatArray()
mesh.getUVs(uArray, vArray)

uvShellArray = om.MIntArray()
shells = om.MScriptUtil()
shellsPtr = shells.asUintPtr()

mesh.getUvShellsIds(uvShellArray, shellsPtr)

for i in range(uArray.length()):
    if uvShellArray[i] not in uvDict:
        uvDict[uvShellArray[i]] = [i]

    else:
        uvDict[uvShellArray[i]].append(i)

for i in uvDict.values():
    for j in i:
        mc.select("pSphere1.map[{}]".format(j), add=1)
    rm = random.choice(layout.values()[0])
    mc.polyEditUV(r=0, u=rm[0], v=rm[1])











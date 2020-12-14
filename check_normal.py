import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import pymel.core as pm


def check_normal(model):    # model: mesh,polygon

    if model.lower() == "polygon":
        obj = mc.ls(sl=1)
    else:
        return

    dag = pm.PyNode(obj[0]).__apimdagpath__()
    it = OpenMaya.MItMeshPolygon(dag)
    temp = OpenMaya.MFnMesh(dag)
    ray_source = OpenMaya.MFloatPoint()
    hit_points = OpenMaya.MFloatPointArray()
    while not it.isDone():
        center_point = it.center(OpenMaya.MSpace.kWorld)

        face_normal = OpenMaya.MVector()
        it.getNormal(face_normal, OpenMaya.MSpace.kWorld)
        d_normal = face_normal*0.1
        temp_point = center_point + d_normal
        ray_source.setCast(temp_point)
        b_intersection = temp.allIntersections(ray_source, OpenMaya.MFloatVector(face_normal),
                                              None, None, False, OpenMaya.MSpace.kWorld, 999, False, None, False,
                                              hit_points, None, None, None, None, None)
        if b_intersection and hit_points.length() % 2 != 0:
            print it.index()

        it.next()

check_normal("polygon")

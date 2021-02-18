# coding:utf-8
from __future__ import division
import maya.cmds as mc
import maya.OpenMaya as om
import time
a = time.time()


def compute(turn=True):
    sel = om.MSelectionList()
    om.MGlobal.getActiveSelectionList(sel)
    source = om.MDagPath()
    target = om.MDagPath()
    sel.getDagPath(0, source)
    source_mesh = om.MFnMesh(source)
    source_bounding = source_mesh.boundingBox()
    sel.remove(0)
    target_iter = om.MItSelectionList(sel, om.MFn.kMesh)
    point = om.MPointArray()
    hit_points = om.MFloatPointArray()

    face_normal = om.MVector()
    mc.select(cl=True)
    while not target_iter.isDone():
        target_iter.getDagPath(target)
        target_dag = om.MFnDagNode(target)
        target_bounding = target_dag.boundingBox()
        if not source_bounding.intersects(target_bounding):
            target_iter.next()
            continue

        face_iter = om.MItMeshPolygon(target)
        while not face_iter.isDone():
            face_iter.getPoints(point, om.MSpace.kWorld)
            face_iter.getNormal(face_normal, om.MSpace.kWorld)
            for i in range(0, point.length()):

                temp_point = om.MFloatPoint(point[i][0], point[i][1], point[i][2])
                direction_normal = om.MFloatVector(face_normal[0], face_normal[1], face_normal[2])
                hit = source_mesh.allIntersections(temp_point, direction_normal, None, None, False, om.MSpace.kWorld, 999, True, None, True, hit_points, None, None, None, None, None)

                if hit and i == point.length()-1 and (round(hit_points[0][0], 6) >= round(point[i][0], 6) >= round(hit_points[1][0], 6) or round(hit_points[0][0], 6) <= round(point[i][0], 6) <= round(hit_points[1][0], 6)) and (round(hit_points[0][1], 6) >= round(point[i][1], 6) >= round(hit_points[1][1], 6) or round(hit_points[0][1], 6) <= round(point[i][1], 6) <= round(hit_points[1][1], 6)) and (round(hit_points[0][2], 6) >= round(point[i][2], 6) >= round(hit_points[1][2], 6) or round(hit_points[0][2], 6) <= round(point[i][2], 6) <= round(hit_points[1][2], 6)):
                    mc.select("{}.f[{}]".format(target.fullPathName(), face_iter.index()), add=True)
                elif hit and (round(hit_points[0][0], 6) >= round(point[i][0], 6) >= round(hit_points[1][0], 6) or round(hit_points[0][0], 6) <= round(point[i][0], 6) <= round(hit_points[1][0], 6)) and (round(hit_points[0][1], 6) >= round(point[i][1], 6) >= round(hit_points[1][1], 6) or round(hit_points[0][1], 6) <= round(point[i][1], 6) <= round(hit_points[1][1], 6)) and (round(hit_points[0][2], 6) >= round(point[i][2], 6) >= round(hit_points[1][2], 6) or round(hit_points[0][2], 6) <= round(point[i][2], 6) <= round(hit_points[1][2], 6)):
                    continue
                else:
                    break

            face_iter.next()

        target_iter.next()

    if turn:
        pass
        # mc.delete()
compute()
b = time.time()
#print b-a


# coding:utf-8
import maya.cmds as mc
import pymel.core as pm
import maya.OpenMaya as om
import numpy as np
import decimal
from collections import OrderedDict
import time
decimal.getcontext().prec = 2
selected = mc.ls(sl=True,l=True)
a = time.time()


def compute(obj):
    dict_obj = OrderedDict()
    point = om.MPointArray()
    position = []
    face_iter = om.MItMeshPolygon(pm.PyNode("{}".format(mc.listRelatives(obj[0], c=True, type="mesh")[0])).__apimdagpath__())
    face_normal = om.MVector()
    while not face_iter.isDone():
        face_iter.getPoints(point, om.MSpace.kWorld)
        face_iter.getNormal(face_normal, om.MSpace.kWorld)
        for i in range(0, point.length()):
            position.append([point[i][0], point[i][1], point[i][2]])
        aver_x_y_z = np.sum(position, axis=0).tolist()
        x = aver_x_y_z[0]/point.length()
        y = aver_x_y_z[1]/point.length()
        z = aver_x_y_z[2]/point.length()
        dict_obj["{}".format(face_iter.index())] = [[x, y, z], [face_normal[0], face_normal[1], face_normal[2]]]
        del position[:]
        face_iter.next()

    return dict_obj


def check(parm):
    results = []
    target_mesh = om.MFnMesh(pm.PyNode("{}".format(mc.listRelatives(selected[0], c=True, type="mesh")[0])).__apimdagpath__())
    for i, data in parm.iteritems():

        x = data[0][0]+0.1
        y = ((data[1][1]*0.1)/data[1][0])+data[0][1]
        z = ((data[1][2]*0.01)/data[1][0])+data[0][2]

        x_vector = 0.1
        y_vector = y - data[0][1]
        z_vector = z - data[0][2]

        if (x_vector*data[1][0]+y_vector*data[1][1]+z_vector*data[1][2]) >= 0:

            pass

        else:

            x = data[0][0]-0.1

            y = ((data[1][1]*-0.1)/data[1][0])+data[0][1]

            z = ((data[1][2]*-0.1)/data[1][0])+data[0][2]

        temp_point = om.MFloatPoint(x, y, z)
        direction_normal = om.MFloatVector(data[1][0], data[1][1], data[1][2])
        hit_faces = om.MIntArray()
        hit_points = om.MFloatPointArray()
        target_mesh.allIntersections(temp_point, direction_normal, None, None, True, om.MSpace.kWorld, 999, False, None, False, hit_points, None, hit_faces, None, None, None)

        if decimal.Decimal(hit_points.length())/decimal.Decimal(2) != 0:
            results.append(i)
    return results
print check(compute(selected))
b = time.time()
print b-a


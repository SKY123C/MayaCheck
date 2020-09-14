# coding:utf-8
import maya.OpenMaya as Om
from collections import defaultdict
import numpy as np
import maya.cmds as mc
'''
通过叉乘判断两个边是否相交
判断前先判断该polygon中全部边x的最小值是否大于下个polygon中全部边x的最大值
'''


def compute_edge(edge, next_edge):
    if sorted(edge, key=lambda x: x[0][0], reverse=True)[0][0][0] <= sorted(next_edge, key=lambda x: x[0][0])[0][0][0] or \
        sorted(edge, key=lambda x: x[0][1], reverse=True)[0][0][1] <= sorted(next_edge, key=lambda x: x[0][1])[0][0][1] or \
        sorted(edge, key=lambda x: x[0][0])[0][0][0] >= sorted(next_edge, key=lambda x: x[0][0], reverse=True)[0][0][0] or \
        sorted(edge, key=lambda x: x[0][1])[0][0][1] >= sorted(next_edge, key=lambda x: x[0][1], reverse=True)[0][0][1]:
        return False
    for e in edge:
        for next_e in next_edge:
            if sorted(e, key=lambda x: x[0])[0][0] >= sorted(next_e, key=lambda x: x[0], reverse=True)[0][0] or \
                sorted(e, key=lambda x: x[1])[0][1] >= sorted(next_e, key=lambda x: x[1], reverse=True)[0][1] or \
                sorted(e, key=lambda x: x[0], reverse=True)[0][0] <= sorted(next_e, key=lambda x: x[0])[0][0] or \
                sorted(e, key=lambda x: x[1], reverse=True)[0][1] <= sorted(next_e, key=lambda x: x[1])[0][1]:
                continue
            vector_u = e[1][0]-e[0][0]
            vector_v = e[1][1]-e[0][1]
            vector_first_u = next_e[0][0]-e[0][0]
            vector_first_v = next_e[0][1]-e[0][1]
            vector_second_u = next_e[1][0]-e[0][0]
            vector_second_v = next_e[1][1]-e[0][1]
            if np.linalg.det([[vector_u, vector_v], [vector_first_u, vector_first_v]])*np.linalg.det([[vector_u, vector_v], [vector_second_u, vector_second_v]]) < 0:
                return True


def main():
    face_id_dict = defaultdict(list)
    face_edge = defaultdict(list)
    ptr = Om.MScriptUtil()
    sel = Om.MSelectionList()
    Om.MGlobal.getActiveSelectionList(sel)
    iterator = Om.MItSelectionList(sel, Om.MFn.kMesh)
    shape = Om.MDagPath()
    while not iterator.isDone():

        iterator.getDagPath(shape)
        mesh = Om.MFnMesh(shape)

        itr = Om.MItMeshFaceVertex(shape)
        while not itr.isDone():
            float2 = ptr.asFloat2Ptr()
            itr.getUV(float2)

            pt = (ptr.getFloat2ArrayItem(float2, 0, 0), ptr.getFloat2ArrayItem(float2,0,1))
            face_id_dict['{}'.format(itr.faceId())].append(pt)
            itr.next()
        for face_id, point in face_id_dict.iteritems():
            for i in xrange(len(point)-1):
                face_edge['{}'.format(face_id)].append([point[i], point[i+1]])

        for i in xrange(mesh.numPolygons()):
            for j in xrange(i+1, mesh.numPolygons()):
                if compute_edge(face_edge["{}".format(i)], face_edge["{}".format(j)]):
                    mc.select("{}.f[{}]".format(mesh.fullPathName(), i), add=True)
                    mc.select("{}.f[{}]".format(mesh.fullPathName(), j), add=True)

        iterator.next()


main()



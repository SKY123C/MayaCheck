import maya.cmds as mc
import maya.OpenMaya as OpenMaya
import pymel.core as pm
import logging
all_objects = mc.ls(dag=1, type="transform", v=1)


def check_normal(objects):

    LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
    logger = logging.getLogger("mylog")
    logger.setLevel(logging.ERROR)
    handle = logging.FileHandler('D:/mayaCheckNormal.log')
    formatter = logging.Formatter(LOG_FORMAT)
    handle.setFormatter(formatter)
    logger.addHandler(handle)
    if not objects:
        logger.error("{}:The scene lacks objects".format(mc.file(exn=1)))
        return

    for obj in objects:
        dag = pm.PyNode(obj).__apimdagpath__()
        it = OpenMaya.MItMeshPolygon(dag)
        temp = OpenMaya.MFnMesh(dag)
        ray_source = OpenMaya.MFloatPoint()
        hit_points = OpenMaya.MFloatPointArray()
        while not it.isDone():
            center_point = it.center(OpenMaya.MSpace.kWorld)

            face_normal = OpenMaya.MVector()
            it.getNormal(face_normal, OpenMaya.MSpace.kWorld)
            d_normal = face_normal * 0.1
            temp_point = center_point + d_normal
            ray_source.setCast(temp_point)
            b_intersection = temp.allIntersections(ray_source, OpenMaya.MFloatVector(face_normal),
                                                   None, None, False, OpenMaya.MSpace.kWorld, 999, False, None, False,
                                                   hit_points, None, None, None, None, None)
            if b_intersection and hit_points.length() % 2 != 0:
                logger.warning("%s.f[%d]" % (obj, it.index()))

            it.next()


check_normal(all_objects)


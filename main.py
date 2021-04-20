# coding:utf-8
import maya.OpenMaya as om
import maya.OpenMayaUI as mui
import pymel.core as pm
import shiboken2
from PySide2 import QtWidgets, QtCore


def get_window():
    ptr = mui.MQtUtil().mainWindow()

    win = shiboken2.wrapInstance(long(ptr), QtWidgets.QMainWindow)
    return win


def delete_ui(name):
    if pm.control(name, exists=True):
        pm.deleteUI(name, ctl=1)


class GridLayout(QtWidgets.QGridLayout):
    signal = QtCore.Signal(dict)

    def __init__(self, label, spacing, *args):

        super(GridLayout, self).__init__()
        self.dis = 1
        self.spacing = spacing
        self.args = args
        self.label = label
        self.button_group = QtWidgets.QButtonGroup(self)

        self.button_group.buttonClicked.connect(self.transfer_signal)
        self.add_widget_init()

    def add_widget_init(self):

        self.dis += 1
        for name in self.args:
            exec ('self.{} = QtWidgets.QRadioButton("{}")'.format(name, name))
            exec ("self.addWidget(self.{}, 0, self.dis)".format(name))
            exec ("self.button_group.addButton(self.{})".format(name))
            self.dis += 1

        for i in range(2, self.dis + 1):
            self.setColumnMinimumWidth(i, self.spacing)
        self.setColumnStretch(self.dis, 30)

    def transfer_signal(self, button):
        self.signal.emit({self.label: button.text()})


class UI(QtWidgets.QMainWindow):
    settings = {'Sample space': '', 'Vertex Normal': '', 'Mirroring': '', 'Search method': ''}

    def __init__(self):

        delete_ui('Transfer_Attribute')
        parent = get_window()

        super(UI, self).__init__(parent=parent)
        self.setWindowTitle('Transfer Attribute')
        self.setObjectName('Transfer_Attribute')
        self.menu = self.menuBar()

        self.widget = QtWidgets.QWidget()
        self.main_layout = QtWidgets.QVBoxLayout(self.widget)
        self.layout1 = QtWidgets.QFormLayout()
        self.layout2 = QtWidgets.QFormLayout()

        self.grid = QtWidgets.QGridLayout()
        self.h_layout = QtWidgets.QHBoxLayout()
        self.group1 = QtWidgets.QGroupBox('Attributes To Transfer')
        self.group2 = QtWidgets.QGroupBox('Attribute Settings')

        self.vertex_normal = GridLayout('Vertex Normal', 70, 'Off', 'On')
        self.space = GridLayout('Sample space', 70, 'World', 'Local', 'UV', 'Component', 'Topology')
        self.mirror = GridLayout('Mirroring', 70, 'Off', 'X', 'Y', 'Z')
        self.search = GridLayout('Search method', 148, 'Closest_along_normal', 'Closest_to_point')
        self.vertex_normal.signal.connect(self.set_settings)
        self.space.signal.connect(self.set_settings)
        self.mirror.signal.connect(self.set_settings)
        self.search.signal.connect(self.set_settings)

        self.transfer_btn = QtWidgets.QPushButton('Transfer')
        self.apply_btn = QtWidgets.QPushButton('Apply')
        self.close_btn = QtWidgets.QPushButton('Close')

        self.setCentralWidget(self.widget)
        self.resize(600, 500)
        self.menu_init()
        self.layout_init()

        self.transfer_btn.clicked.connect(self.transfer)
        self.apply_btn.clicked.connect(self.apply)
        self.close_btn.clicked.connect(self.close)

        self.parent().show()

    def layout_init(self):
        self.layout2.addRow('Sample space:', self.space)
        self.layout2.addRow('Mirroring:', self.mirror)
        self.layout2.addRow('Search method:', self.search)
        self.layout2.setVerticalSpacing(0)

        self.layout1.addRow('Vertex Normal:', self.vertex_normal)

        self.h_layout.addWidget(self.transfer_btn)
        self.h_layout.addWidget(self.apply_btn)
        self.h_layout.addWidget(self.close_btn)

        self.group1.setLayout(self.layout1)
        self.group2.setLayout(self.layout2)

        self.main_layout.addWidget(self.group1)
        self.main_layout.addWidget(self.group2)
        self.main_layout.addStretch(1)
        self.main_layout.addLayout(self.h_layout)

    def menu_init(self):
        edit_menu = self.menu.addMenu('Edit')
        edit_menu.addAction('Save Settings')
        edit_menu.addAction('Reset Settings')

    def transfer(self):
        if self.settings['Vertex Normal'] in ['Off', '']:
            pm.warning('Please check whether vertex normal is on')
            return
        else:
            self.transfer_vertex_normal()
        self.transfer_vertex_normal()
        self.close()

    def set_settings(self, value):
        self.settings[value.keys()[0]] = value.values()[0]

    def apply(self):

        if self.settings['Vertex Normal'] in ['Off', '']:
            pm.warning('Please check whether vertex normal is on')
            return
        else:
            self.transfer_vertex_normal()

    def transfer_vertex_normal(self):

        if self.settings['Mirroring'] == 'X':

            matrix_values = [-1, 0, 0, 0,
                             0, 1, 0, 0,
                             0, 0, 1, 0,
                             0, 0, 0, 1]

        elif self.settings['Mirroring'] == 'Y':
            matrix_values = [1, 0, 0, 0,
                             0, -1, 0, 0,
                             0, 0, 1, 0,
                             0, 0, 0, 1]
        elif self.settings['Mirroring'] == 'Z':
            matrix_values = [1, 0, 0, 0,
                             0, 1, 0, 0,
                             0, 0, -1, 0,
                             0, 0, 0, 1]
        elif self.settings['Mirroring'] == 'Off':
            matrix_values = [1, 0, 0, 0,
                             0, 1, 0, 0,
                             0, 0, 1, 0,
                             0, 0, 0, 1]
        else:
            pm.warning('Please check whether Mirroring is on')
            return

        if self.settings['Sample space'] == 'World':
            space = om.MSpace.kWorld
        elif self.settings['Sample space'] == 'Local':
            space = om.MSpace.kObject
        elif self.settings['Sample space'] in ['Component', 'Topology']:
            pm.displayInfo(u'该功能暂时不写，有点简单')
            return
        if self.settings['Sample space'] in ['World', 'Local'] and self.settings[
            'Search method'] == 'Closest_along_normal':
            self.transfer_along_normal(matrix_values, space)
            return
        elif self.settings['Sample space'] == 'UV' and self.settings['Search method'] in ['Closest_to_point',
                                                                                          'Closest_along_normal']:
            self.transfer_vertex_normal_uv(matrix_values)
            return

        elif self.settings['Sample space'] == '' :
            pm.warning('Please check whether Sample space is on')
            return


        replaced = pm.PyNode(pm.ls(sl=1)[0]).__apimdagpath__()
        to_replace = pm.PyNode(pm.ls(sl=1)[1]).__apimdagpath__()

        to_replace_mesh = om.MFnMesh(to_replace)
        to_iter_polygon = om.MItMeshPolygon(to_replace)
        iter_polygon = om.MItMeshPolygon(replaced)

        count = 0
        vertex = om.MScriptUtil(to_replace_mesh.numFaceVertices()).asUint()
        normal = om.MVector()
        normal_list = om.MVectorArray()
        face_list = om.MIntArray(vertex)
        vertex_list = om.MIntArray(vertex)
        matrix = om.MMatrix()
        om.MScriptUtil().createMatrixFromList(matrix_values, matrix)

        for face_id in range(0, to_replace_mesh.numPolygons()):

            face_vertex_list = om.MIntArray()
            to_replace_mesh.getPolygonVertices(face_id, face_vertex_list)

            for vertex_id in range(0, face_vertex_list.length()):
                face_list[count] = face_id
                vertex_list[count] = face_vertex_list[vertex_id]
                count += 1

        while not to_iter_polygon.isDone():

            to_center_point = to_iter_polygon.center(space)

            closest_normal = [1000, 0]
            while not iter_polygon.isDone():

                center_point = iter_polygon.center(space)
                distance = to_center_point.distanceTo(center_point)
                if distance <= closest_normal[0]:
                    iter_polygon.getNormal(normal, space)
                    closest_normal[0] = distance
                    closest_normal[1] = normal * matrix
                iter_polygon.next()

            for i in range(to_iter_polygon.polygonVertexCount()):
                normal_list.append(normal)

            iter_polygon.reset()
            to_iter_polygon.next()
        to_replace_mesh.setFaceVertexNormals(normal_list, face_list, vertex_list, space)

    @staticmethod
    def transfer_vertex_normal_uv(matrix_values):
        replaced = pm.PyNode(pm.ls(sl=1)[0]).__apimdagpath__()
        to_replace = pm.PyNode(pm.ls(sl=1)[1]).__apimdagpath__()

        to_replace_mesh = om.MFnMesh(to_replace)
        to_iter_polygon = om.MItMeshPolygon(to_replace)
        iter_polygon = om.MItMeshPolygon(replaced)

        count = 0
        ptr = om.MScriptUtil()
        normal = om.MVector()
        normal_list = om.MVectorArray()
        face_list = om.MIntArray()
        face_list.setLength(to_replace_mesh.numFaceVertices())
        vertex_list = om.MIntArray()
        vertex_list.setLength(to_replace_mesh.numFaceVertices())

        matrix = om.MMatrix()
        om.MScriptUtil().createMatrixFromList(matrix_values, matrix)

        uv_point = ptr.asFloat2Ptr()
        for face_id in range(0, to_replace_mesh.numPolygons()):

            face_vertex_list = om.MIntArray()
            to_replace_mesh.getPolygonVertices(face_id, face_vertex_list)

            for vertex_id in range(0, face_vertex_list.length()):
                face_list[count] = face_id
                vertex_list[count] = face_vertex_list[vertex_id]
                count += 1

        while not to_iter_polygon.isDone():

            to_center_point = to_iter_polygon.center()
            to_iter_polygon.getUVAtPoint(to_center_point, uv_point)
            to_uv_coordinate = om.MPoint(om.MScriptUtil.getFloat2ArrayItem(uv_point, 0, 0),
                                         om.MScriptUtil.getFloat2ArrayItem(uv_point, 0, 1))

            closest_normal = [1000, 0]
            while not iter_polygon.isDone():

                center_point = iter_polygon.center()
                iter_polygon.getUVAtPoint(center_point, uv_point)
                uv_coordinate = om.MPoint(om.MScriptUtil.getFloat2ArrayItem(uv_point, 0, 0),
                                          om.MScriptUtil.getFloat2ArrayItem(uv_point, 0, 1))
                distance = uv_coordinate.distanceTo(to_uv_coordinate)
                if distance <= closest_normal[0]:
                    iter_polygon.getNormal(normal, om.MSpace.kWorld)
                    closest_normal[0] = distance
                    closest_normal[1] = normal

                iter_polygon.next()
            for i in range(to_iter_polygon.polygonVertexCount()):
                normal_list.append(normal)

            iter_polygon.reset()
            to_iter_polygon.next()
        to_replace_mesh.setFaceVertexNormals(normal_list, face_list, vertex_list, om.MSpace.kWorld)

    @staticmethod
    def transfer_along_normal(matrix_values, space):

        replaced = pm.PyNode(pm.ls(sl=1)[0]).__apimdagpath__()
        to_replace = pm.PyNode(pm.ls(sl=1)[1]).__apimdagpath__()

        replaced_mesh = om.MFnMesh(replaced)
        to_replace_mesh = om.MFnMesh(to_replace)
        to_iter_polygon = om.MItMeshPolygon(to_replace)

        count = 0
        ptr = om.MScriptUtil()
        normal = om.MVector()
        normal_list = om.MVectorArray()
        face_list = om.MIntArray()
        face_list.setLength(to_replace_mesh.numFaceVertices())
        vertex_list = om.MIntArray()
        vertex_list.setLength(to_replace_mesh.numFaceVertices())
        matrix = om.MMatrix()
        om.MScriptUtil().createMatrixFromList(matrix_values, matrix)

        hit_face = ptr.asIntPtr()

        while not to_iter_polygon.isDone():

            to_center_point = to_iter_polygon.center(space)
            to_iter_polygon.getNormal(normal, space)
            hit = replaced_mesh.closestIntersection(om.MFloatPoint(to_center_point), om.MFloatVector(normal), None,
                                                    None, None, space, 999, True,
                                                    None, om.MFloatPoint(), None, hit_face, None, None, None)

            if hit:
                replaced_mesh.getPolygonNormal(ptr.getInt(hit_face), normal, space)
                normal = normal * matrix
                vertices = om.MIntArray()
                to_iter_polygon.getVertices(vertices)
                for vertex_id in range(to_iter_polygon.polygonVertexCount()):
                    face_list[count] = to_iter_polygon.index()
                    vertex_list[count] = vertices[vertex_id]
                    normal_list.append(normal)
                    count += 1

            to_iter_polygon.next()
        face_list.setLength(count)
        vertex_list.setLength(count)
        normal_list.setLength(count)
        to_replace_mesh.setFaceVertexNormals(normal_list, face_list, vertex_list, space)


ui = UI()

ui.show()


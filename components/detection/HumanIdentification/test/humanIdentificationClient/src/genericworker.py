#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#    Copyright (C) 2020 by YOUR NAME HERE
#
#    This file is part of RoboComp
#
#    RoboComp is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    RoboComp is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with RoboComp.  If not, see <http://www.gnu.org/licenses/>.

import sys, Ice, os
from PySide2 import QtWidgets, QtCore

ROBOCOMP = ''
try:
    ROBOCOMP = os.environ['ROBOCOMP']
except KeyError:
    print('$ROBOCOMP environment variable not set, using the default value /opt/robocomp')
    ROBOCOMP = '/opt/robocomp'

Ice.loadSlice("-I ./src/ --all ./src/CommonBehavior.ice")
import RoboCompCommonBehavior

Ice.loadSlice("-I ./src/ --all ./src/CameraSimple.ice")
import RoboCompCameraSimple
Ice.loadSlice("-I ./src/ --all ./src/MultiModalHumanIdentification.ice")
import RoboCompMultiModalHumanIdentification

class ImgType(list):
    def __init__(self, iterable=list()):
        super(ImgType, self).__init__(iterable)

    def append(self, item):
        assert isinstance(item, byte)
        super(ImgType, self).append(item)

    def extend(self, iterable):
        for item in iterable:
            assert isinstance(item, byte)
        super(ImgType, self).extend(iterable)

    def insert(self, index, item):
        assert isinstance(item, byte)
        super(ImgType, self).insert(index, item)

setattr(RoboCompCameraSimple, "ImgType", ImgType)

class ImgType(list):
    def __init__(self, iterable=list()):
        super(ImgType, self).__init__(iterable)

    def append(self, item):
        assert isinstance(item, byte)
        super(ImgType, self).append(item)

    def extend(self, iterable):
        for item in iterable:
            assert isinstance(item, byte)
        super(ImgType, self).extend(iterable)

    def insert(self, index, item):
        assert isinstance(item, byte)
        super(ImgType, self).insert(index, item)

setattr(RoboCompMultiModalHumanIdentification, "ImgType", ImgType)

class BoundingBox(list):
    def __init__(self, iterable=list()):
        super(BoundingBox, self).__init__(iterable)

    def append(self, item):
        assert isinstance(item, int)
        super(BoundingBox, self).append(item)

    def extend(self, iterable):
        for item in iterable:
            assert isinstance(item, int)
        super(BoundingBox, self).extend(iterable)

    def insert(self, index, item):
        assert isinstance(item, int)
        super(BoundingBox, self).insert(index, item)

setattr(RoboCompMultiModalHumanIdentification, "BoundingBox", BoundingBox)

class BoundingBoxList(list):
    def __init__(self, iterable=list()):
        super(BoundingBoxList, self).__init__(iterable)

    def append(self, item):
        assert isinstance(item, RoboCompMultiModalHumanIdentification.BoundingBox)
        super(BoundingBoxList, self).append(item)

    def extend(self, iterable):
        for item in iterable:
            assert isinstance(item, RoboCompMultiModalHumanIdentification.BoundingBox)
        super(BoundingBoxList, self).extend(iterable)

    def insert(self, index, item):
        assert isinstance(item, RoboCompMultiModalHumanIdentification.BoundingBox)
        super(BoundingBoxList, self).insert(index, item)

setattr(RoboCompMultiModalHumanIdentification, "BoundingBoxList", BoundingBoxList)

class LabelList(list):
    def __init__(self, iterable=list()):
        super(LabelList, self).__init__(iterable)

    def append(self, item):
        assert isinstance(item, str)
        super(LabelList, self).append(item)

    def extend(self, iterable):
        for item in iterable:
            assert isinstance(item, str)
        super(LabelList, self).extend(iterable)

    def insert(self, index, item):
        assert isinstance(item, str)
        super(LabelList, self).insert(index, item)

setattr(RoboCompMultiModalHumanIdentification, "LabelList", LabelList)






class GenericWorker(QtCore.QObject):

    kill = QtCore.Signal()

    def __init__(self, mprx):
        super(GenericWorker, self).__init__()

        self.camerasimple_proxy = mprx["CameraSimpleProxy"]
        self.multimodalhumanidentification_proxy = mprx["MultiModalHumanIdentificationProxy"]

        self.mutex = QtCore.QMutex(QtCore.QMutex.Recursive)
        self.Period = 30
        self.timer = QtCore.QTimer(self)


    @QtCore.Slot()
    def killYourSelf(self):
        rDebug("Killing myself")
        self.kill.emit()

    # \brief Change compute period
    # @param per Period in ms
    @QtCore.Slot(int)
    def setPeriod(self, p):
        print("Period changed", p)
        self.Period = p
        self.timer.start(self.Period)

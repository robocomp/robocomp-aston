#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
#    Copyright (C) 2020 by Shubh Maheshwari
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

Ice.loadSlice("-I ./src/ --all ./src/MPTFeatures.ice")
import RoboCompMPTFeatures

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

setattr(RoboCompMPTFeatures, "ImgType", ImgType)

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

setattr(RoboCompMPTFeatures, "BoundingBox", BoundingBox)

class BoundingBoxList(list):
    def __init__(self, iterable=list()):
        super(BoundingBoxList, self).__init__(iterable)

    def append(self, item):
        assert isinstance(item, RoboCompMPTFeatures.BoundingBox)
        super(BoundingBoxList, self).append(item)

    def extend(self, iterable):
        for item in iterable:
            assert isinstance(item, RoboCompMPTFeatures.BoundingBox)
        super(BoundingBoxList, self).extend(iterable)

    def insert(self, index, item):
        assert isinstance(item, RoboCompMPTFeatures.BoundingBox)
        super(BoundingBoxList, self).insert(index, item)

setattr(RoboCompMPTFeatures, "BoundingBoxList", BoundingBoxList)

class TrackingIdList(list):
    def __init__(self, iterable=list()):
        super(TrackingIdList, self).__init__(iterable)

    def append(self, item):
        assert isinstance(item, int)
        super(TrackingIdList, self).append(item)

    def extend(self, iterable):
        for item in iterable:
            assert isinstance(item, int)
        super(TrackingIdList, self).extend(iterable)

    def insert(self, index, item):
        assert isinstance(item, int)
        super(TrackingIdList, self).insert(index, item)

setattr(RoboCompMPTFeatures, "TrackingIdList", TrackingIdList)

class Feature(list):
    def __init__(self, iterable=list()):
        super(Feature, self).__init__(iterable)

    def append(self, item):
        assert isinstance(item, float)
        super(Feature, self).append(item)

    def extend(self, iterable):
        for item in iterable:
            assert isinstance(item, float)
        super(Feature, self).extend(iterable)

    def insert(self, index, item):
        assert isinstance(item, float)
        super(Feature, self).insert(index, item)

setattr(RoboCompMPTFeatures, "Feature", Feature)

class Features(list):
    def __init__(self, iterable=list()):
        super(Features, self).__init__(iterable)

    def append(self, item):
        assert isinstance(item, RoboCompMPTFeatures.Feature)
        super(Features, self).append(item)

    def extend(self, iterable):
        for item in iterable:
            assert isinstance(item, RoboCompMPTFeatures.Feature)
        super(Features, self).extend(iterable)

    def insert(self, index, item):
        assert isinstance(item, RoboCompMPTFeatures.Feature)
        super(Features, self).insert(index, item)

setattr(RoboCompMPTFeatures, "Features", Features)

class TImageList(list):
    def __init__(self, iterable=list()):
        super(TImageList, self).__init__(iterable)

    def append(self, item):
        assert isinstance(item, RoboCompMPTFeatures.TImage)
        super(TImageList, self).append(item)

    def extend(self, iterable):
        for item in iterable:
            assert isinstance(item, RoboCompMPTFeatures.TImage)
        super(TImageList, self).extend(iterable)

    def insert(self, index, item):
        assert isinstance(item, RoboCompMPTFeatures.TImage)
        super(TImageList, self).insert(index, item)

setattr(RoboCompMPTFeatures, "TImageList", TImageList)


import mptfeaturesI




class GenericWorker(QtCore.QObject):

    kill = QtCore.Signal()

    def __init__(self, mprx):
        super(GenericWorker, self).__init__()


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

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

Ice.loadSlice("-I ./src/ --all ./src/GaitFeatures.ice")
import RoboCompGaitFeatures

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

setattr(RoboCompGaitFeatures, "ImgType", ImgType)

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

setattr(RoboCompGaitFeatures, "Feature", Feature)

class FeatureList(list):
    def __init__(self, iterable=list()):
        super(FeatureList, self).__init__(iterable)

    def append(self, item):
        assert isinstance(item, RoboCompGaitFeatures.Feature)
        super(FeatureList, self).append(item)

    def extend(self, iterable):
        for item in iterable:
            assert isinstance(item, RoboCompGaitFeatures.Feature)
        super(FeatureList, self).extend(iterable)

    def insert(self, index, item):
        assert isinstance(item, RoboCompGaitFeatures.Feature)
        super(FeatureList, self).insert(index, item)

setattr(RoboCompGaitFeatures, "FeatureList", FeatureList)

class TImages(list):
    def __init__(self, iterable=list()):
        super(TImages, self).__init__(iterable)

    def append(self, item):
        assert isinstance(item, RoboCompGaitFeatures.TImage)
        super(TImages, self).append(item)

    def extend(self, iterable):
        for item in iterable:
            assert isinstance(item, RoboCompGaitFeatures.TImage)
        super(TImages, self).extend(iterable)

    def insert(self, index, item):
        assert isinstance(item, RoboCompGaitFeatures.TImage)
        super(TImages, self).insert(index, item)

setattr(RoboCompGaitFeatures, "TImages", TImages)

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

setattr(RoboCompGaitFeatures, "TrackingIdList", TrackingIdList)


import gaitfeaturesI




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

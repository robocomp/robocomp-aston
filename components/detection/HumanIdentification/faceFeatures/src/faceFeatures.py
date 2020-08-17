#!/usr/bin/env python3
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
#

# \mainpage RoboComp::faceFeatures
#
# \section intro_sec Introduction
#
# Some information about the component...
#
# \section interface_sec Interface
#
# Descroption of the interface provided...
#
# \section install_sec Installation
#
# \subsection install1_ssec Software depencences
# Software dependences....
#
# \subsection install2_ssec Compile and install
# How to compile/install the component...
#
# \section guide_sec User guide
#
# \subsection config_ssec Configuration file
#
# <p>
# The configuration file...
# </p>
#
# \subsection execution_ssec Execution
#
# Just: "${PATH_TO_BINARY}/faceFeatures --Ice.Config=${PATH_TO_CONFIG_FILE}"
#
# \subsection running_ssec Once running
#
#
#

import sys
import traceback
import IceStorm
import time
import os
import copy
import argparse
import mxnet as mx

from termcolor import colored
# Ctrl+c handling
import signal

from PySide2 import QtCore

from specificworker import *
from lib import face_model # Main face model

class CommonBehaviorI(RoboCompCommonBehavior.CommonBehavior):
    def __init__(self, _handler):
        self.handler = _handler
    def getFreq(self, current = None):
        self.handler.getFreq()
    def setFreq(self, freq, current = None):
        self.handler.setFreq()
    def timeAwake(self, current = None):
        try:
            return self.handler.timeAwake()
        except:
            print('Problem getting timeAwake')
    def killYourSelf(self, current = None):
        self.handler.killYourSelf()
    def getAttrList(self, current = None):
        try:
            return self.handler.getAttrList()
        except:
            print('Problem getting getAttrList')
            traceback.print_exc()
            status = 1
            return

#SIGNALS handler
def sigint_handler(*args):
    QtCore.QCoreApplication.quit()
    
if __name__ == '__main__':
    app = QtCore.QCoreApplication(sys.argv)
    parser = argparse.ArgumentParser()
    parser.add_argument('iceconfigfile', nargs='?', type=str, default='etc/config')
    parser.add_argument('--startup-check', action='store_true')

    parser.add_argument('--image-size', default='112,112', help='')
    parser.add_argument('--model', default='./src/PretrainedModels/model-y1-test2/', help='path to load model.')
    #512-D feature is dependent to model. it means same face feature from different model will not be similar at all.
    parser.add_argument('--gpu', default=0, type=int, help='gpu id')
    parser.add_argument('--det', default=0, type=int, help='mtcnn option, 1 means using R+O, 0 means detect from beginning')
    parser.add_argument('--flip', default=0, type=int, help='whether do lr flip aug')
    parser.add_argument('--threshold', default=1.24, type=float, help='ver dist threshold')
    parser.add_argument('--score', default=0.99, type=float, help='if detected face''s score is lower than this, than it will not be detected as face')#0.999여도 좋을지도

    args = parser.parse_args()

    ic = Ice.initialize(args.iceconfigfile)
    status = 0
    mprx = {}
    parameters = {}
    for i in ic.getProperties():
        parameters[str(i)] = str(ic.getProperties().getProperty(i))

    if status == 0:
        model = face_model.FaceModel(args, ctx=mx.cpu() if args.gpu == -1 else mx.gpu(args.gpu))
        worker = SpecificWorker(mprx, model,args.startup_check)
        worker.setParams(parameters)
    else:
        print("Error getting required connections, check config file")
        sys.exit(-1)

    adapter = ic.createObjectAdapter('FaceFeatures')
    adapter.add(facefeaturesI.FaceFeaturesI(worker), ic.stringToIdentity('facefeatures'))
    adapter.activate()

    signal.signal(signal.SIGINT, sigint_handler)
    app.exec_()

    if ic:
        # try:
        ic.destroy()
        # except:
        #     traceback.print_exc()
        #     status = 1

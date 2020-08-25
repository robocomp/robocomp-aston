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
#

# Imports for running center track
import cv2
import sys
import numpy as np
CENTERTRACK_PATH = "./src/lib/"
sys.path.insert(0, CENTERTRACK_PATH)
from detector import Detector
from opts import opts
import matplotlib.pyplot as plt


from torchreid.utils import FeatureExtractor


from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QApplication
from genericworker import *
import RoboCompMPTFeatures


# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# sys.path.append('/opt/robocomp/lib')
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel

class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000
        if startup_check:
            self.startup_check()
        else:
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)


        # Load center track, our tracking module
        opt = opts().init()
        self.detector = Detector(opt)

        # Reid reture extractor 
        self.reid_extractor = FeatureExtractor(model_name='shufflenet',model_path='/home/shubh/Downloads/shufflenet-bee1b265.pth.tar',device='cuda')


    def __del__(self):
        print('SpecificWorker destructor')

    def setParams(self, params):
        #try:
        #   self.innermodel = InnerModel(params["InnerModelPath"])
        #except:
        #   traceback.print_exc()
        #   print("Error reading config params")
        return True


    @QtCore.Slot()
    def compute(self):
        print('SpecificWorker.compute...')
        # computeCODE
        # try:
        #   self.differentialrobot_proxy.setSpeedBase(100, 0)
        # except Ice.Exception as e:
        #   traceback.print_exc()
        #   print(e)

        # The API of python-innermodel is not exactly the same as the C++ version
        # self.innermodel.updateTransformValues('head_rot_tilt_pose', 0, 0, 0, 1.3, 0, 0)
        # z = librobocomp_qmat.QVec(3,0)
        # r = self.innermodel.transform('rgbd', z, 'laser')
        # r.printvector('d')
        # print(r[0], r[1], r[2])

        return True

    def startup_check(self):
        QTimer.singleShot(200, QApplication.instance().quit)



    # =============== Methods for Component Implements ==================
    # ===================================================================

    #
    # IMPLEMENTATION of getReidFeature method from MPTFeatures interface
    #
    def MPTFeatures_detectHumans(self, im):
    
        # Convert image to numpy format
        arr = np.fromstring(im.image, np.uint8).reshape((im.height, im.width, im.depth))
        ret = self.detector.run(arr)

        # Copy all data to Robocomp.DetectedHumans class
        detectedHumans = RoboCompMPTFeatures.DetectedHumans()
        boundingBoxList = RoboCompMPTFeatures.BoundingBoxList()
        trackingidlist = RoboCompMPTFeatures.TrackingIdList()

        # Find all humans detected
        bbox_list = []
        tracking_list = []
        for r in ret['results']:
            if r['class'] == 1 and np.abs((r['bbox'][3]-r['bbox'][1])*(r['bbox'][2]-r['bbox'][0])) > 400: # If person is detected and area greater than 20x20
                bbox_list.append(r['bbox'].astype(np.uint32))
                tracking_list.append(r['tracking_id'])
        
        detectedHumans.numhumans = len(bbox_list)        
        detectedHumans.boundingboxes = np.array(bbox_list).astype(np.int32)
        detectedHumans.trackingidlist = tracking_list    

        return detectedHumans    
    # ===================================================================
    # ===================================================================
    def MPTFeatures_getReidFeature(self, imlist):
        """
            Extract person re-identification features for 
        """
        images = [ np.fromstring(im.image, np.uint8).reshape((im.height, im.width, im.depth)) for im in imlist] # Convert TImage to numpy array to send as input to the model    
        
        features = self.reid_extractor(images).data.cpu().numpy()

        features /= np.linalg.norm(features,axis=1,keepdims=True) + 1e-8# Normalize for comparision

        reidFeatures = RoboCompMPTFeatures.Features()
        for i,feature in enumerate(features):
            feature = RoboCompMPTFeatures.Feature(iterable=feature)
            reidFeatures.append(feature)

        return reidFeatures

    ######################
    # From the RoboCompMPTFeatures you can use this types:
    # RoboCompMPTFeatures.TImage
    # RoboCompMPTFeatures.Features


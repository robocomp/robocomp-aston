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

# Imports 
import cv2
import numpy as np 


from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QApplication
from genericworker import *

import RoboCompFaceFeatures

# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# sys.path.append('/opt/robocomp/lib')
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel

class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, face_model, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 2000
        if startup_check:
            self.startup_check()
        else:
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)

        self.face_model = face_model    

    def __del__(self):
        print('SpecificWorker destructor')

    def setParams(self, params):
        #try:
        #	self.innermodel = InnerModel(params["InnerModelPath"])
        #except:
        #	traceback.print_exc()
        #	print("Error reading config params")
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
    # IMPLEMENTATION of detectFace method from FaceFeatures interface
    #
    def FaceFeatures_detectFace(self, im):    
        # Given the input as an image this the function will detect the faces and return their features 

        # Convert the input TImage object to numpy array, resize it to 640,360 
        arr = np.fromstring(im.image, np.uint8)
        arr = np.reshape(arr, (im.height, im.width, im.depth))
        # arr = cv2.resize(arr,(640,360)) # For faster computation


        boxes, points, results = self.face_model.get_input_new(face_img=arr) #get face boxes, points(eye, nose, mouth), aligned images
        detectedFaces = RoboCompFaceFeatures.DetectedFaces()

        if boxes is not None: # Atleast one person detected
            detectedFaces.numfaces = len(boxes)
            boxes[:,-1] *= 100 # Multiply score with 100 to convert from plot to percentage
            detectedFaces.boundingboxes = np.array(boxes).astype(np.int32)

            alignedfaces = RoboCompFaceFeatures.AlignedFaceList()
            for result in results:
                aim = RoboCompFaceFeatures.TImage()
                aim.image = result.tostring()
                aim.height, aim.width, aim.depth = result.shape
                alignedfaces.append(aim)

            detectedFaces.alignedfaces = alignedfaces

        return detectedFaces
    #
    # IMPLEMENTATION of getFaceFeature method from FaceFeatures interface
    #
    def FaceFeatures_getFaceFeature(self, alignedimlist):
        # Given the input as a list of images already aligned by FaceFeatures_detectFace the function will return their features 
        results = np.array([ np.fromstring(im.image, np.uint8).reshape((im.height, im.width, im.depth)) for im in alignedimlist]) # Convert TImage to numpy array to send as input to the model    
        features = self.face_model.get_feature_new(results)
        
        faceFeatureList = RoboCompFaceFeatures.FeatureList()
        for feature in features:
            feature = RoboCompFaceFeatures.Feature(iterable=feature)
            faceFeatureList.append(feature)
        return faceFeatureList
    # ===================================================================
    # ===================================================================


    ######################
    # From the RoboCompFaceFeatures you can use this types:
    # RoboCompFaceFeatures.TImage
    # RoboCompFaceFeatures.Features


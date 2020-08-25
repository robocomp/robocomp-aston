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

import os 
import time
import numpy as np
import torch
import cv2
import traceback
from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QApplication
from genericworker import *
import RoboCompGaitFeatures

sys.path.append("./src/lib")
from models import UNet # Model to perform segmentation
from base.base_inference import ImageListInference
from GaitSet.gaitset import SetNet

# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# sys.path.append('/opt/robocomp/lib')
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel

class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, opts,startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 50
        if startup_check:
            self.startup_check()
        else:
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)

        self.opts = opts # Copy user options
        self.wait_frames = 5 # Wait for these many frames to get stored before calling gaitset (see gaitSet/pretreatment.py)
        # Dictonary to store mapping between tracking id and segmentation mask
        self.id2mask = {}


        # Segmentation module
        segmentation_model = UNet(backbone="resnet18", num_classes=2)
        segmentation_model.load_state_dict(torch.load("./src/PretrainedModels/UNet_ResNet18.pth", map_location="cpu")['state_dict'], strict=False)
        self.segmentation_inference = ImageListInference(segmentation_model,opts)

        # Gait feature extraction
        self.gait_model = SetNet(256)
        self.gait_model.load_state_dict(torch.load("./src/PretrainedModels/GaitSet_CASIA-B_73_False_256_0.2_128_full_30-80000-encoder.ptm",map_location="cpu"),strict=False)
        if self.opts.gpu >= 0:
            self.gait_model.cuda()
        self.gait_model.eval()

        # Variables to store data for computation
        self.lock = False # Lock from taking any more input until features are calculated
        self.input_image_list = [] # Store images in this list before performing segmentation
        self.input_tracking_id = [] # Store respective tracking id here

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

        if len(self.input_image_list) > 0:  

            while self.lock: # Wait if busy
                print("Waiting for module to get free")
                time.sleep(0.1)

            # Create segmentation mask 
            try:
                masklist = self.segmentation_inference.run([np.fromstring(im.image,np.uint8).reshape((im.height,im.width,im.depth)) for im in self.input_image_list]) # Extract segmentation mask from person's image    
                # Store segmentation mask by tracking ids
                for tr_id,mask in zip(self.input_tracking_id,masklist):
                    if mask.sum() < 400: # If white pixels less than 10% of the data continue
                        continue 
                    if tr_id not in self.id2mask:
                        self.id2mask[tr_id] = []
                    self.id2mask[tr_id].append(mask)

                    if len(self.id2mask[tr_id]) > 32: # Max length 32
                        self.id2mask[tr_id] = self.id2mask[tr_id][:-32]

            except Exception as e:
                traceback.print_exc()
                print([ (im.height,im.width,im.depth) for im in self.input_image_list])



            self.lock = True
            self.input_image_list  = [] # Clean 
            self.input_tracking_id = [] # Clean
            self.lock = False

        cv2.waitKey(1)
        return True

    def startup_check(self):
        QTimer.singleShot(200, QApplication.instance().quit)

    # =============== Methods for Component Implements ==================
    # ===================================================================

    #
    # IMPLEMENTATION of getGaitFeature method from GaitFeatures interface
    #
    def GaitFeatures_getGaitFeature(self, trackingIdlist):
    
        gaitfeatures = RoboCompGaitFeatures.FeatureList()
        for i,ind in enumerate(trackingIdlist):
            if ind in self.id2mask:
                if len(self.id2mask[ind]) > self.wait_frames:
                    silho = torch.Tensor(self.id2mask[ind]).unsqueeze(0)
                    feature,_ = self.gait_model(silho.cuda() if self.opts.gpu >= 0 else silho) # Call module to get features
                    feature = feature.view(-1).data.cpu().numpy()
                    feature /= np.linalg.norm(feature)
                else:
                    feature = []
            else:
                feature = []

            feature = RoboCompGaitFeatures.Feature(iterable=feature)
            gaitfeatures.append(feature)

        return gaitfeatures
    #
    # IMPLEMENTATION of storeGaitFeature method from GaitFeatures interface
    #
    def GaitFeatures_storeGaitFeature(self, imlist, trackingIdList):
    
        while self.lock:
            time.sleep(0.1) # Wait until lock is lifted 

        # Update 
        self.lock = True
        self.input_image_list.extend(imlist)
        self.input_tracking_id.extend(trackingIdList)

        if len(self.input_image_list) > 100:
        	self.input_image_list = self.input_image_list[:-100]
        	self.input_tracking_id = self.input_tracking_id[:-100]

        self.lock = False

    # ===================================================================
    # ===================================================================


    ######################
    # From the RoboCompGaitFeatures you can use this types:
    # RoboCompGaitFeatures.TImage


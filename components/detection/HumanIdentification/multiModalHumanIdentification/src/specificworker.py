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
import cv2
import numpy as np
import traceback

from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QApplication
from genericworker import *
import RoboCompMultiModalHumanIdentification
import RoboCompFaceFeatures
import RoboCompMPTFeatures
import RoboCompGaitFeatures

# Modules 
from database import Database, LiveDatabase
from trackingId2Label import TrackingId2Label


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

        # Our data structure to map tracking index to their respective labels
        self.id2label = TrackingId2Label()

        # TODO / Need to perform experiments,test for this 
        # Currently different features stored as ./database/modality/name.h5 
        self.database = {'face': Database("./database/face"),'gait':Database("./database/gait")}
        self.live_database = {'reid':LiveDatabase(),'face': LiveDatabase(),'gait':LiveDatabase()} # Store data for unknown classes
            
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
    # IMPLEMENTATION of addLabel method from MultiModalHumanIdentification interface
    #
    def MultiModalHumanIdentification_addLabel(self, trackingId, label,k=10):
        """
            Given the tracking id and the name of person. 
            Create .h5 file to store features from the live list 

            Note:- Make sure the tracking id is always the parent tracking id (self.id2label[tr_id] == tr_id or id2label[tr_id] == -1)

            @params: 
                trackingId: tracking id of the person: int
                label: name of the person: str
                k = number of samples to be stored person. Default 10  

            @returns:
                status : whether succesfully able to add to database or not 
        """
        tr_id = int(trackingId.split(':')[-1]) # Format "unknown:tr_id"
        # Check tr_id present in id2label
        assert len(self.id2label.not_present([tr_id])) == 0,f"Tracking id:{tr_id} not present in id2label" 
        # Check tr_id is parent
        assert tr_id == self.id2label._find(tr_id),f"Tracking id:{tr_id} not a parent in id2label" 

        children = self.id2label.children(tr_id)
        print("children",children)
        for modality in self.database:
            featurelist,imagelist = self.live_database[modality].deleteLabel(children) # Remove from the live list
            print(len(featurelist))
            try:
                self.database[modality].addLabel(label,featurelist,imagelist,k=k) # Add to the database and create and .h5 file
            except Exception: 
                traceback.print_exc()
                # If any error in updating the dataset, add the data back to live dataset
                self.live_database[modality].addLabel([tr_id]*len(featurelist),np.array(featurelist),np.array(imagelist))
                return 0 

        self.id2label.update([tr_id],[label])

        return 1
    #
    # IMPLEMENTATION of deleteLabel method from MultiModalHumanIdentification interface
    #
    def MultiModalHumanIdentification_deleteLabel(self, label):
        """
            Given the name of person, for the tracking id. 
            Create .h5 file to store features in the database

            Note:- Make sure the tracking id is always the parent tracking id (self.id2label[tr_id] == tr_id or id2label[tr_id] == -1)

            @params: 
                label: name of the person: str
                k = number of samples to be stored person. Default 10  

            @returns:
                status : whether succesfully able to add to database or not 
        """

        # Check trackingId present in id2label
        assert type(label) == str,f"Name of the person not string but:{type(label)}" 

        # Find tracking id mapped to the label, if present
        tr_id = None
        for k in self.id2label.dict:
            if self.id2label.dict[k] == label:
                tr_id = k
                break

        # For each modality delete the data 
        for modality in self.database:
            try:
                self.database[modality].deleteLabel(label) # Add to the database and create and .h5 file
            except Exception as e: 
                traceback.print_exc()
                return 0 
        if tr_id is not None:
            self.id2label.dict[tr_id] = -1

        return 1

    #
    # IMPLEMENTATION of getLabel method from MultiModalHumanIdentification interface
    #
    def _convert_TImage_object(self,orig_im,new_im): # Helper function
        # To pass the same object (have same declaration) between 2 robocomponets we need to make sure they they are compatilbe
        # eg. RoboCompMPTFeatures.TImage != RoboCompFaceFeatures.TImage, hence we need to create a new object and copy these values 
        new_im.width = orig_im.width
        new_im.height = orig_im.height
        new_im.depth = orig_im.depth
        new_im.image = orig_im.image
        return new_im

    def _find_face_ind(self,human_bbox,face_bbox):
        """
            Given human bounding boxes and face bounding box, check if able to detect face, if yes, then return its index 

            @param: human_bbox: Nx4, list of human bounding boxes
            @param: face_bbox: Mx4, list of face bounding boxes
            
            @return: face_inds: index of face if inside human bounding box 
        """    
        # print("Human BBOX:",human_bbox)
        # print("Face BBOX:",face_bbox)

        if len(face_bbox) == 0: # If not face detected, return nothing
            return [],[]

        human_inds = []
        face_inds = []
        for i,bbox in enumerate(human_bbox):
            # print("BBox:",bbox)
            cond1 =  np.logical_and(face_bbox[:,0] > bbox[0], face_bbox[:,1] > bbox[1])  
            cond2 =  np.logical_and(face_bbox[:,2] < bbox[2], face_bbox[:,3] < bbox[3])

            # print(cond1)
            # print(cond2)

            inds = np.where( np.logical_and(cond1,cond2) )[0]

            # print(f"Found Intersectons:{i} inds:{inds}")
            if len(inds) == 1: 
                # If only one face found in the human bounding box
                temp = 0                
            elif len(inds) > 1:
                # print("Found more than one person inside the box")
                # If multiple face inside a person's bounding box, 
                # choose the one closes to the center in x-axis/width
                # print(face_bbox[inds,[0,2]])
                temp = np.argmin(np.linalg.norm( (face_bbox[inds,0] + face_bbox[inds,2])/2 -  (bbox[0]+bbox[2])/2))
                
                # print(f"Result:{i} -> {inds[temp]}")
            else: # No person detectef
                continue
            human_inds.append(i)
            face_inds.append(inds[temp])

        return human_inds,face_inds 


    def MultiModalHumanIdentification_getLabel(self, im):

        # Convert im to numpy array         
        arr = np.fromstring(im.image, np.uint8).reshape((im.height, im.width, im.depth))

        # Detect humans present in the image 
        reid_im = self._convert_TImage_object(im,RoboCompMPTFeatures.TImage()) # Required by robocomp to make object compatible across components
        detectedHumans = self.mptfeatures_proxy.detectHumans(reid_im) # Contains the tracking ids, bounding boxes of person detected in the frame


        # If new tracking id detected then add to id2label data structure
        new_ind = self.id2label.not_present(detectedHumans.trackingidlist)
        if len(new_ind) > 0:
            
            # A person can have multiple tracking ids, hence first step is 
            # to use the apperance to find associations with previous tracklets. 
            # To do this we use human re-identification module 

            # Create the input for reid & gait component             
            reid_person_list = RoboCompMPTFeatures.TImageList()
            store_im = []
            for i in new_ind: # Segement all the humans, create the sub-image and add to TImageList clasd 
                bbox = detectedHumans.boundingboxes[i]
                new_image = arr[bbox[1]:bbox[3],bbox[0]:bbox[2],:]

                store_im.append(cv2.resize(new_image,(128,256)))

                nim = RoboCompMPTFeatures.TImage()
                nim.height, nim.width, nim.depth = new_image.shape
                nim.image = new_image.tostring()
                reid_person_list.append(nim)


            # Calculate reid features
            reid_features = self.mptfeatures_proxy.getReidFeature(reid_person_list) 
            reid_features = np.array(reid_features)
            
            # Search current reid tracking list     
            labels,dists = self.live_database['reid'].query(reid_features,thresh=10) # Find tracking ids similiar to new features 
            self.id2label.add([detectedHumans.trackingidlist[i] for i in new_ind],labels)
            self.live_database['reid'].addLabel([detectedHumans.trackingidlist[i] for i in new_ind],reid_features,np.array(store_im))            


            # for i,ind in enumerate(new_ind):
            #     print(f"New:{detectedHumans.trackingidlist[ind]} -> {labels[i]} dists:{dists[i]}")


        # Next we use face & gait recognition to find labels of unkown persons => here unknown is defined as person not recognized from the database              
        unknown_inds,unknown_ids = self.id2label.find_unknown(detectedHumans.trackingidlist)
        # print("Remaining ids:",unknown_ids)
        unknown_inds = []
        if len(unknown_inds) > 0: # If idenity of the person found 
            # Get face features from RoboCompFaceFeatures 
            face_im = self._convert_TImage_object(im,RoboCompFaceFeatures.TImage()) # Make object compatible across components
            # First detect faces 
            detectface = self.facefeatures_proxy.detectFace(face_im) # Contains bounding boxes of faces detected and aligned them for feature extraction

            # Check if the bounding box of the face is inside the bounding box of the person 
            human_inds,face_inds = self._find_face_ind([detectedHumans.boundingboxes[i] for i in unknown_inds ],np.array(detectface.boundingboxes))
            # print("Intersection Detected:",human_inds,face_inds)

            # If any face is present inside the persons bounding box
            if len(human_inds) > 0:
                face_features = self.facefeatures_proxy.getFaceFeature([detectface.alignedfaces[i] for i in face_inds])
                face_features = np.array(face_features)

                # print("Face Features:",face_features.shape)

                # Search the face database
                not_found,found,found_labels = self.database['face'].query(face_features,thresh=0.55) # Find tracking ids similiar to face features 

                # Update the labels with string 
                # print(f"Found Inds:{found} String labels:{found_labels}, Updating tracking ids:{[unknown_ids[human_inds[i]] for i in found]}")
                self.id2label.update([unknown_ids[human_inds[i]] for i in found],found_labels) 


                # print("Not found:",not_found)
                # For remaining inds search the current face live list     
                labels,dists = self.live_database['face'].query(face_features[not_found],thresh=0.55) # Find tracking ids similiar to new features 
                store_ind = [ i for i,x in enumerate(labels) if x !=-1 ] 

                # Add newly found mapping between not found tracking ids 
                self.id2label.update([unknown_ids[human_inds[not_found[i]]] for i in store_ind],labels[store_ind])

                # Add Data about unknown label to face live list 
                # Find aligned faces
                store_im = []
                for i in not_found: 
                    new_im = detectface.alignedfaces[face_inds[i]]
                    new_im = np.fromstring(new_im.image,np.uint8).reshape((new_im.height, new_im.width, new_im.depth))
                    store_im.append(new_im)

                self.live_database['face'].addLabel([unknown_ids[human_inds[i]] for i in not_found],face_features[not_found],np.array(store_im))


        # Use gait recognition
        unknown_inds,unknown_ids = self.id2label.find_unknown(detectedHumans.trackingidlist)            
        if len(unknown_inds) > 0: # If idenity of the person found 
            # from Gait module return features for tracking ind 

            gait_features = self.gaitfeatures_proxy.getGaitFeature(unknown_ids)
            # Search first ind indexes for which gait is found unknown gait list
            present_inds = [i for i,x in enumerate(gait_features) if len(x) > 0]
            if len(present_inds) > 0:
                gait_features = np.array([gait_features[i] for i in present_inds])
                # Search the face database
                not_found,found,found_labels = self.database['gait'].query(gait_features,thresh=0.55) # Find tracking ids similiar to face features 

                # Update the labels with string 
                # print(f"Found Inds:{found} String labels:{found_labels}, Updating tracking ids:{[unknown_ids[human_inds[i]] for i in found]}")
                self.id2label.update([unknown_ids[present_inds[i]] for i in found],found_labels) 


                # print("Not found:",not_found)
                # For remaining inds search the current face live list     
                labels,dists = self.live_database['gait'].query(gait_features[not_found],thresh=0.55) # Find tracking ids similiar to new features 
                store_ind = [ i for i,x in enumerate(labels) if x !=-1 ] 

                # Add newly found mapping between not found tracking ids 
                self.id2label.update([unknown_ids[present_inds[not_found[i]]] for i in store_ind],labels[store_ind])

                # Add Data about unknown label to face live list 
                self.live_database['gait'].addLabel([unknown_ids[present_inds[i]] for i in not_found],gait_features[not_found],np.zeros((len(not_found),64,64)))

        # Store remaining data        
        unknown_inds,unknown_ids = self.id2label.find_unknown(detectedHumans.trackingidlist)            
        if len(unknown_inds) > 0:
            gait_person_list = RoboCompGaitFeatures.TImages()
            for i in unknown_inds: # Segement all the humans, create the sub-image and add to TImageList clasd 
                bbox = detectedHumans.boundingboxes[i]
                if bbox[1] == bbox[3]:
                    bbox[3] += 1

                if bbox[0] == bbox[2]:
                    bbox[2] += 1

                new_image = arr[bbox[1]:bbox[3],bbox[0]:bbox[2],:]

                nim = RoboCompGaitFeatures.TImage()
                nim.height, nim.width, nim.depth = new_image.shape
                nim.image = new_image.tostring()
                gait_person_list.append(nim)

            # Store values for gait recognition
            self.gaitfeatures_proxy.storeGaitFeature(gait_person_list,unknown_ids)



        # Copy all data to Robocomp.RecognisedHumans class     
        recognisedHumans = RoboCompMultiModalHumanIdentification.RecognisedHumans()
        recognisedHumans.numhumans = len(detectedHumans.boundingboxes)
        recognisedHumans.boundingboxes = list(detectedHumans.boundingboxes)
        recognisedHumans.labellist = self.id2label.query(detectedHumans.trackingidlist)

        return recognisedHumans
        # # # Get Reid Features from RoboCompReID features
        # # reid_im = self._convert_TImage_object(im,RoboCompMPTFeatures.TImage()) # Make object compatible across components
        # # face_features = self.mptfeatures_proxy.getReidFeature(reid_im)
    # ===================================================================
    # ===================================================================


    ######################
    # From the RoboCompFaceFeatures you can call this methods:
    # self.facefeatures_proxy.detectFace(...)
    # self.facefeatures_proxy.getFaceFeature(...)

    ######################
    # From the RoboCompFaceFeatures you can use this types:
    # RoboCompFaceFeatures.TImage
    # RoboCompFaceFeatures.DetectedFaces

    ######################
    # From the RoboCompGaitFeatures you can call this methods:
    # self.gaitfeatures_proxy.getGaitFeature(...)
    # self.gaitfeatures_proxy.storeGaitFeature(...)

    ######################
    # From the RoboCompGaitFeatures you can use this types:
    # RoboCompGaitFeatures.TImage

    ######################
    # From the RoboCompMPTFeatures you can call this methods:
    # self.mptfeatures_proxy.getReidFeature(...)

    ######################
    # From the RoboCompMPTFeatures you can use this types:
    # RoboCompMPTFeatures.TImage
    # RoboCompMPTFeatures.Features

    ######################
    # From the RoboCompMultiModalHumanIdentification you can use this types:
    # RoboCompMultiModalHumanIdentification.TImage


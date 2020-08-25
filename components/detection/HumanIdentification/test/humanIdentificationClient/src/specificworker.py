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
import os
import cv2
import numpy as np
import traceback
import wx

from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QApplication
from genericworker import *
import RoboCompMultiModalHumanIdentification


# If RoboComp was compiled with Python bindings you can use InnerModel in Python
# sys.path.append('/opt/robocomp/lib')
# import librobocomp_qmat
# import librobocomp_osgviewer
# import librobocomp_innermodel

class GUI():
    """
        This method will be a simple way to interact with our system  
        
        By hovering the mouse over the person, the person will get highlighted 

        We can double-click on a person: 
            1) If we do not know the person, 
                we can add his details to the database
            2) If we do known the person, we can delete the person  


        - This class has these public functions:
        => update_mouse_location(): Connect with cv2 callback to update mouse position
        => intersect(bbox): Check if mouse inside bbox   
        => find_unknown(inds): Check if tracking id maps to a known or unkown person, return the parent tracking ids for persons not present in the database  
        => add(inds,labels): Add new tracking ids 
        => update(inds, new_label): update tracking ids with new labels 
        
        This is similiar to how union find is used for Krushkal's method in minimum spanning tree
    """
    def __init__(self):
        super(GUI, self).__init__() 
        
        # Position of the mouse
        self.x = 0 
        self.y = 0 
        self.open_popup = False # Pop up button used to add pr delete label    

        self.app = wx.App()
        self.app.MainLoop()


    def update_mouse_location(self,event,x,y,flags,param):
        """
            Update mouse using cv2.callback function 

            @params: 
                event   : mouse click event 
                x,y     : mouse positions
        """
        self.x = x
        self.y = y
        if event == cv2.EVENT_LBUTTONDBLCLK:
            self.open_popup = True

    def intersect(self,bbox):
        """
            Find whether mouse present inside the bounding box
            @params
                bbox: bounding box of person : [x1,y1,x2,y2]

            @returns:
                True/False : whether mouse is present inside the bbox
        """
        return bbox[0] < self.x and bbox[1] < self.y and bbox[2] > self.x and bbox[3] > self.y

    def get_user_input(self,parent=None, message="Add Name" , default_value=''):
        """
            When unknown person gets double clicked, get information
        """
        dlg = wx.TextEntryDialog(parent, message)
        dlg.ShowModal()
        result = dlg.GetValue()
        dlg.Destroy()
        return result

    def ok_button(self,message):
        wx.MessageDialog(None, message, 'Updated', wx.OK | wx.ICON_INFORMATION).ShowModal()
        # dlg = wx.MessageDialog(parent, message)
        # dlg.ShowModal()
        # result = dlg.GetValue()
        # dlg.Destroy()
        print("Message:",message)

class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, video_path,startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 50
        if startup_check:
            self.startup_check()
        else:
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)

        if video_path == 'CameraSimple':
            self.cap = "CameraSimple"
        elif video_path == 'webcam':
            self.cap = cv2.VideoCapture(0)
        else:
            if os.path.isfile(video_path):
                self.cap = cv2.VideoCapture(video_path)
            else:
                raise FileNotFoundError(f"Unable to load {video_path}")

        self.gui = GUI()

    def __del__(self):
        print('SpecificWorker destructor')

    def setParams(self, params):
        self.label2color = {} # Store random color for tracking ids 
        return True

    def resize(self,frame,max_length=640):
        """
            # For faster computation resize the image to maximum size of 640
            @params:
                frame: image to be resized : np.darray HxWx3
                max_length: maximum size of a dimension: int: default 640
        """

        if np.max(frame.shape) < 640:
            return frame
        elif frame.shape[0] > frame.shape[1]:
            r = (frame.shape[1]*640)//frame.shape[0]
            frame = cv2.resize(frame,(r,640)) 
        else: 
            r = (frame.shape[0]*640)//frame.shape[1]
            frame = cv2.resize(frame,(640,r))

        return frame 
    def read_frame(self):
        """
            For different sensors to take input, this method uses them to read each image
        """

        if self.cap == "CameraSimple":
            data = self.camerasimple_proxy.getImage()
            frame = np.fromstring(data.image, np.uint8).reshape((data.height, data.width, data.depth))
        elif type(self.cap) == cv2.VideoCapture:
            _,frame = self.cap.read()
            if frame is not None:
                frame = self.resize(frame) # Preprocess
                # frame = frame.transpose((1,0,2))
        else:
            frame = None
            raise Error("Unable to load video from input")

        return frame


    def _get_rand_color(self):
        c = ((np.random.random((3)) * 0.6 + 0.2) * 255).astype(np.int32).tolist()
        return c

    @QtCore.Slot()
    def compute(self):
        print('SpecificWorker.compute...')
        # compute CODE
        try:
            frame = self.read_frame()
            if frame is not None:
                im = RoboCompMultiModalHumanIdentification.TImage()
                im.height,im.width,im.depth = frame.shape

                im.image = frame.tostring()
                recognisedHumans = self.multimodalhumanidentification_proxy.getLabel(im)

                frame = np.ascontiguousarray(frame) # Make compatile to preprocessing

                for i in range(recognisedHumans.numhumans):
                    bbox = recognisedHumans.boundingboxes[i]

                    # Get color information 
                    txt = recognisedHumans.labellist[i]
                    if txt not in self.label2color: 
                        self.label2color[txt] = self._get_rand_color()
                    thickness = 2

                    # Draw bounding box
                    cv2.rectangle(frame,(bbox[0],bbox[1]),(bbox[2],bbox[3]),self.label2color[txt],thickness)        

                    # Put text
                    fontsize = 0.8
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    cat_size = cv2.getTextSize(txt, font, fontsize, thickness)[0]

                    cv2.rectangle(frame,
                                  (bbox[0], bbox[1] - cat_size[1] - thickness),
                                  (bbox[0] + cat_size[0], bbox[1]), self.label2color[txt]+[0.1], -1)
                    cv2.putText(frame, txt, (bbox[0], bbox[1] - thickness - 1), 
                                font, fontsize, (0, 0, 0), thickness=1, lineType=cv2.LINE_AA)

                    # Highlight is mouse present
                    if self.gui.intersect(bbox):
                        # Create highlight region
                        highlight = frame[ bbox[1]:bbox[3], bbox[0]:bbox[2],:]
                        # highlight = cv2.addWeighted(highlight, 0.5, np.full_like(highlight,255), 0.5, 1.0)

                        # Update image
                        frame[ bbox[1]:bbox[3], bbox[0]:bbox[2],:] = highlight

                        # If person double clicks
                        if self.gui.open_popup:
                            self.gui.open_popup = False 
                            self.setPeriod(10000) # Wait for 10 seconds for every update when bbox is on
                            try:
                                if "unknown" in txt:
                                    name = self.gui.get_user_input()
                                    status = self.multimodalhumanidentification_proxy.addLabel(txt, name)
                                    self.gui.ok_button(f"Successfully added {name} to database!" if status == 1 else f"Unable to add {name}")

                                else:
                                    status = self.multimodalhumanidentification_proxy.deleteLabel(txt)
                                    self.gui.ok_button(f"Successfully deleted {txt} from database!" if status == 1 else f"Unable to delete {txt}")                                
                            except Exception as e:
                                traceback.print_exc()

                            self.setPeriod(50)

                cv2.namedWindow('Human MultiModal Re-Identification', cv2.WND_PROP_FULLSCREEN)
                cv2.setWindowProperty('Human MultiModal Re-Identification',cv2.WND_PROP_FULLSCREEN,cv2.WINDOW_FULLSCREEN)
                cv2.imshow('Human MultiModal Re-Identification',frame)
                cv2.setMouseCallback('Human MultiModal Re-Identification',self.gui.update_mouse_location) # Need to find the location of 

            else:
                print("Video Completed Closing")

        except Ice.Exception as e:
          traceback.print_exc()
          print(e)

        cv2.waitKey(1) # Wait key required by cv2.imshow
        return True

    def startup_check(self):
        QTimer.singleShot(200, QApplication.instance().quit)


    ######################
    # From the RoboCompCameraSimple you can call this methods:
    # self.camerasimple_proxy.getImage(...)

    ######################
    # From the RoboCompCameraSimple you can use this types:
    # RoboCompCameraSimple.TImage

    ######################
    # From the RoboCompMultiModalHumanIdentification you can call this methods:
    # self.multimodalhumanidentification_proxy.addLabel(...)
    # self.multimodalhumanidentification_proxy.deleteLabel(...)
    # self.multimodalhumanidentification_proxy.getLabel(...)

    ######################
    # From the RoboCompMultiModalHumanIdentification you can use this types:
    # RoboCompMultiModalHumanIdentification.TImage


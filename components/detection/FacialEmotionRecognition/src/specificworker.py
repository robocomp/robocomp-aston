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
#

from PySide2.QtCore import QTimer
from PySide2.QtWidgets import QApplication


import sys, os, traceback, time, glob
import numpy as np
import cv2
import face_recognition
import time

from genericworker import *
sys.path.append(os.path.join(os.getcwd(),"assets"))
import face_detection

class SpecificWorker(GenericWorker):
    def __init__(self, proxy_map, startup_check=False):
        super(SpecificWorker, self).__init__(proxy_map)
        self.Period = 50
        if startup_check:
            self.startup_check()
        else:
            self.timer.timeout.connect(self.compute)
            self.timer.start(self.Period)
        self.bb_color = [0,0,255]   
        self.bb_thickness = 3
        self.text_color = (255,255,255)
        self.fps_text_color = (0,0,0)

        # Select face_detection = 1 for dlib and 2 for RetinaNetMobile
        self.face_detection = 2
        if (self.face_detection == 2):
            self.detector = face_detection.build_detector("RetinaNetMobileNetV1", max_resolution=1080)



    def __del__(self):
        print('SpecificWorker destructor')

    def setParams(self, params):
        return True


    @QtCore.Slot()
    def compute(self):
        print('SpecificWorker.compute...')
        try:
            self.start_time = time.time()
            data = self.camerasimple_proxy.getImage()
            arr = np.fromstring(data.image, np.uint8)
            frame = np.reshape(arr, (data.height, data.width, data.depth))

            # Perform face detection using dlib model
            if (self.face_detection == 1):
                locations = face_recognition.face_locations(frame, model='cnn')
                for i in range(len(locations)):
                    face_location = locations[i]
                    cv2.rectangle(frame, (face_location[3], face_location[0]), (face_location[1], face_location[2]), self.bb_color, self.bb_thickness)
                    faceImg = frame[face_location[0]:face_location[2],face_location[3]:face_location[1],:]
                    # Run inference of the face image and get the label
                    emotionlabel = "UNKNOWN"
                    cv2.putText(frame, emotionlabel, (face_location[3], face_location[0]-2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.text_color, 1 , cv2.LINE_AA)

            # Perform face detection using RetinaNetMobile
            elif (self.face_detection == 2):
                locations = self.detector.detect(frame[:, :, ::-1])[:, :4]
                for bbox in locations:
                    x0, y0, x1, y1 = [int(_) for _ in bbox]
                    cv2.rectangle(frame, (x0, y0), (x1, y1), self.bb_color, self.bb_thickness)
                    faceImg = frame[y0:y1,x0:x1,:]
                    emotionlabel = "UNKNOWN"
                    cv2.putText(frame, emotionlabel, (x0, y0-2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.text_color, 1 , cv2.LINE_AA)

            # Calculating and showing FPS
            fps = 1.0 / (time.time() - self.start_time)
            print_text = "FPS : " + str(int(fps))
            cv2.putText(frame, print_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.fps_text_color, 2)

            cv2.imshow('Output', frame)

        except Exception as e:
            print (e)
        return True

    def startup_check(self):
        QTimer.singleShot(200, QApplication.instance().quit)


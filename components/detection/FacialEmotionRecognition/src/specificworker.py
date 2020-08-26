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
import matplotlib.pyplot as plt

import face_recognition
import time
import atexit

from genericworker import *
sys.path.append(os.path.join(os.getcwd(),"assets"))
import face_detection
sys.path.append(os.path.join(os.getcwd(),"model"))
import visualize

class SpecificWorker(GenericWorker):
	def __init__(self, proxy_map):
		super(SpecificWorker, self).__init__(proxy_map)
		self.timer.timeout.connect(self.compute)
		self.Period = 50
		self.timer.start(self.Period)
		self.bb_color = [0,0,255]   
		self.bb_thickness = 3
		self.text_color = (255,255,255)
		self.fps_text_color = (0,0,0)
		self.class_names = ['Angry', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
		self.frame_count = np.zeros((6))

		# Select face_detection = 1 for dlib and 2 for RetinaNetMobile
		self.face_detection_method = 2
		if (self.face_detection_method == 2):
			self.detector = face_detection.build_detector("RetinaNetMobileNetV1", max_resolution=1080)

		self.fig = plt.gcf()
		self.fig.show()
		self.fig.canvas.draw()

	def __del__(self):
		print('Final Report')
		for idx, class_name in enumerate(self.class_names):
			print (class_name + ' = ' + "{:.3f}".format(self.frame_count[idx]/np.sum(self.frame_count)))
		print ("Most prevalent emotion during the interaction was : " + self.class_names[np.argmax(self.frame_count)])

	def setParams(self, params):
		return True


	@QtCore.Slot()
	def compute(self):
		print('SpecificWorker.compute...')
		try:
			self.start_time = time.time()
			data = self.camerasimple_proxy.getImage()
			arr = np.fromstring(data.image, np.uint8)
			self.frame = np.reshape(arr, (data.height, data.width, data.depth))

			self.bb = []
			self.probability_vector = []

			# Perform face detection using dlib model
			if (self.face_detection_method == 1):
				locations = face_recognition.face_locations(self.frame, model='cnn')
				for i in range(len(locations)):
					face_location = locations[i]
					y0, x1, y1, x0 = [int(_) for _ in face_location]
					self.bb.append([x0,y0,x1,y1])

			# Perform face detection using RetinaNetMobile
			elif (self.face_detection_method == 2):
				locations = self.detector.detect(self.frame[:, :, ::-1])[:, :4]
				for bbox in locations:
					x0, y0, x1, y1 = [int(_) for _ in bbox]
					self.bb.append([x0,y0,x1,y1])

			for idx in range(len(self.bb)):
				x0, y0, x1, y1 = [int(_) for _ in self.bb[idx]]
				cv2.rectangle(self.frame, (x0, y0), (x1, y1), self.bb_color, self.bb_thickness)
				faceImg = self.frame[y0:y1,x0:x1,:]
				faceImgGray = cv2.cvtColor(faceImg, cv2.COLOR_BGR2GRAY)
				faceImgGray = cv2.resize(faceImgGray, (48, 48))
				prob_vector = visualize.predict_emotion(faceImgGray)
				self.probability_vector.append(prob_vector)
				emotionlabel = self.class_names[np.argmax(prob_vector)]
				self.frame_count[np.argmax(prob_vector)] += 1
				cv2.putText(self.frame, emotionlabel, (x0, y0-2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.text_color, 1 , cv2.LINE_AA)
				self.plot_emotion_graph()

			# Calculating and showing FPS
			fps = 1.0 / (time.time() - self.start_time)
			print_text = "FPS : " + str(int(fps))
			cv2.putText(self.frame, print_text, (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.fps_text_color, 2)
			cv2.imshow('Output', self.frame)
			self.FacialEmotionRecognition_getEmotionList()

		except Exception as e:
			print (e)
		return True


	def plot_emotion_graph(self):		
		self.fig.clear()
		plt.barh(self.class_names, (self.frame_count/np.sum(self.frame_count)))
		self.fig.set_facecolor((216/255, 230/255, 242/255))
		plt.title("Probable emotion during the interaction",  fontdict = {'fontsize' : 10})
		plt.xlabel('Proabability(P) [0 <= P <= 1]')
		plt.xlim(0, 1)
		plt.grid(color='w', linestyle='-', linewidth=2)
		plt.grid(True)
		plt.grid(color='w', linestyle='-', linewidth=2)
		plt.yticks(fontsize = 10)
		self.fig.canvas.draw()

	# =============== Methods for Component Implements ==================
	# ===================================================================

	#
	# getEmotionList
	#
	def FacialEmotionRecognition_getEmotionList(self):
		EmotionList = []
		for idx in range(len(self.bb)):
			x0, y0, x1, y1 = [int(_) for _ in self.bb[idx]]
			faceImg = self.frame[y0:y1,x0:x1,:]
			im = TImage()
			im.image = faceImg
			im.height, im.width, im.depth = faceImg.shape
			person_data = SEmotion()
			person_data.FaceImage = im
			person_data.EmotionVector = self.probability_vector[idx]
			person_data.x = x0
			person_data.y = y0
			person_data.w = x1 - x0
			person_data.h = y1 - y0
			EmotionList.append(person_data)
		return EmotionList

	# ===================================================================
	# ===================================================================



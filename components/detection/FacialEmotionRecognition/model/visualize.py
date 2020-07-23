import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
import os
from torch.autograd import Variable

import transforms as transforms
import torchvision.models as models
import cv2
import warnings
warnings.filterwarnings("ignore", category=UserWarning) 

cut_size = 44

transform_test = transforms.Compose([
    transforms.TenCrop(cut_size),
    transforms.Lambda(lambda crops: torch.stack([transforms.ToTensor()(crop) for crop in crops])),
])
class_names = ['Angry', 'Fear', 'Happy', 'Sad', 'Surprise', 'Neutral']
net = models.vgg19()
checkpoint = torch.load(os.path.join('model','weights', 'PrivateTest_model.t7'))
net.load_state_dict(checkpoint['net'])
net.eval()


def predict_emotion(img):

	img = img[:, :, np.newaxis]

	img = np.concatenate((img, img, img), axis=2)
	img = Image.fromarray(img)
	inputs = transform_test(img)

	ncrops, c, h, w = np.shape(inputs)
	inputs = inputs.view(-1, c, h, w)
	inputs = Variable(inputs)
	outputs = net(inputs)
	outputs_avg = outputs.view(ncrops, -1).mean(0)  # avg over crops
	score = F.softmax(outputs_avg)
	_, predicted = torch.max(outputs_avg.data, 0)
	emotion_label = class_names[int(predicted.cpu().numpy())]
	return emotion_label

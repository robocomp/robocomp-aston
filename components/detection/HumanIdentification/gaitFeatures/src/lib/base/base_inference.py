#------------------------------------------------------------------------------
#   Libraries
#------------------------------------------------------------------------------
import cv2, torch
import numpy as np
from time import time
from torch.nn import functional as F


#------------------------------------------------------------------------------
#   BaseInference
#------------------------------------------------------------------------------
class BaseInference(object):
	def __init__(self, model, color_f=[255,0,0], color_b=[0,0,255], kernel_sz=25, sigma=0, background_path=None):
		self.model = model
		self.color_f = color_f
		self.color_b = color_b
		self.kernel_sz = kernel_sz
		self.sigma = sigma
		self.background_path = background_path
		if background_path is not None:
			self.background = cv2.imread(background_path)[...,::-1]
			self.background = self.background.astype(np.float32)


	def load_image(self):
		raise NotImplementedError


	def preprocess(self, image, *args):
		raise NotImplementedError


	def predict(self, X):
		raise NotImplementedError


	def draw_matting(self, image, mask):
		"""
		image (np.uint8) shape (H,W,3)
		mask  (np.float32) range from 0 to 1, shape (H,W)
		"""
		mask = 255*(1.0-mask)
		mask = np.expand_dims(mask, axis=2)
		mask = np.tile(mask, (1,1,3))
		mask = mask.astype(np.uint8)
		image_alpha = cv2.add(image, mask)
		return image_alpha


	def draw_transperency(self, image, mask):
		"""
		image (np.uint8) shape (H,W,3)
		mask  (np.float32) range from 0 to 1, shape (H,W)
		"""
		mask = mask.round()
		alpha = np.zeros_like(image, dtype=np.uint8)
		alpha[mask==1, :] = self.color_f
		alpha[mask==0, :] = self.color_b
		image_alpha = cv2.add(image, alpha)
		return image_alpha


	def draw_background(self, image, mask):
		"""
		image (np.uint8) shape (H,W,3)
		mask  (np.float32) range from 0 to 1, shape (H,W)
		"""
		image = image.astype(np.float32)
		mask_filtered = cv2.GaussianBlur(mask, (self.kernel_sz, self.kernel_sz), self.sigma)
		mask_filtered = np.expand_dims(mask_filtered, axis=2)
		mask_filtered = np.tile(mask_filtered, (1,1,3))

		image_alpha = image*mask_filtered + self.background*(1-mask_filtered)
		return image_alpha.astype(np.uint8)

#------------------------------------------------------------------------------
#   ImageListInference
#------------------------------------------------------------------------------
class ImageListInference():
	def __init__(self, model, opts):
		# Initialize
		super(ImageListInference, self).__init__()

		self.model = model
		if opts.gpu != -1:
			self.model.cuda()
		self.model.eval()

		self.color_f=[255,0,0]
		self.color_b=[0,0,255]
		self.kernel_sz=25
		self.sigma = 0 

		self.input_size = 320
		self.T_H = 64 # Height of the  
		self.T_W = 64 # Height of the  

		self.use_cuda = opts.gpu >= 0

		# Preprocess
		self.mean = np.array([0.485,0.456,0.406])[None,None,None,:]
		self.std = np.array([0.229,0.224,0.225])[None,None,None,:]

	def preprocess(self, imagelist):
		image = np.array([cv2.resize(image, (self.input_size,self.input_size), interpolation=cv2.INTER_LINEAR) for image in imagelist ])
		image = image.astype(np.float32) / 255.0
		image = (image - self.mean) / self.std
		X = np.transpose(image, axes=(0,3, 1, 2))
		X = torch.tensor(X, dtype=torch.float32)
		return X

	def predict(self, X):
		with torch.no_grad():
			if self.use_cuda:
				mask = self.model(X.cuda())
				mask = F.softmax(mask, dim=1)
				mask = mask[:,1,...].cpu().numpy()
			else:
				mask = self.model(X)
				mask = F.softmax(mask, dim=1)
				mask = mask[:,1,...].numpy()
			return mask

	def post_process(self,img):
		"""
			Post process and create 64x64 image for gatiset
		"""
		img = img.astype(np.float32)
		y = img.sum(axis=1)	
		y_top = (y != 0).argmax(axis=0)
		y_btm = (y != 0).cumsum(axis=0).argmax(axis=0)
		img = img[y_top:y_btm + 1, :]
		# As the height of a person is larger than the width,
		# use the height to calculate resize ratio.
		_r = img.shape[1] / img.shape[0]
		_t_w = int(self.T_H * _r)
		img = cv2.resize(img, (_t_w, self.T_H), interpolation=cv2.INTER_CUBIC)
		# Get the median of x axis and regard it as the x center of the person.
		sum_point = img.sum()
		sum_column = img.sum(axis=0).cumsum()
		x_center = -1
		for i in range(sum_column.size):
			if sum_column[i] > sum_point / 2:
				x_center = i
				break

		h_T_W = int(self.T_W / 2)
		left = x_center - h_T_W
		right = x_center + h_T_W
		if left <= 0 or right >= img.shape[1]:
			left += h_T_W
			right += h_T_W
			_ = np.zeros((img.shape[0], h_T_W))
			img = np.concatenate([_, img, _], axis=1)
		img = img[:, left:right]
		return img.astype('uint8')




	def run(self,imagelist):
		# Preprocess
		X = self.preprocess(imagelist)
		# Predict
		mask = self.predict(X)
		masklist = [self.post_process(m > 0.5) for m in mask] # Need to change the threshold
		return masklist
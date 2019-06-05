from PIL import Image
from PIL import ImageFilter
import copy
import numpy as np

class Filter(object):

	GaussianH = np.array([[0.003, 0.013, 0.022, 0.013, 0.003],
				[0.013, 0.059, 0.097, 0.059, 0.013],
			    [0.022, 0.097, 0.159, 0.097, 0.022],
				[0.013, 0.059, 0.097, 0.059, 0.013],
				[0.003, 0.013, 0.022, 0.013, 0.003]])

	SobelX = np.array([[-1, 0, 1],
					   [-2, 0, 2],
					   [-1, 0, 1]]) / 8

	SobelY = np.array([[1, 2, 1],
					   [0, 0, 0],
					   [-1, -2, -1]]) / 8



	def __init__(self):
		pass


	def apply_filter_pixel(self, image, H, i, j):
		n, m = H.shape
		res = 0.0
		for x in range(n):
			for y in range(m):
				res += H[x, y] * image[i+x-int(n/2), j+y-int(m/2)]
		return int(res)


	def gaussian_filter(self, image):
		H = np.zeros(image.shape)
		G = self.GaussianH
		H[:G.shape[0], :G.shape[1]] = G

		F_fft = np.fft.fft2(image)
		H_fft = np.fft.fft2(H)
		return np.abs(np.fft.ifft2(F_fft * H_fft)).astype(int) 	# fourier transformation speed up


	def sobel_filter(self, image):
		Hx = np.zeros(image.shape)
		Hy = np.zeros(image.shape)
		G1 = self.SobelX
		G2 = self.SobelY
		Hx[:G1.shape[0], :G1.shape[1]] = G1
		Hy[:G2.shape[0], :G2.shape[1]] = G2

		Sx = np.abs(np.fft.ifft2(np.fft.fft2(image) * np.fft.fft2(Hx))).astype(int)
		Sy = np.abs(np.fft.ifft2(np.fft.fft2(image) * np.fft.fft2(Hy))).astype(int)
		return (Sx, Sy)





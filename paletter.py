from sklearn.cluster import MiniBatchKMeans
import matplotlib.pyplot as plt
import argparse
import utils
import numpy as np
import cv2

class IClusteringService:
	def fit(self, data, n_clusters): pass
	def get_histogram(self, clusters, weighted: bool, height: int, width: int): pass

class IImageService:
	def get_pixels_list(self, image_path: str): pass
	def save(self, image, dpi: int, path: str): pass

class MatplotlibImageService(IImageService):
	def get_pixels_list(self, image_path: str):
		image = cv2.imread(image_path)
		image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
		image = image.reshape((image.shape[0] * image.shape[1], 3))
		return image

	def save(self, image_array, dpi: int, path: str):
		plt.figure()
		plt.axis("off")
		plt.imshow(image_array)
		plt.savefig(path, dpi=dpi, bbox_inches='tight', pad_inches = 0)


class ScikitClusteringService(IClusteringService):
	def fit(self, data, n_clusters): 
		clusters = MiniBatchKMeans(n_clusters = n_clusters)
		clusters.fit(data)
		return clusters 

	def get_histogram(self, clusters, weighted: bool, height: int, width: int):
		num_labels = np.arange(0, len(np.unique(clusters.labels_)) + 1)
		hist, _ = np.histogram(clusters.labels_, bins = num_labels)
		hist = hist.astype("float")
		hist /= hist.sum()

		if not weighted:
			return self.__plot_uniform_bars(hist, clusters.cluster_centers_, width, height)

		return self.__plot_weighted_bars(hist, clusters.cluster_centers_, width, height)

	def __plot_uniform_bars(self, hist, centroids, width, height):
		bar = np.zeros((height, width, 3), dtype = "uint8")
		start_x = 0
		num_labels = len(centroids) 
		bar_width = width / num_labels

		for (percent, color) in zip(hist, centroids):
			end_x = start_x + bar_width
			cv2.rectangle(bar, (int(start_x), 0), (int(end_x), height), color.astype("uint8").tolist(), -1)
			start_x = end_x

		return bar

	def __plot_weighted_bars(self, hist, centroids, width, height):
		bar = np.zeros((height, width, 3), dtype = "uint8")
		start_x = 0

		for (percent, color) in zip(hist, centroids):
			end_x = start_x + (percent * width)
			cv2.rectangle(bar, (int(start_x), 0), (int(end_x), height), color.astype("uint8").tolist(), -1)
			start_x = end_x

		return bar

class PaletteService:
	def __init__(self, clustering_service: IClusteringService, image_service: IImageService):
		self.clustering_service = clustering_service
		self.image_service = image_service
		# telegram APIs allow for a limited combination of h x w x dpi as a final output
	
	def generate(self, input_path: str, output_path: str, width=300, height=300, dpi=1200, colors=5, weighted_palette=False):
		pixels = self.image_service.get_pixels_list(input_path)

		clusters = self.clustering_service.fit(pixels, colors)
		histogram = self.clustering_service.get_histogram(clusters, weighted_palette, height, width)

		self.image_service.save(histogram, dpi, output_path)
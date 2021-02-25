from sklearn.cluster import MiniBatchKMeans
import matplotlib.pyplot as plt
import argparse
import utils
import cv2

def extract_palette(image_path: str, n_clusters: int):
	image = cv2.imread(image_path)
	image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
	image = image.reshape((image.shape[0] * image.shape[1], 3)) # reshape as list of pixels [[R,G,B], ...]

	# use K-Means to extract color palettes from picture
	clusters = MiniBatchKMeans(n_clusters = n_clusters)
	clusters.fit(image) 

	return clusters


def export_palette_to_image(clusters, image_path: str, width: int, height: int, dpi: int) -> str:
	# initialize and color a histogram. each centroid colors one bar of the histogram
	centroid_histogram = utils.centroid_histogram(clusters) 
	palette = utils.plot_colors(centroid_histogram, clusters.cluster_centers_, width, height)

	output_filename = str(image_path) + "_processed.png"

	plt.figure()
	plt.axis("off")
	plt.imshow(palette)
	plt.savefig(output_filename, dpi=dpi, bbox_inches='tight', pad_inches = 0)
	
	return output_filename


def generate_palette_from_image(image_path: str, expected_colors: int, width: int, height: int, dpi: int) -> str:
	clusters = extract_palette(image_path, expected_colors)
	return export_palette_to_image(clusters, image_path, width, height, dpi)

if __name__ == "__main__":
	ap = argparse.ArgumentParser()
	ap.add_argument("-i", "--image", required = True, help = "Path to the image")
	ap.add_argument("-c", "--clusters", required = True, type = int,
		help = "# of clusters")
	args = vars(ap.parse_args())

	generate_palette_from_image(args["image"], args["clusters"], 300, 300, 1200)
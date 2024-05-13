import sys, random, argparse, requests
import numpy as np
import math
from PIL import Image


def fetch_xapp_token(client_id, client_secret, api_url):
    try:
        response = requests.post(api_url+'tokens/xapp_token', json={"client_id": client_id, "client_secret": client_secret})
        if response.status_code == 200:
            xapp_token = response.json().get("token")
            echo("Fetched xapp token:", xapp_token)
            return xapp_token
        else:
            print("Failed to fetch xapp token. Status code:", response.status_code)
            return None
    except Exception as e:
        print("An error occurred:", str(e))
        return None



def get_random_artwork(xapp_token, api_url):
    try:
        url = api_url+'artworks?offset='+str(random.randint(0, 10000))+'&size=1&page=1'
        response = requests.get(url, headers={"X-Api-Key": xapp_token})
        if response.status_code == 200:
            artwork = response.json()
            echo("Fetched artwork:", artwork)
            return artwork
        else:
            echo("Failed to fetch artwork. Status code:", response.status_code)
            return None
    except Exception as e:
        print("An error occurred:", str(e))
        return None






# Python code to convert an image to ASCII image.

# gray scale level values from:
# http://paulbourke.net/dataformats/asciiart/

# 70 levels of gray
gscale1 = "$@B%8&WM#*oahkbdpqwmZO0QLCJUYXzcvunxrjft/\|()1{}[]?-_+~<>i!lI;:,\"^`'. "

# 10 levels of gray
gscale2 = '@%#*+=-:. '

def getAverageL(image):

	"""
	Given PIL Image, return average value of grayscale value
	"""
	# get image as numpy array
	im = np.array(image)

	# get shape
	w,h = im.shape

	# get average
	return np.average(im.reshape(w*h))

def covertImageToAscii(fileName, cols, scale, moreLevels):
	"""
	Given Image and dims (rows, cols) returns an m*n list of Images
	"""
	# declare globals
	global gscale1, gscale2

	# open image and convert to grayscale
	image = Image.open(fileName).convert('L')

	# store dimensions
	W, H = image.size[0], image.size[1]
	print("input image dims: %d x %d" % (W, H))

	# compute width of tile
	w = W/cols

	# compute tile height based on aspect ratio and scale
	h = w/scale

	# compute number of rows
	rows = int(H/h)

	print("cols: %d, rows: %d" % (cols, rows))
	print("tile dims: %d x %d" % (w, h))

	# check if image size is too small
	if cols > W or rows > H:
		print("Image too small for specified cols!")
		exit(0)

	# ascii image is a list of character strings
	aimg = []
	# generate list of dimensions
	for j in range(rows):
		y1 = int(j*h)
		y2 = int((j+1)*h)

		# correct last tile
		if j == rows-1:
			y2 = H

		# append an empty string
		aimg.append("")

		for i in range(cols):

			# crop image to tile
			x1 = int(i*w)
			x2 = int((i+1)*w)

			# correct last tile
			if i == cols-1:
				x2 = W

			# crop image to extract tile
			img = image.crop((x1, y1, x2, y2))

			# get average luminance
			avg = int(getAverageL(img))

			# look up ascii char
			if moreLevels:
				gsval = gscale1[int((avg*69)/255)]
			else:
				gsval = gscale2[int((avg*9)/255)]

			# append ascii char to string
			aimg[j] += gsval

	# return txt image
	return aimg

# main() function
def main():
	# create parser
	descStr = "This program converts an image into ASCII art."
	parser = argparse.ArgumentParser(description=descStr)
	# add expected arguments
	parser.add_argument('--file', dest='imgFile', required=True)
	parser.add_argument('--scale', dest='scale', required=False)
	parser.add_argument('--out', dest='outFile', required=False)
	parser.add_argument('--cols', dest='cols', required=False)
	parser.add_argument('--morelevels',dest='moreLevels',action='store_true')

	# parse args
	args = parser.parse_args()

	imgFile = args.imgFile

	# set output file
	outFile = 'out.txt'
	if args.outFile:
		outFile = args.outFile

	# set scale default as 0.43 which suits
	# a Courier font
	scale = 0.43
	if args.scale:
		scale = float(args.scale)

	# set cols
	cols = 80
	if args.cols:
		cols = int(args.cols)

	print('generating ASCII art...')
	# convert image to ascii txt
	aimg = covertImageToAscii(imgFile, cols, scale, args.moreLevels)

	# open file
	f = open(outFile, 'w')

	# write to file
	for row in aimg:
		f.write(row + '\n')

	# cleanup
	f.close()
	print("ASCII art written to %s" % outFile)

# call main
if __name__ == '__main__':
	main()


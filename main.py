#!/usr/bin/python3
from sentinelsat.sentinel import SentinelAPI
import requests
from lxml import etree
from datetime import datetime
from joblib import Parallel, delayed
import os
import csv
import cv2

# check params.py to choose the following request parameters
from params import tiles, begin_date, end_date, max_cloud_coverage, resolution, scale_percent, user, password, api_mirror, download_last, parallel_jobs

# those will contain list of image links and list of image already processed (allows for multithreading in particular)
imgLinks = []
imgOutputs = []

# initialise API (to get list of shots and links) and requests session (to download image directly from link)
api = SentinelAPI(user, password, api_mirror)
session = requests.Session()
session.auth = (user, password)

# this populates imgLinks with the link to the tile image
def getTile(tile):
	# API request
	products = api.query(filename = '*_T{}_*'.format(tile),
		             date = (begin_date, end_date),
		             platformname = 'Sentinel-2',
		             processinglevel = 'Level-2A',
		             cloudcoverpercentage = (0, max_cloud_coverage))

	gdf = api.to_geodataframe(products)
	gdf_sorted = gdf.sort_values(by='ingestiondate', ascending=False)

	# get all orbit numbers on that tile
	# each tile is crossed by 1 orbit (which covers the entire tile) 2 or 3 orbits (which cover only part of the tile)
	# in the second case, we need to make a mosaic of those orbits to get the entire tile
	orbits = [ [], [], [] ]
	numbers = []
	for product in gdf_sorted.itertuples():
		if (product.relativeorbitnumber not in numbers):
			numbers.append(product.relativeorbitnumber)
	
	# order all shots by orbit number
	for product in gdf_sorted.itertuples():
		for i in range(len(numbers)):
			if numbers[i] == product.relativeorbitnumber:
				orbits[i].append(product)
	
	# show list of shots for user to choose
	for relativeorbits in orbits:
		if len(relativeorbits) > 0:
			print("\nTile " + tile + " - Orbit " +str(relativeorbits[0].relativeorbitnumber) + "\n")
		i = 0
		for product in relativeorbits:
			print(str(i) + " - " + str(product.ingestiondate).split(" ")[0] + " - " + str(int(product.cloudcoverpercentage)) + "% cloud")
			i += 1
	
	# ask user to select shot for all orbits for this tile
	# if download_last is True, always select the first shot in the list	
	allselected = []
	if download_last:
		allselected.append(0)
		if len(numbers) == 2:
			allselected.append(0)
		elif len(numbers) == 3:
			allselected.append(0)
			allselected.append(0)
	else:
		allselected.append(int(input("\nSelected version for tile " + tile +" - Orbit " + str(numbers[0]) + ": ")))
		if len(numbers) == 2:
			allselected.append(int(input("Selected version for tile " + tile +" - Orbit " + str(numbers[1]) + ": ")))
		elif len(numbers) == 3:
			allselected.append(int(input("Selected version for tile " + tile +" - Orbit " + str(numbers[1]) + ": ")))
			allselected.append(int(input("Selected version for tile " + tile +" - Orbit " + str(numbers[2]) + ": ")))
	
	# fetch image link
	i=0
	for selected in allselected:
		# record tile coordinates when fetched and write it down
		# (keeps the previously fetched coordinates just in case)
		tile_coordinates = orbits[i][selected].geometry.bounds
		with open("tilesCoordinates.csv", "a") as f:
			writer = csv.writer(f)
			writer.writerow((tile + "_" + str(orbits[i][selected].relativeorbitnumber),) + tile_coordinates)
		
		# get product link and look for the link to the TCI image at the right resolution
		# (a product contains lots of images that are not needed here)
		link_with_value = orbits[i][selected].link
		link = link_with_value[:link_with_value.rfind("/")]
		filename = orbits[i][selected].filename

		granules_url = link + "/Nodes('" + filename + "')/Nodes('GRANULE')/Nodes"

		with session.get(granules_url) as r:
			r.raise_for_status()
			granules_xml = r.text.encode('utf-8')

		tree = etree.fromstring(granules_xml)
		entries = tree.findall('.//{*}entry')
		for e in entries:
			granule = e.find(".//{*}link[@title='Node']")
			gnode = granule.attrib['href']

			imgdata_url = granules_url[:granules_url.rfind("/")] + "/" + gnode + "/Nodes('IMG_DATA')/Nodes('R" + str(resolution) + "m')/Nodes"

			with session.get(imgdata_url) as r:
			    r.raise_for_status()
			    imgdata_xml = r.text.encode('utf-8')

			tree = etree.fromstring(imgdata_xml)
			links = tree.findall('.//{*}entry/{*}link[@type="application/octet-stream"]')

			for link in links:
				href = link.attrib['href']
				if '_TCI_' + str(resolution) + 'm.jp2' in href:
					tcinode_value = href
					break

		# once the link is found, append it to the imgLinks array
		imgLinks.append({'tile':tile, 'orbit': orbits[i][selected].relativeorbitnumber, 'url':imgdata_url[:imgdata_url.rfind("/")] + "/" + tcinode_value})
		i += 1
		
# multi-threaded calls to explore function
Parallel(n_jobs=parallel_jobs,require='sharedmem')(delayed(getTile)(tile) for tile in tiles)

# once imgLinks array is populated, ask user to download
input("\nDownload " + str(len(imgLinks)) + " images ?\n")

# create a new directory in the output folder
date = str(datetime.now()).split(".")[0]
path = "output/" + str(resolution) + "m/" + date
os.mkdir(path)

# download images
for link in imgLinks:
	print(link['tile'] + " orbit " + str(link['orbit']))
	with session.get(link['url']) as r:
		# Save image
		filename = path + "/" + link['tile'] + "_" + str(link['orbit'])
		f = open(filename + ".jp2", 'wb+')
		f.write(r.content)
		f.close()
		
		# Resize image, make black zone (exists if 2 orbits cross the same tile) transparent (to create the mosaic) and convert to png
		# Sometimes sentinel images raise errors when read with cv2, not sure why, but rare, just use try
		try:
			image = cv2.imread(filename + ".jp2")
		
			# resize according to scale_percent
			# no need to resize 10 and 20 resolution as we can just use 60 in that case
			if resolution == 60:
				width = int(image.shape[1] * scale_percent / 100)
				height = int(image.shape[0] * scale_percent / 100)
				dim = (width, height)
				image = cv2.resize(image, dim, interpolation = cv2.INTER_AREA)
				
			# make black zone transparent
			tmp = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
			_,alpha = cv2.threshold(tmp,0,255,cv2.THRESH_BINARY)
			b, g, r = cv2.split(image)
			rgba = [b,g,r, alpha]
			image = cv2.merge(rgba,4)
		
			# save as png
			cv2.imwrite(filename + ".png", image)
			os.remove(filename + ".jp2")
		except:
			print("Error : " + link['tile'] + "_" + str(link['orbit']) + " not created")

		# if other orbit on same tile exists, make a mosaic
		for imgOutput in imgOutputs:
			if imgOutput.split("_")[0] == filename.split("_")[0]:
				background = cv2.imread(filename + ".png", cv2.IMREAD_UNCHANGED)
				foreground = cv2.imread(imgOutput + ".png", cv2.IMREAD_UNCHANGED)

				# put one on top of the other
				alpha_background = background[:,:,3] / 255.0
				alpha_foreground = foreground[:,:,3] / 255.0

				for color in range(0, 3):
				    background[:,:,color] = alpha_foreground * foreground[:,:,color] + \
					alpha_background * background[:,:,color] * (1 - alpha_foreground)

				background[:,:,3] = (1 - (1 - alpha_foreground) * (1 - alpha_background)) * 255

				# save as png a mosaic of both files
				# filename becomes filename + imgOutput
				cv2.imwrite(filename + ".png", background)
				os.remove(imgOutput + ".png")
				imgOutputs.remove(imgOutput)
				
		imgOutputs.append(filename)

# convert all png to jpg
for file in os.listdir(path):
	filename = os.fsdecode(file)
	if filename.endswith(".png"): 
		image = cv2.imread(path + "/" + filename)
		cv2.imwrite(path + "/" + filename.split("_")[0] + ".jpg", image)	 
		os.remove(path + "/" + filename)    


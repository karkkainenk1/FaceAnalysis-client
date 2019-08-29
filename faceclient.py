import argparse
import aiohttp
import asyncio
import os
import csv


async def main():
	parser = argparse.ArgumentParser(description='Analyze face images')
	parser.add_argument('input', metavar='inputfile', help='Name of the input file. A text file where each row should contain a path to an input image.')
	parser.add_argument('output', metavar='outputfile', help='Name of the output file.')
	args = parser.parse_args()

	input_file = args.input
	output_file = args.output

	if not os.path.exists(input_file):
		raise RuntimeError("Input file does not exist")

	if os.path.exists(output_file):
		raise RuntimeError("Output file already exists")

	input_images = get_input_images(input_file)

	response_rows = []
	for image in input_images:
		response = await send_request(image)
		response_rows += format_output(image, response)
	
	write_results(output_file, response_rows)


def get_input_images(input_file):
	with open(input_file, 'r') as f:
		contents = f.read()
		rows = [row for row in contents.split('\n') if row != ""]
	
	for image_file in rows:
		if not is_valid_file(image_file):
			raise RuntimeError("File path not valid: {}".format(image_file))

	return rows


def is_valid_file(image_file):
	# TODO: Verify that the file is an image
	return os.path.exists(image_file)


async def send_request(image_path):
	url = 'http://localhost/faces'
	data = {'image': open(image_path, 'rb')}
	async with aiohttp.ClientSession() as session:
		async with session.post(url, data=data) as resp:
			if resp.status != 200:
				raise RuntimeError("Server error")
			return await resp.json()


def format_output(image_path, response):
	return [generate_face_row(image_path, face) for face in response["faces"]]


def generate_face_row(image_path, face):
	attrs = face["attributes"]
	rect = face["rectangle"]

	return {"image":	image_path, 
			"gender": 	attrs["gender"], 
			"age":		attrs["age"], 
			"race": 	attrs["race"], 
			"left": 	rect["left"],
			"top": 		rect["top"],
			"width": 	rect["width"],
			"height": 	rect["height"]}


def write_results(output_file, response_rows):
	with open(output_file, 'w', newline='') as f:
		writer = csv.DictWriter(f, fieldnames=["image", "gender", "age", "race", "left", "top", "width", "height"])

		writer.writeheader()
		writer.writerows(response_rows)

if __name__ == "__main__":
	asyncio.run(main())

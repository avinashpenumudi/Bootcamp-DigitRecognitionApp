import os
import sys
import shutil
import joblib
import numpy as np
from PIL import Image
from Model.model import predict_value,train_model
from Utility.ImageProcessing import imageToPixel,extract_number
from flask import Flask, jsonify, request, render_template, make_response, Response

app = Flask(__name__)
# Turn ON this path for AWS EC2 Instance - Also make sure you are working with the exact given folder structure otherwise
# change accordingly

# UNCOMMENT WHEN DEPLOYING ON AWS
# basepath = "/var/www/FlaskApplications/SampleApp/api"

# COMMENT WHEN DEPLOYING ON AWS
basepath = "."

app.config['UPLOAD_FOLDER'] = basepath + "/static/"


# Using "POST" method to handle "POST" request sent
# by the client (our android application in this case)
@app.route('/model/predict', methods=['POST'])
def apicall():
	# Basepath - You need to changes this if you are not following the exact same folder structure.
	# basepath = "/var/www/FlaskApplications/SampleApp/api"

	filename = ""

	# Check if the 'test_image' key is present in the files section of the request.
	# If it is that means that the android application (or whatever client sent this post request)
	# has successfully sent an image file (of the sketch of the digit)
	if 'test_image' in request.files:
		# Get that image file and store it in file variable
		file = request.files['test_image']

		# Also save the filename
		filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)

		# Now save this file on EC2 instance storage
		file.save(filename)


	test_image_path = filename

	# Pass the path of this file which you just saved on EC2 Instance to your image processing function extract_number()
	# It will process it and return the a list of file paths (these filepaths are for images of digits extracted from
	# the original image).
	digits = extract_number(test_image_path,app.config['UPLOAD_FOLDER']+filename.split('/')[-1]+"_")

	predictions = []

	for digitPath in digits:
		# Convert the image of digit present on the filepath (digitPath) to pixel values
		test_X = imageToPixel(digitPath).tolist()

		# Recognizing digit using the trained model
		pred_Y = predict_value(test_X)
		predictions.append(pred_Y)

	# Return result as response to the application
	return (jsonify({"prediction":predictions[0][0],"filename":filename}))

if __name__ == "__main__":
	app.run(debug=True, port=5000)

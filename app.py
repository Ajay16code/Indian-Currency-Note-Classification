from flask import Flask, render_template, request, jsonify, send_file
from PIL import Image
# from gtts import gTTS
import os, io, sys
import re
import traceback
import numpy as np
import cv2
import base64
# import time

from yolo_detection import run_model

app = Flask(__name__)


def extract_detected_values(text):
    matches = re.findall(r"(\d+)Rupees", text)
    if not matches:
        return ""
    return ", ".join(matches)


############################################## THE REAL DEAL STARTS HERE ###############################################
@app.route('/detectObject', methods=['POST'])
def mask_image():
    uploaded_file = request.files.get('image')
    if uploaded_file is None or uploaded_file.filename == "":
        return jsonify({
            'status': '',
            'englishmessage': 'No image received. Please choose an image and try again.',
            'detectedtext': ''
        }), 400

    file = uploaded_file.read()
    npimg = np.frombuffer(file, np.uint8)
    decoded = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    if decoded is None:
        return jsonify({
            'status': '',
            'englishmessage': 'Unable to read the image. Please upload a valid image file.',
            'detectedtext': ''
        }), 400

    img = decoded[:, :, ::-1]
    
    ################################################
    # cv2.imshow('After reading from request', img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    ################################################
    ################################################
    ######### Do preprocessing here ################
    # img[img > 150] = 0
    ## any random stuff do here
    ################################################
    try:
        img, text = run_model(img)
    except Exception as err:
        print(traceback.format_exc(), file=sys.stderr)
        error_message = str(err)
        if "No module named 'torchvision'" in error_message:
            message = "Missing dependency: torchvision. Start the app from the project .venv and try again."
        else:
            message = "Detection failed on the server. Please restart the app and try another image."
        return jsonify({
            'status': '',
            'englishmessage': message,
            'detectedtext': ''
        }), 200

    print("{} This is from app.py".format(text))
    if(text.lower() == "image contains"):
        text = ""

    if(len(text) == 0):
        text = "Reload the page and try with another better image"
    
    englishtext = text
    detectedtext = extract_detected_values(text)
    
    # below encodes the detected image as it sent to server back
    """
    rawBytes = io.BytesIO()
    img = Image.fromarray(img.astype("uint8"))
    img.save(rawBytes,"JPEG")
    rawBytes.seek(0)
    img_base64 = base64.b64encode(rawBytes.read())
    return jsonify({'status':str(img_base64)})
    """
    bufferedBytes = io.BytesIO()
    img_base64 = Image.fromarray(img)
    img_base64.save(bufferedBytes, format="JPEG")
    img_base64 = base64.b64encode(bufferedBytes.getvalue())
    # return jsonify({'status':str(img_base64)})
    return jsonify({'status':str(img_base64), 'englishmessage': englishtext, 'detectedtext': detectedtext})

################################## THE MAIN PART IS DONE ABOVE #########################################################


@app.route('/test', methods=['GET', 'POST'])
def test():
	print("log: got at test", file=sys.stderr)
	return jsonify({'status': 'succces'}) 


@app.route('/')
def home():
    return render_template('index.html')

@app.after_request
def after_request(response):
    print("log: setting cors", file=sys.stderr)
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers','Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response


if __name__ == '__main__':
	# app.run(debug=True) 
    # when run using above command change localhost/5000 default port in index.js file
    # In order to work for any device connected to wifi/LAN same network, use below
    app.run(host="0.0.0.0", port=8080, debug=False, threaded=False)
    # make threaded=True for concurrent users
    # ip = "0.0.0.0" matches all ip address, and server listens to all ip address requests
    # below method is for devices connected to Wifi/ LAN
    # using ifconfig/ipconfig cmd in terminal find ip
    # app.run(debug=False, host="xxx.xxx.xxx.xxx",port=8080)
    # change the route path in index.js with http://host_ip:port/

    

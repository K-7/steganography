import os

from flask import Flask, request, redirect, url_for,\
	render_template
from werkzeug import secure_filename
from PIL import Image
import binascii
import optparse

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
	if request.method == 'POST':
		type = request.form['button']

		file = request.files['file']
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

			if type == "Encode":
				message = request.form['message']
				if hide(os.path.join(app.config['UPLOAD_FOLDER'],filename),message):
					link = os.path.join(app.config['UPLOAD_FOLDER'],filename)
					return render_template('result.html',FLAG="SUCCESS",TYPE="Encode",LINK=link)
				else:
					response = "FAILED"
					FAILED_MESSAGE = "Incorrect Image could not hide the text."

			elif type == "Decode":
				return_message = retr(os.path.join(app.config['UPLOAD_FOLDER'],filename))
				if return_message:
					return render_template('result.html',FLAG="SUCCESS",TYPE="Decode",MESSAGE=return_message)
				else:
					response = "FAILED"
					FAILED_MESSAGE = "Incorrect Image could not retrieve the text."
		else:
			response = "FAILED"
			FAILED_MESSAGE = "Failed to upload the Image"
		return render_template('result.html', FLAG=response,FAILED_MESSAGE=FAILED_MESSAGE)
	else:
		return render_template('upload.html')

	

def rgb2hex(r,g,b):
	return '#{:02x}{:02x}{:02x}'.format(r,g,b)

def hex2rgb(hexcode):
	return tuple(map(ord, hexcode[1:].decode("hex")))

# ======================================================================
def num2bin(digit):
	return int(bin(digit)[2:])

def bin2num(binary):
	return int(binary, 2)


def str2bin(message):
	binary = bin(int(binascii.hexlify(message),16))
	return binary[2:]

def bin2str(binary):
	message = binascii.unhexlify('%x' % (int('0b'+binary, 2)))
	return message

def encode(binary, digit):
	binary = str(binary)
	binary = binary[:-1]+digit
	return binary
	
def decode(binary):
	binary = str(binary)
	print binary[-1]
	print "=====================+++++++++++++++++++========================="
	return binary[-1]


def hide(filename,message):
	img = Image.open(filename)
	binary_message = str2bin(message) + "1111111111111110"
	
	if img.mode in ('RGB'):
		img = img.convert('RGB')
		pixel_list = img.getdata()

		new_pixel_list = []
		digit = 0
		temp = ''

		for pixel in pixel_list:
			if digit < len(binary_message):
				r = bin2num(encode(num2bin(pixel[0]),binary_message[digit]))
				digit += 1
			else:
				r = pixel[0]
			if digit < len(binary_message):
				g = bin2num(encode(num2bin(pixel[1]),binary_message[digit]))
				digit += 1
			else:
				g = pixel[1]
			if digit < len(binary_message):
				b = bin2num(encode(num2bin(pixel[2]),binary_message[digit]))
				digit += 1
			else:
				b = pixel[2]
				
			new_pixel_list.append((r, g, b, 255))
			
		print binary_message
		print "=================="
		img.putdata(new_pixel_list)
		
		file_type = filename.split(".")[-1]
		
		if file_type.lower() == "png":
			img.save(filename)
		elif file_type.lower() == "jpg":
			img.save(filename)
		elif file_type.lower() == "jpeg":
			img.save(filename,"JPEG")
		elif file_type.lower() == "gif":
			img.save(filename, format="GIF")
		return True
	return False


def retr(filename):
	img = Image.open(filename)
	binary_message = ""
	print img.mode
	if img.mode in ('RGB'):
		img = img.convert('RGB')
		pixel_list = img.getdata()

		for pixel in pixel_list:
			digit = decode(num2bin(pixel[0]))
			binary_message += digit
			if binary_message[-16:] == "1111111111111110":
				break;

			digit = decode(num2bin(pixel[1]))
			binary_message += digit
			if binary_message[-16:] == "1111111111111110":
				break;

			digit = decode(num2bin(pixel[2]))
			binary_message += digit
			if binary_message[-16:] == "1111111111111110":
				break;
			
		print binary_message
		print "++++++++++++++++++"
		return bin2str(binary_message[:-16])
	return None



if __name__ == "__main__":
	app.run(debug=True)

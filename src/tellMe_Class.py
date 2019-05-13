#----------------------------------------------------------------------------------------
# HRW- Modul: Eingebettete Systeme
# Gruppe: TELL-ME
# Mitglieder: Lukas Kandora, Thilo Voigt, Jan Vogt
#----------------------------------------------------------------------------------------

import io
import sys
import os
import os.path as path
import picamera
import time
import json
import datetime
from google.cloud import vision
from google.cloud.vision import types
from google.cloud import texttospeech
import RPi.GPIO as GPIO
import time

class TellMe:

	def __init__(self):
		self.status = "init"
		self.camera = picamera.PiCamera()

	def makePicture(self):
		self.status = "makePicture"
		picName = 'picture'
		picDate = datetime.datetime.now()
		#self.camera.start_preview()
		self.camera.capture('../res/' + picName + '.png')
		
	def imageToText(self,filePath):	
		self.status = "imageToText"
		print(myApp.getCurrentTime() + "Send photo to API")
		client = vision.ImageAnnotatorClient()
		file_name =  filePath

		with io.open(file_name, 'rb') as image_file:
			content = image_file.read()
		image = types.Image(content=content)
		response = client.document_text_detection(image=image)	
		#labels = response.label_annotations
		if(len(response.text_annotations) > 0):
			texts = response.text_annotations
			textOfPicture = texts[0].description
			textOfPicture = textOfPicture.replace("\n", " ")
			print(len(textOfPicture))
			if(len(textOfPicture) > 750):
				textOfPicture=textOfPicture[:750]
			print(myApp.getCurrentTime()+ textOfPicture)
		else:
			textOfPicture = ""
		return textOfPicture

	def textToAudio(self,textOfPicture):
		self.status = "textToAudio"
		if not (textOfPicture == ""):
			client = texttospeech.TextToSpeechClient()
			synthesis_input = texttospeech.types.SynthesisInput(text=textOfPicture)
			voice = texttospeech.types.VoiceSelectionParams(
				language_code='de-DE',
				ssml_gender=texttospeech.enums.SsmlVoiceGender.NEUTRAL)
			
			audio_config = texttospeech.types.AudioConfig(
			#audio_encoding=texttospeech.enums.AudioEncoding.MP3)
			audio_encoding=texttospeech.enums.AudioEncoding.LINEAR16,
			speaking_rate=0.9)
			response = client.synthesize_speech(synthesis_input, voice, audio_config)

			with open('../res/output.wav', 'wb') as out:
				out.write(response.audio_content)
				print(self.getCurrentTime() + 'Audio content written to file "output.wav"')
			return "output.wav"
		else:
			return "nodetection.wav"

	def playAudio(self, fileName):
		self.status = "playAudio"
		full_path = path.join(path.abspath(path.join(os.getcwd(),"../res")), fileName )
		os.system('aplay -D bluealsa:HCI=hci0,DEV=B8:D5:0B:C3:02:71,PROFILE=a2dp ' + full_path)

	def getCurrentTime(self):
		return time.strftime("%d.%m.%Y %H:%M:%S") + " - "

#----------------------------------------------------------------------------------------
# Main Loop
#----------------------------------------------------------------------------------------

input_pin = 11
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "/home/pi/tellme/res/HRW_TellMe.json"
GPIO.setmode(GPIO.BOARD)
GPIO.setup(input_pin,GPIO.IN, pull_up_down = GPIO.PUD_DOWN)


full_path = path.join(path.abspath(path.join(os.getcwd(),"../res")), "startup.wav" )
os.system('aplay -D bluealsa:HCI=hci0,DEV=B8:D5:0B:C3:02:71,PROFILE=a2dp ' + full_path)

while True:
	try:
		if(GPIO.input(input_pin)==0):
			myApp = TellMe()
			myApp.makePicture()
			time.sleep(0.5)
			myApp.camera.close()
			print(myApp.getCurrentTime() + "Status:" + str(myApp.status))
			pictureText = myApp.imageToText(path.join(path.abspath(path.join(os.getcwd(),"../res")), 'picture.png' ))
			print(myApp.getCurrentTime() + "Status:" + str(myApp.status))
			audioName = myApp.textToAudio(pictureText)
			print(myApp.getCurrentTime() + "Status:" + str(myApp.status))
			myApp.playAudio(audioName)
			print(myApp.getCurrentTime() + "Status:" + str(myApp.status))
			print(myApp.getCurrentTime() + "Audio played")
	except:
		print "Es ist ein unerwarteter Fehler aufgetreten"
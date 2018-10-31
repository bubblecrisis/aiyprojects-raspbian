#!/usr/bin/env python3

"""A demo of the Google Assistant GRPC recognizer."""

import logging
import pprint

import RPi.GPIO as GPIO
import aiy.assistant.grpc
import aiy.audio
import aiy.voicehat
import subprocess
import wave
import cv2
import time
import sys
from argparse import ArgumentParser

launch_phrase_data = None
image_rotate = 90

#
#    The supported statuses are:
#      - "starting"
#      - "ready"
#      - "listening"
#      - "thinking"
#      - "stopping"
#      - "power-off"
#      - "error"
#

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)

logger = logging.getLogger('face')

def launch_phrase(launch_file):
    read = wave.open(launch_file,'rb')
    chunk_size = 3200
    number_of_chunks = int(read.getnframes() / chunk_size)
    
    data_frames = []
    read.rewind()             
    for c in range(0, number_of_chunks):
        data_frames.append(read.readframes(chunk_size))
    return data_frames

def process_arg():
    parser = ArgumentParser()
    parser.add_argument("-l", "--launch", help="Launch *.wav file", metavar="FILE")
    parser.add_argument("-r", "--rotate", help="Rotate image",  type=int, metavar="N")
    return parser.parse_args()

def wait_for_face(faceCascade):
    global image_rotate
    cap = cv2.VideoCapture(0)
    cap.set(3,640) # set Width
    cap.set(4,480) # set Height
    try:
        face_found = False
        logger.info('Waiting for a face...')
        while not face_found:
            time.sleep(0.5)
            ret, img = cap.read()

            # img = cv2.flip(img, -1)
            # rotate image
            (h, w) = img.shape[:2]
            center = (w/2, h/2)
            M = cv2.getRotationMatrix2D(center, image_rotate, 1.0)
            img = cv2.warpAffine(img, M, (h, w))

            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = faceCascade.detectMultiScale(gray,scaleFactor=1.2,minNeighbors=5,minSize=(20, 20))
            logger.info('detecting face...')
            for (x,y,w,h) in faces:
                if w > 50 and h > 50:
                    face_found = True 
                    logger.info('Face detected. x=%s, y=%s, w=%s, h=%s',w,y,w,h)
                    break
                else:
                    logger.info('Face bypassing. x=%s, y=%s, w=%s, h=%s',w,y,w,h)            
    finally:   
        cap.release()

def converse(assistant, status_ui):
    # Hello
    text, audio, state = assistant.send_phrase(launch_phrase("launch/hello.wav"))
    if audio:
        aiy.audio.play_audio(audio, assistant.get_volume())

    # Wait for answer    
    # with aiy.audio.get_recorder():
        continue_conversation = True
        while continue_conversation:
            status_ui.status('listening')
            print('Listening...')
            text, audio, state = assistant.recognize()
            if text:
                if text == 'shut down':
                    logger.info("Shutting down, goodbye")
                    subprocess.call("sudo shutdown now", shell=True)
                    sys.exit()
                    return
                if text == 'reboot':
                    logger.info("Rebooting")
                    subprocess.call("sudo shutdown -r now", shell=True)
                    sys.exit()
                    return
                if text == 'goodbye':
                    status_ui.status('power-off')
                    logger.info('Goodbye')
                    silent_launch(assistant)
                    continue_conversation = False
                print('You said "', text, '"')

            if audio:
                status_ui.status('thinking')
                aiy.audio.play_audio(audio, assistant.get_volume())

def silent_launch(assistant):
    global launch_phrase_data
    if launch_phrase_data:
        logger.info('Launching skill...')
        text, audio, state = assistant.send_phrase(launch_phrase_data)
        if audio:
            logger.info('Skil launched')

def main():
    global launch_phrase_data
    global image_rotate

    arguments = process_arg()
    status_ui = aiy.voicehat.get_status_ui()
    status_ui.status('starting')
    assistant = aiy.assistant.grpc.get_assistant()
    status_ui.status('ready')
    
    # Launch phrase option
    if arguments.launch:
        launch_phrase_data = launch_phrase(arguments.launch)
        silent_launch(assistant)
    if arguments.rotate:
        image_rotate = arguments.rotate     

    faceCascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')
    with aiy.audio.get_recorder():
        try:
            while True:
                wait_for_face(faceCascade)
                converse(assistant, status_ui)
        finally:
            cap.release()        



if __name__ == '__main__':
    try:
        main()
    finally:
        GPIO.cleanup()
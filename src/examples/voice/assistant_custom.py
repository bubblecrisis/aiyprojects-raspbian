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
from argparse import ArgumentParser

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
    return parser.parse_args()

def main():
    arguments = process_arg()
    status_ui = aiy.voicehat.get_status_ui()
    status_ui.status('starting')
    assistant = aiy.assistant.grpc.get_assistant()
    button = aiy.voicehat.get_button()
    status_ui.status('ready')
    print('Press the button and speak')
    button.wait_for_press()

    # Send launch phrase
    if arguments.launch:
        text, audio, state = assistant.send_phrase(launch_phrase(arguments.launch))
        if audio:
            aiy.audio.play_audio(audio, assistant.get_volume())

    # Wait for answer    
    with aiy.audio.get_recorder():
        while True:
            status_ui.status('listening')
            print('Listening...')
            text, audio, state = assistant.recognize()
            if text:
                if text == 'shut down':
                    print("Shutting down, goodbye")
                    subprocess.call("sudo shutdown now", shell=True)
                    return
                if text == 'reboot':
                    print("Rebooting")
                    subprocess.call("sudo shutdown -r now", shell=True)
                    return
                if text == 'goodbye':
                    status_ui.status('power-off')
                    print('Bye!')
                    return
                print('You said "', text, '"')

            if audio:
                status_ui.status('thinking')
                aiy.audio.play_audio(audio, assistant.get_volume())


if __name__ == '__main__':
    try:
        main()
    finally:
        GPIO.cleanup()
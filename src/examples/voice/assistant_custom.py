#!/usr/bin/env python3

"""A demo of the Google Assistant GRPC recognizer."""

import logging
import pprint

import aiy.assistant.grpc
import aiy.audio
import aiy.voicehat
import subprocess
import wave

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)

def launch_phrase():
    read = wave.open('./launch/nab.wav','rb')
    size = read.getnframes() * read.getsampwidth() * read.getnchannels()
    chunk = size / 3200
    data_frames = []

    for c in range(chunk):
        data_frames[c] = read.readframes(read.tell() + c + 1)
    return data_frames

def main():
    status_ui = aiy.voicehat.get_status_ui()
    status_ui.status('starting')
    assistant = aiy.assistant.grpc.get_assistant()
    button = aiy.voicehat.get_button()
    status_ui.status('ready')
    print('Press the button and speak')
    button.wait_for_press()

    # Send launch phrase
    text, audio, state = assistant.send_phrase(launch_phrase())
    if audio:
        aiy.audio.play_audio(audio, assistant.get_volume())

    # Wait for answer    
    status_ui.status('listening')
    with aiy.audio.get_recorder():
        while True:

            print('Listening...')
            text, audio, state = assistant.recognize()
            if text:
                if text == 'shut down':
                    print("Shutting down, goodbye")
                    subprocess.call("sudo shutdown now", shell=True)
                    break
                if text == 'reboot':
                    print("Rebooting")
                    subprocess.call("sudo shutdown -r now", shell=True)
                    break
                if text == 'goodbye':
                    status_ui.status('stopping')
                    print('Bye!')
                    break
                print('You said "', text, '"')

            if audio:
                aiy.audio.play_audio(audio, assistant.get_volume())


if __name__ == '__main__':
    main()

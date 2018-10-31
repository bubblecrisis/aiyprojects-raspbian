#!/usr/bin/env python3

"""A demo of the Google Assistant GRPC recognizer."""

import logging
import pprint
import cv2
import time

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s:%(name)s:%(message)s"
)

def main():
  print('started')
  faceCascade = cv2.CascadeClassifier('haarcascades/haarcascade_frontalface_default.xml')

  cap = cv2.VideoCapture(0)
  cap.set(3,640) # set Width
  cap.set(4,480) # set Height

  try:
    while True:
      ret, img = cap.read()
#      img = cv2.flip(img, -1)
      # rotate 90
      (h, w) = img.shape[:2]
      center = (w/2, h/2)
      M = cv2.getRotationMatrix2D(center, 90, 1.0)
      img = cv2.warpAffine(img, M, (h, w))

      gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
      faces = faceCascade.detectMultiScale(gray,scaleFactor=1.2,minNeighbors=5,minSize=(20, 20))
#      time.sleep(1)
      pprint.pprint(faces)
  finally:
    cap.release()

if __name__ == '__main__':
  main()

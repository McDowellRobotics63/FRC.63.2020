#
# This is a demo program showing CameraServer usage with OpenCV to do image
# processing. The image is acquired from the USB camera, then a rectangle
# is put on the image and sent to the dashboard. OpenCV has many methods
# for different types of processing.
#
# NOTE: This code runs in its own process, so we cannot access the robot here,
#       nor can we create/use/see wpilib objects
#
# To try this code out locally (if you have robotpy-cscore installed), you
# can execute `python3 -m cscore vision.py:main`
#

import cv2
import numpy

from cscore import CameraServer


def main():

    IMG_WIDTH = 320
    IMG_HEIGHT = 240
    H_LOW = 50
    H_HIGH = 90
    S_LOW = 98
    S_HIGH = 244
    V_LOW = 73
    V_HIGH = 136

    hsv_frame = None
    threshold_frame = None

    cs = CameraServer.getInstance()
    cs.enableLogging()

    camera = cs.startAutomaticCapture()

    camera.setResolution(IMG_WIDTH, IMG_HEIGHT)

    # Get a CvSink. This will capture images from the camera
    cvSink = cs.getVideo()

    # (optional) Setup a CvSource. This will send images back to the Dashboard
    outputStream = cs.putVideo("Rectangle", IMG_WIDTH, IMG_HEIGHT)

    # Allocating new images is very expensive, always try to preallocate
    img = numpy.zeros(shape=(IMG_HEIGHT, IMG_WIDTH, 3), dtype=numpy.uint8)

    # Color threshold values, in HSV space
    low_limit_hsv = numpy.array((H_LOW, S_LOW, V_LOW), dtype=numpy.uint8)
    high_limit_hsv = numpy.array((H_HIGH, S_HIGH, V_HIGH), dtype=numpy.uint8)

    while True:
        # Tell the CvSink to grab a frame from the camera and put it
        # in the source image.  If there is an error notify the output.
        time, img = cvSink.grabFrame(img)
        if time == 0:
            # Send the output the error.
            outputStream.notifyError(cvSink.getError())
            # skip the rest of the current iteration
            continue

        if hsv_frame is None:
            hsv_frame = numpy.empty(shape=img.shape, dtype=numpy.uint8)

        if threshold_frame is None:
            threshold_frame = numpy.empty(shape=img.shape[:2], dtype=numpy.uint8)

        hsv_frame = cv2.cvtColor(img, cv2.COLOR_BGR2HSV, dst=hsv_frame)
        threshold_frame = cv2.inRange(hsv_frame, low_limit_hsv, high_limit_hsv,
                                           dst=threshold_frame)

        # OpenCV 3 returns 3 parameters!
        # Only need the contours variable
        _, contours, _ = cv2.findContours(threshold_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        #print(f'Number of contours: {len(contours)}')

        # Give the output stream a new image to display
        outputStream.putFrame(img)


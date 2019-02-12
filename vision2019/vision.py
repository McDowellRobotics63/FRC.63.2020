#!/usr/bin/env python3
#----------------------------------------------------------------------------
# Copyright (c) 2018 FIRST. All Rights Reserved.
# Open Source Software - may be modified and shared by FRC teams. The code
# must be accompanied by the FIRST BSD license file in the root directory of
# the project.
#----------------------------------------------------------------------------

import json
import time
import sys

import numpy
import cv2

from cscore import CameraServer, VideoSource, UsbCamera, MjpegServer
from networktables import NetworkTablesInstance
from networktables import NetworkTables

#   JSON format:
#   {
#       "team": <team number>,
#       "ntmode": <"client" or "server", "client" if unspecified>
#       "cameras": [
#           {
#               "name": <camera name>
#               "path": <path, e.g. "/dev/video0">
#               "pixel format": <"MJPEG", "YUYV", etc>   // optional
#               "width": <video mode width>              // optional
#               "height": <video mode height>            // optional
#               "fps": <video mode fps>                  // optional
#               "brightness": <percentage brightness>    // optional
#               "white balance": <"auto", "hold", value> // optional
#               "exposure": <"auto", "hold", value>      // optional
#               "properties": [                          // optional
#                   {
#                       "name": <property name>
#                       "value": <property value>
#                   }
#               ],
#               "stream": {                              // optional
#                   "properties": [
#                       {
#                           "name": <stream property name>
#                           "value": <stream property value>
#                       }
#                   ]
#               }
#           }
#       ]
#   }

configFile = "/boot/frc.json"
team = None
server = False
cameraConfigs = []
cameras = []

cs = None

H_LOW = 50
H_HIGH = 90
S_LOW = 98
S_HIGH = 244
V_LOW = 73
V_HIGH = 136

class CameraConfig: pass

"""Report parse error."""
def parseError(str):
    print("config error in '" + configFile + "': " + str, file=sys.stderr)

"""Read single camera configuration."""
def readCameraConfig(config):
    cam = CameraConfig()

    # name
    try:
        cam.name = config["name"]
    except KeyError:
        parseError("could not read camera name")
        return False

    # path
    try:
        cam.path = config["path"]
    except KeyError:
        parseError("camera '{}': could not read path".format(cam.name))
        return False

    # stream properties
    cam.streamConfig = config.get("stream")

    cam.config = config

    cameraConfigs.append(cam)
    return True

"""Read configuration file."""
def readConfig():
    global team
    global server

    # parse file
    try:
        with open(configFile, "rt") as f:
            j = json.load(f)
    except OSError as err:
        print("could not open '{}': {}".format(configFile, err), file=sys.stderr)
        return False

    # top level must be an object
    if not isinstance(j, dict):
        parseError("must be JSON object")
        return False

    # team number
    try:
        team = j["team"]
    except KeyError:
        parseError("could not read team number")
        return False

    # ntmode (optional)
    if "ntmode" in j:
        str = j["ntmode"]
        if str.lower() == "client":
            server = False
        elif str.lower() == "server":
            server = True
        else:
            parseError("could not understand ntmode value '{}'".format(str))

    # cameras
    try:
        cameras = j["cameras"]
    except KeyError:
        parseError("could not read cameras")
        return False
    for camera in cameras:
        if not readCameraConfig(camera):
            return False

    return True

"""Start running the camera."""
def startCameras():
    global cs

    for config in cameraConfigs:
        print("Starting camera '{}' on {}".format(config.name, config.path))
        camera = UsbCamera(config.name, config.path)

        camera.setConfigJson(json.dumps(config.config))
        camera.setConnectionStrategy(VideoSource.ConnectionStrategy.kKeepOpen)

        if config.name == "driver_cam" and config.streamConfig is not None:
            print("Starting automatic capture for camera '{}'".format(config.name))
            server = cs.startAutomaticCapture(camera=camera, return_server=True)
            server.setConfigJson(json.dumps(config.streamConfig))

        cameras.append(camera)

def main_loop():
    global cs

    hsv_frame = None
    threshold_frame = None

    nt = NetworkTables.getTable("team63_vision_table")

    target_cam = None
    for camera in cameras:
        if "usb-0:1.3:1.0" in camera.getPath():
            target_cam = camera

    if target_cam is None:
        print("Could not find target camera!!!!")
        sys.exit(1)

    # Get a CvSink. This will capture images from the camera
    cvSink = cs.getVideo(camera=target_cam)

    # Setup a CvSource. This will send images back to the Dashboard
    outputStream = cs.putVideo("target", target_cam.getVideoMode().width, target_cam.getVideoMode().height)

    # Allocating new images is very expensive, always try to preallocate
    img = numpy.zeros(shape=(target_cam.getVideoMode().height, target_cam.getVideoMode().width, 3), dtype=numpy.uint8)
    hsv_frame = numpy.empty(shape=img.shape, dtype=numpy.uint8)
    threshold_frame = numpy.empty(shape=img.shape[:2], dtype=numpy.uint8)

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

        hsv_frame = cv2.cvtColor(img, cv2.COLOR_BGR2HSV, dst=hsv_frame)
        threshold_frame = cv2.inRange(hsv_frame, low_limit_hsv, high_limit_hsv,
                                           dst=threshold_frame)

        # OpenCV 3 returns 3 parameters!
        # Only need the contours variable
        _, contours, _ = cv2.findContours(threshold_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        nt.putNumber("count_contours", len(contours))

        cv2.rectangle(img, (100, 100), (300, 300), (255, 255, 255), 5)

        # Give the output stream a new image to display
        outputStream.putFrame(img)

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        configFile = sys.argv[1]

    # read configuration
    if not readConfig():
        sys.exit(1)

    cs = CameraServer.getInstance()

    # start NetworkTables
    ntinst = NetworkTablesInstance.getDefault()
    if server:
        print("Setting up NetworkTables server")
        ntinst.startServer()
    else:
        print("Setting up NetworkTables client for team {}".format(team))
        ntinst.startClientTeam(team)

    startCameras()
    main_loop()


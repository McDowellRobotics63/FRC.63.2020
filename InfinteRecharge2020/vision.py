from cscore import CameraServer

def run():
    cs = CameraServer.getInstance()
    cs.enableLogging()
    cs.startAutomaticCapture()
    cs.setResolution(480, 320)

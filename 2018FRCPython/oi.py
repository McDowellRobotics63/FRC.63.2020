
from xboxcontroller import XboxController

class OI(object):

    def __init__(self, robot):
        self.robot = robot

        self.controller1 = XboxController(0)
        self.controller2 = XboxController(1)

    def getController1(self):
        return self.controller1

    def getController2(self):
        return self.controller2

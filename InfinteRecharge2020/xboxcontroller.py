import wpilib
from wpilib import Joystick
from networktables.util import ntproperty

import wpilib
#from xboxdpadbutton import XboxDPadButton

import robotmap

import math


class XBox(Joystick):
    def __init__(self, port):
        super().__init__(port)

    def conditonAxis(self, axis, deadband, rate, expo, power, minimum, maximum):
        deadband = min(abs(deadband), 1)
        rate = max(0.1, min(abs(rate), 10))
        expo = max(0, min(abs(expo), 1))
        power = max(1, min(abs(power), 10))

        if axis > -deadband and axis < deadband:
            axis = 0
        else:
            axis = rate * (math.copysign(1, axis) * ((abs(axis) - deadband) / (1 - deadband)))

        if expo > 0.01:
            axis = ((axis * (abs(axis) ** power) * expo) + (axis * (1 - expo)))

        axis = max(min(axis, maximum), minimum)

        return axis

    def leftStickX(self):
        return -self.conditonAxis(self.getRawAxis(robotmap.XBOX_LEFT_X_AXIS), 0.06, 0.85, 0.6, 1.5, -1, 1)

    def leftStickY(self):
        return self.conditonAxis(self.getRawAxis(robotmap.XBOX_LEFT_Y_AXIS), 0.06, 0.85, 0.6, 1.5, -1, 1)

    def rightStickX(self):
        return -self.conditonAxis(self.getRawAxis(robotmap.XBOX_RIGHT_X_AXIS), 0.15, 0.85, 0.6, 1.5, -1, 1)

    def rightStickY(self):
        return self.conditonAxis(self.getRawAxis(robotmap.XBOX_RIGHT_Y_AXIS), 0.15, 0.85, 0.6, 1.5, -1, 1)

    def A(self):
        return self.getRawButton(robotmap.XBOX_A)

    def B(self):
        return self.getRawButton(robotmap.XBOX_B)

    def X(self):
        return self.getRawButton(robotmap.XBOX_X)

    def Y(self):
        return self.getRawButton(robotmap.XBOX_Y)

    def Start(self):
        return self.getRawButton(robotmap.XBOX_START)

    def Back(self):
        return self.getRawButton(robotmap.XBOX_BACK)

    def LeftBumper(self):
        return self.getRawButton(robotmap.XBOX_LEFT_BUMPER)

    def RightBumper(self):
        return self.getRawButton(robotmap.XBOX_RIGHT_BUMPER)

    def getDPadUp(self):
        return self.getPOV() == 0

    def getDPadRight(self):
        return self.getPOV() == 90

    def getDPadDown(self):
        return self.getPOV() == 180

    def getDPadLeft(self):
        return self.getPOV() == 270
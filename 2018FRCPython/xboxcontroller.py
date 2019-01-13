

from wpilib import Joystick
from wpilib.buttons import JoystickButton

from xboxdpadbutton import DPAD_BUTTON

import robotmap

class XboxController(Joystick):
    def __init__(self, port):
        super().__init__(port)
        self.btnX = JoystickButton(self, robotmap.XBOX_X)
        self.btnY = JoystickButton(self, robotmap.XBOX_Y)
        self.btnA = JoystickButton(self, robotmap.XBOX_A)
        self.btnB = JoystickButton(self, robotmap.XBOX_B)
        self.btnLB = JoystickButton(self, robotmap.XBOX_LEFT_BUMPER)
        self.btnRB = JoystickButton(self, robotmap.XBOX_RIGHT_BUMPER)
        self.btnStart = JoystickButton(self, robotmap.XBOX_START)
        self.btnBack = JoystickButton(self, robotmap.XBOX_BACK)
        self.btnDpadUp = JoystickButton(self, DPAD_BUTTON.DPAD_UP)
        self.btnDpadRight = JoystickButton(self, DPAD_BUTTON.DPAD_RIGHT)
        self.btnDpadDown = JoystickButton(self, DPAD_BUTTON.DPAD_DOWN)
        self.btnDpadLeft = JoystickButton(self, DPAD_BUTTON.DPAD_LEFT)

    def LeftStickY(self):
        return -self.getRawAxis(robotmap.XBOX_LEFT_Y_AXIS)

    def LeftStickX(self):
        return self.getRawAxis(robotmap.XBOX_LEFT_X_AXIS)

    def RightStickY(self):
        return -self.getRawAxis(robotmap.XBOX_RIGHT_Y_AXIS)

    def RightStickX(self):
        return self.getRawAxis(robotmap.XBOX_RIGHT_X_AXIS)

    def X(self):
        return self.btnX

    def Y(self):
        return self.btnY

    def A(self):
        return self.btnA

    def B(self):
        return self.btnB

    def LeftBumper(self):
        return self.btnLB

    def RightBumper(self):
        return self.btnRB

    def Start(self):
        return self.btnStart

    def Back(self):
        return self.btnBack

    def DpadUp(self):
        return self.btnDpadUp

    def DpadDown(self):
        return self.btnDpadDown

    def DpadLeft(self):
        return self.btnDpadLeft

    def DpadRight(self):
        return self.btnDpadRight

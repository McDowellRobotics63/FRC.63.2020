from wpilib import Joystick
from wpilib.buttons import JoystickButton
from wpilib.smartdashboard import SmartDashboard
from networktables.util import ntproperty
import wpilib

from xboxdpadbutton import DPAD_BUTTON
from xboxdpadbutton import XboxDPadButton

import robotmap

import math

class XboxController(Joystick):
    #Left Y
    left_y_rate = ntproperty("/DriveSettings/left_y_rate", 0.85, persistent = True)
    left_y_expo = ntproperty("/DriveSettings/left_y_expo", 0.6, persistent = True)
    left_y_deadband = ntproperty("/DriveSettings/left_y_deadband", 0.02, persistent = True)
    left_y_power = ntproperty("/DriveSettings/left_y_power", 1.5, persistent = True)
    left_y_min = ntproperty("/DriveSettings/left_y_min", -1.0, persistent = True)
    left_y_max = ntproperty("/DriveSettings/left_y_max", 1.0, persistent = True)

    #Left X
    left_x_rate = ntproperty("/DriveSettings/left_x_rate", 0.85, persistent = True)
    left_x_expo = ntproperty("/DriveSettings/left_x_expo", 0.6, persistent = True)
    left_x_deadband = ntproperty("/DriveSettings/left_x_deadband", 0.02, persistent = True)
    left_x_power = ntproperty("/DriveSettings/left_x_power", 1.5, persistent = True)
    left_x_min = ntproperty("/DriveSettings/left_x_min", -1.0, persistent = True)
    left_x_max = ntproperty("/DriveSettings/left_x_max", 1.0, persistent = True)
    
    #Right Y
    right_y_rate = ntproperty("/DriveSettings/right_y_rate", 1.0, persistent = True)
    right_y_expo = ntproperty("/DriveSettings/right_y_expo", 0.0, persistent = True)
    right_y_deadband = ntproperty("/DriveSettings/right_y_deadband", 0.1, persistent = True)
    right_y_power = ntproperty("/DriveSettings/right_y_power", 1.0, persistent = True)
    right_y_min = ntproperty("/DriveSettings/right_y_min", -1.0, persistent = True)
    right_y_max = ntproperty("/DriveSettings/right_y_max", 1.0, persistent = True)

    #Right X
    right_x_rate = ntproperty("/DriveSettings/right_x_rate", 1.0, persistent = True)
    right_x_expo = ntproperty("/DriveSettings/right_x_expo", 0.0, persistent = True)
    right_x_deadband = ntproperty("/DriveSettings/right_x_deadband", 0.1, persistent = True)
    right_x_power = ntproperty("/DriveSettings/right_x_power", 1.0, persistent = True)
    right_x_min = ntproperty("/DriveSettings/right_x_min", -1.0, persistent = True)
    right_x_max = ntproperty("/DriveSettings/right_x_max", 1.0, persistent = True)

    creep_x_rate = ntproperty("/DriveSettings/creep_x_rate", 0.6, persistent = True)
    creep_x_expo = ntproperty("/DriveSettings/creep_x_expo", 0.6, persistent = True)
    creep_x_deadband = ntproperty("/DriveSettings/creep_x_deadband", 0.02, persistent = True)
    creep_x_power = ntproperty("/DriveSettings/creep_x_power", 1.5, persistent = True)
    creep_x_min = ntproperty("/DriveSettings/creep_x_min", -1.0, persistent = True)
    creep_x_max = ntproperty("/DriveSettings/creep_x_max", 1.0, persistent = True)

    creep_y_rate = ntproperty("/DriveSettings/creep_y_rate", 0.6, persistent = True)
    creep_y_expo = ntproperty("/DriveSettings/creep_y_expo", 0.6, persistent = True)
    creep_y_deadband = ntproperty("/DriveSettings/creep_y_deadband", 0.02, persistent = True)
    creep_y_power = ntproperty("/DriveSettings/creep_y_power", 1.5, persistent = True)
    creep_y_min = ntproperty("/DriveSettings/creep_y_min", -1.0, persistent = True)
    creep_y_max = ntproperty("/DriveSettings/creep_y_max", 1.0, persistent = True)

    def __init__(self, port):
        super().__init__(port)

        self.timer = wpilib.Timer()
        self.timer.start()

        self.btnX = JoystickButton(self, robotmap.XBOX_X)
        self.btnY = JoystickButton(self, robotmap.XBOX_Y)
        self.btnA = JoystickButton(self, robotmap.XBOX_A)
        self.btnB = JoystickButton(self, robotmap.XBOX_B)
        self.btnLB = JoystickButton(self, robotmap.XBOX_LEFT_BUMPER)
        self.btnRB = JoystickButton(self, robotmap.XBOX_RIGHT_BUMPER)
        self.btnStart = JoystickButton(self, robotmap.XBOX_START)
        self.btnBack = JoystickButton(self, robotmap.XBOX_BACK)
        self.btnDpadUp = XboxDPadButton(self, DPAD_BUTTON.DPAD_UP)
        self.btnDpadRight = XboxDPadButton(self, DPAD_BUTTON.DPAD_RIGHT)
        self.btnDpadDown = XboxDPadButton(self, DPAD_BUTTON.DPAD_DOWN)
        self.btnDpadLeft = XboxDPadButton(self, DPAD_BUTTON.DPAD_LEFT)

    def config(self):
        pass
    
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

    def LeftStickY(self):
        return self.conditonAxis(-self.getRawAxis(robotmap.XBOX_LEFT_Y_AXIS), self.left_y_deadband, self.left_y_rate, self.left_y_expo, self.left_y_power, self.left_y_min, self.left_y_max)

    def LeftStickX(self):
        return self.conditonAxis(self.getRawAxis(robotmap.XBOX_LEFT_X_AXIS), self.left_x_deadband, self.left_x_rate, self.left_x_expo, self.left_x_power, self.left_x_min, self.left_x_max)

    def RightStickY(self):
        return self.conditonAxis(-self.getRawAxis(robotmap.XBOX_RIGHT_Y_AXIS), self.right_y_deadband, self.right_y_rate, self.right_y_expo, self.right_y_power, self.right_y_min, self.right_y_max)

    def RightStickX(self):
        return self.conditonAxis(self.getRawAxis(robotmap.XBOX_RIGHT_X_AXIS), self.right_x_deadband, self.right_x_rate, self.right_x_expo, self.right_x_power, self.right_x_min, self.right_x_max)

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

    def pulseRumble(self, time):
        pulse_time = 0.5

        if self.timer.get() > 0 and self.timer.get() < pulse_time:
            self.setRumble(Joystick.RumbleType.kRightRumble, 0.5)
        elif self.timer.get() > pulse_time and self.timer.get() < (time + pulse_time):
            self.setRumble(Joystick.RumbleType.kRightRumble, 0)
        elif self.timer.get() > (time + pulse_time):
            self.timer.reset()    
            self.timer.start()

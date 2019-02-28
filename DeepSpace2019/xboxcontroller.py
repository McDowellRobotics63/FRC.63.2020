from wpilib import Joystick
from wpilib.buttons import JoystickButton
from wpilib.smartdashboard import SmartDashboard

from xboxdpadbutton import DPAD_BUTTON

import robotmap

import math

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

        #Left Y
        self.mlyRate = SmartDashboard.getNumber("left_y_rate", 0)
        self.mlyExpo = SmartDashboard.getNumber("left_y_expo", 0)
        self.mlyDeadband = SmartDashboard.getNumber("left_y_deadband", 0)
        self.mlyPower = SmartDashboard.getNumber("left_y_power", 0)
        self.mlyMin = SmartDashboard.getNumber("left_y_min", 0)
        self.mlyMax = SmartDashboard.getNumber("left_y_max", 0)
        #Left X
        self.mlxRate = SmartDashboard.getNumber("left_x_rate", 0)
        self.mlxExpo = SmartDashboard.getNumber("left_x_expo", 0)
        self.mlxDeadband = SmartDashboard.getNumber("left_x_deadband", 0)
        self.mlxPower = SmartDashboard.getNumber("left_x_power", 0)
        self.mlxMin = SmartDashboard.getNumber("left_x_min", 0)
        self.mlxMax = SmartDashboard.getNumber("left_x_max", 0)

        #Left Y
        self.mryRate = SmartDashboard.getNumber("right_y_rate", 0)
        self.mryExpo = SmartDashboard.getNumber("right_y_expo", 0)
        self.mryDeadband = SmartDashboard.getNumber("right_y_deadband", 0)
        self.mryPower = SmartDashboard.getNumber("right_y_power", 0)
        self.mryMin = SmartDashboard.getNumber("right_y_min", 0)
        self.mryMax = SmartDashboard.getNumber("right_y_max", 0)
        #Left X
        self.mrxRate = SmartDashboard.getNumber("right_x_rate", 0)
        self.mrxExpo = SmartDashboard.getNumber("right_x_expo", 0)
        self.mrxDeadband = SmartDashboard.getNumber("right_x_deadband", 0)
        self.mrxPower = SmartDashboard.getNumber("right_x_power", 0)
        self.mrxMin = SmartDashboard.getNumber("right_x_min", 0)
        self.mrxMax = SmartDashboard.getNumber("right_x_max", 0)

    def conditonAxis(self, axis, deadband, rate, expo, power, minimum, maximum):
        deadband = min(abs(deadband), 1)
        rate = max(0.1, min(abs(rate), 10))
        expo = max(0, min(abs(expo), 1))
        power = max(1, min(abs(power), 10))

        if axis > -deadband and axis < deadband:
            axis = 0
        
        axis = (math.copysign(1, axis) * ((abs(axis) - deadband) / (1 - deadband)))

        if expo > 0.01:
            axis = rate * ((axis * (abs(axis) ** power) * expo) + (axis * (1 + expo)))
        else:
            axis = rate * axis

        max(min(axis, maximum), minimum)

        return axis

    def LeftStickY(self):
        #return -self.getRawAxis(robotmap.XBOX_LEFT_Y_AXIS)
        return self.conditonAxis(-self.getRawAxis(robotmap.XBOX_LEFT_Y_AXIS), self.mlyDeadband, self.mlyRate, self.mlyExpo, self.mlyPower, self.mlyMin, self.mlyMax)

    def LeftStickX(self):
        #return self.getRawAxis(robotmap.XBOX_LEFT_X_AXIS)
        return self.conditonAxis(self.getRawAxis(robotmap.XBOX_LEFT_X_AXIS), self.mlxDeadband, self.mlxRate, self.mlxExpo, self.mlxPower, self.mlxMin, self.mlxMax)

    def RightStickY(self):
        #return -self.getRawAxis(robotmap.XBOX_RIGHT_Y_AXIS)
        return self.conditonAxis(-self.getRawAxis(robotmap.XBOX_RIGHT_Y_AXIS), self.mryDeadband, self.mryRate, self.mryExpo, self.mryPower, self.mryMin, self.mryMax)

    def RightStickX(self):
        #return self.getRawAxis(robotmap.XBOX_RIGHT_X_AXIS)
        return self.conditonAxis(self.getRawAxis(robotmap.XBOX_RIGHT_X_AXIS), self.mrxDeadband, self.mrxRate, self.mrxExpo, self.mrxPower, self.mrxMin, self.mrxMax)

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

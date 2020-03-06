import wpilib
from wpilib import Solenoid
from wpilib import Spark

from rev.color import ColorSensorV3

import robotmap
import xboxcontroller

class ColorWheel():
    def __init__(self):
        self.colorWheelExtend = Solenoid(robotmap.PCM_ID, robotmap.COLOR_WHEEL_EXTEND_SOLENOID)
        self.colorWheelRetract = Solenoid(robotmap.PCM_ID, robotmap.COLOR_WHEEL_RETRACT_SOLENOID)

        self.colorWheelMotor = Spark(robotmap.COLOR_WHEEL_ID)

        self.RGBSensor = ColorSensorV3(wpilib.I2C.Port.kOnboard)

        self.colorWheelExtend.set(False)
        self.colorWheelRetract.set(True)

    def DeployWheelArm(self):
        self.colorWheelExtend.set(True)
        self.colorWheelRetract.set(False)

    def StowWheelArm(self):
        self.colorWheelExtend.set(False)
        self.colorWheelRetract.set(True)

    def Iterate(self, copilot: xboxcontroller.XBox):
        self.color = self.RGBSensor.getColor()

        self.ir = self.RGBSensor.getIR()

        self.proxy = self.RGBSensor.getProximity() #proxy's still alive Jazz band


        if self.color.red > 0.7 and self.color.red <= 1:
            self.red = True
        elif self.color.green > 0.7 and self.color.green <= 1:
            self.green = True
        elif self.color.blue > 0.7 and self.color.blue <= 1:
            self.blue = True
        else:
            self.red = False
            self.green = False
            self.blue = False

        #Boolean
        wpilib.SmartDashboard.putBoolean("Red", self.red)
        
        wpilib.SmartDashboard.putBoolean("Green", self.green)
        
        wpilib.SmartDashboard.putBoolean("Blue", self.blue)

        #Value
        wpilib.SmartDashboard.putNumber("RedN", self.color.red)

        wpilib.SmartDashboard.putNumber("BlueN", self.color.blue)

        wpilib.SmartDashboard.putNumber("GreenN", self.color.green)

        wpilib.SmartDashboard.putNumber("IR", self.ir)

        wpilib.SmartDashboard.putNumber("Proxy", self.proxy)

        #print(self.color)

        if copilot.X():
            self.colorWheelMotor.set(0.5)
        elif copilot.B():
            self.colorWheelMotor.set(-0.5)
        else:
            self.colorWheelMotor.stopMotor()

        if copilot.getDPadRight():
            self.DeployWheelArm()
        elif copilot.getDPadLeft():
            self.StowWheelArm()

        

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

        self.RGBSensor.configureProximitySensorLED

        self.RGBSensor.LEDPulseFrequency.k100kHz
        self.RGBSensor.LEDCurrent.kPulse100mA
        self.RGBSensor.ProximityResolution.k10bit

        #self.red = color.red
        #self.blue = color.blue
        #self.green = color.green

        wpilib.SmartDashboard.putNumber("Rojo", self.color.red)

        wpilib.SmartDashboard.putNumber("Azul", self.color.blue)

        wpilib.SmartDashboard.putNumber("Verde", self.color.green)

        wpilib.SmartDashboard.putNumber("IR", self.ir)

        wpilib.SmartDashboard.putNumber("Proxy", self.proxy)

        if copilot.X():
            self.colorWheelMotor.set(0.5)
        else:
            self.colorWheelMotor.stopMotor()

        if copilot.getDPadUp():
            self.DeployWheelArm()
        elif copilot.getDPadDown():
            self.StowWheelArm()

        

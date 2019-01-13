from wpilib.command.subsystem import Subsystem
from wpilib import Solenoid
from wpilib import Spark
from commands_claw.obtain_box_continuous import ObtainBoxContinuous

from infraredsensor import InfraredSensor

import robotmap

class ClawSubsystem(Subsystem):

    def __init__(self, robot):
        super().__init__("Claw")
        self.robot = robot

        self.leftMotor = Spark(robotmap.CLAWLEFT)
        self.rightMotor = Spark(robotmap.CLAWRIGHT)

        self.CLAW_OPEN = Solenoid(robotmap.PCM1_CANID, robotmap.CLAW_OPEN_SOLENOID)
        self.CLAW_CLOSE = Solenoid(robotmap.PCM1_CANID, robotmap.CLAW_CLOSE_SOLENOID)

        self.sensor = InfraredSensor(robotmap.INFRARED_SENSOR_CHANNEL)

        self.close()

    def initDefaultCommand(self):
        self.setDefaultCommand(ObtainBoxContinuous(self.robot))

    def open(self):
        self.CLAW_OPEN.set(True)
        self.CLAW_CLOSE.set(False)

    def close(self):
        self.CLAW_OPEN.set(False)
        self.CLAW_CLOSE.set(True)

    def setSpeed(self, pullSpeed):
        #positive left speed is pull
        self.leftMotor.set(pullSpeed)
        self.rightMotor.set(-pullSpeed)

    def boxIsClose(self):
        return self.sensor.GetMedianVoltage() > 0.6

    def boxIsReallyClose(self):
        return self.sensor.GetMedianVoltage() > 2.6

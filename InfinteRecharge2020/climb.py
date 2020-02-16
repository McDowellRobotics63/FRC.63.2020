import wpilib
from wpilib import Solenoid
from wpilib import Encoder
import ctre

import robotmap
from xboxcontroller import XBox

class Climb():
    def __init__(self):
        self.climbExtend = Solenoid(robotmap.PCM_ID, robotmap.CLIMB_EXTEND_SOLENOID)
        self.climbRetract = Solenoid(robotmap.PCM_ID, robotmap.CLIMB_RETRACT_SOLENOID)

        self.climbMotor = ctre.WPI_TalonSRX(robotmap.LIFT_WINCH_ID)
        self.climbEncoder = Encoder()

        self.climbExtend.set(False)
        self.climbRetract.set(True)

    def DeployWinch(self):
        self.climbExtend.set(True)
        self.climbRetract.set(False)
        
    def StowWinch(self):
        self.climbExtend.set(False)
        self.climbRetract.set(True)

    def config(self):
        pass

    def Iterate(self, pilot: XBox):
        if pilot.getDPadUp():
            self.DeployWinch()
        elif pilot.getDPadDown():
            self.StowWinch()

        if pilot.Y():
            self.climbMotor.set(0.5)
        elif pilot.A():
            self.climbMotor.set(-0.5)
        else:
            self.climbMotor.stopMotor()
            

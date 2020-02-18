import wpilib
from wpilib import Solenoid
from wpilib import Encoder
import ctre

import robotmap
from xboxcontroller import XBox

class Climb():
    def __init__(self):
        self.climbExtend = Solenoid(robotmap.PCM2_ID, robotmap.CLIMB_EXTEND_SOLENOID)
        self.climbRetract = Solenoid(robotmap.PCM2_ID, robotmap.CLIMB_RETRACT_SOLENOID)

        self.hookExtend = Solenoid(robotmap.PCM2_ID, robotmap.HOOK_EXTEND_SOLENOID)
        self.hookRetract = Solenoid(robotmap.PCM2_ID, robotmap.HOOK_RETRACT_SOLENOID)

        self.climbMotor = ctre.WPI_TalonSRX(robotmap.LIFT_WINCH_ID)

        self.climbExtend.set(False)
        self.climbRetract.set(True)

        self.hookExtend.set(False)
        self.hookRetract.set(True)

    def DeployWinch(self):
        self.climbExtend.set(True)
        self.climbRetract.set(False)
        
    def StowWinch(self):
        self.climbExtend.set(False)
        self.climbRetract.set(True)

    def DeployHook(self):
        self.hookExtend.set(True)
        self.hookRetract.set(False)

    def StowHook(self):
        self.hookExtend.set(False)
        self.hookRetract.set(True)

    def config(self):
        pass

    def Iterate(self, pilot: XBox):
        if pilot.getDPadUp():
            self.DeployWinch()
        elif pilot.getDPadDown():
            self.StowWinch()

        if pilot.RightBumper():
            self.DeployHook()
        elif pilot.LeftBumper():
            self.StowHook()

        if pilot.Y():
            self.climbMotor.set(0.5)
        elif pilot.A():
            self.climbMotor.set(-0.5)
        else:
            self.climbMotor.stopMotor()
            

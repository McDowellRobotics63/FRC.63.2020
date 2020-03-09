#testing branch
#apple bottom jeans

import robotmap

import math

import wpilib
from wpilib import Solenoid
from wpilib import Spark
from wpilib import Talon
from xboxcontroller import XBox


#from robotenums import BallRakeState

class BallChute():
    def __init__(self):
        self.stateTimer = wpilib.Timer()
        self.stateTimer.start()

        self.ballRakeExtend = Solenoid(robotmap.PCM2_ID, robotmap.BALL_RAKE_EXTEND_SOLENOID)
        self.ballRakeRetract = Solenoid(robotmap.PCM2_ID, robotmap.BALL_RAKE_RETRACT_SOLENOID)

        self.ballHatchExtend = Solenoid(robotmap.PCM2_ID, robotmap.BALL_HATCH_EXTEND_SOLENOID)
        self.ballHatchRetract = Solenoid(robotmap.PCM2_ID, robotmap.BALL_HATCH_RETRACT_SOLENOID)

        self.ballTickler = Spark(robotmap.BALL_TICKLER_ID)
        self.bottomIntake = Spark(robotmap.BOTTOM_INTAKE_ID)
        self.rakeMotor = Talon(robotmap.RAKE_ID)

        self.ballRakeExtend.set(False)
        self.ballRakeRetract.set(True)

        self.ballHatchExtend.set(False)
        self.ballHatchRetract.set(True)

    #-value so motors run that way we want them to
    def RakeMotorStart(self, value):
        self.rakeMotor.set(-value)

    def RakeMotorStop(self):
        self.rakeMotor.stopMotor()

    def BottomMotorStart(self, value):
        self.bottomIntake.set(-value)

    def BottomMotorStop(self):
        self.bottomIntake.stopMotor()

    def BallTicklerStart(self, value):
        self.ballTickler.set(value)

    def BallTicklerStop(self):
        self.ballTickler.stopMotor()

    #Solenoid functions ot make things easier
    def DeployRake(self):
        self.ballRakeExtend.set(True)
        self.ballRakeRetract.set(False)

    def StowRake(self):
        self.ballRakeExtend.set(False)
        self.ballRakeRetract.set(True)

    def OpenHatch(self):
        self.ballHatchExtend.set(True)
        self.ballHatchRetract.set(False)
        
    def CloseHatch(self):
        self.ballHatchExtend.set(False)
        self.ballHatchRetract.set(True)

    def Iterate(self, copilot: XBox):
        if copilot.Y():
            if copilot.Start():
                self.BottomMotorStart(1)
            elif copilot.X():
                self.BottomMotorStart(-.5)
            else:
                self.BottomMotorStart(.5)
        else:
            self.BottomMotorStop()

        if copilot.A():
            elif copilot.X():
                self.RakeMotorStart(-.5)
            else:
                self.RakeMotorStart(.5)
        else:
            self.RakeMotorStop()

        if copilot.Start():
            self.OpenHatch()
        elif copilot.Back():
            self.CloseHatch()

        if copilot.RightBumper():
            self.DeployRake()
        elif copilot.LeftBumper():
            self.StowRake()

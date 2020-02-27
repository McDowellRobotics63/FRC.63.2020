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

        self.motorPercent = 0.3

        #self.currentRakeState = BallRakeState.RAKE_STOWED
        #self.currentHatchState = BallRakeState.HATCH_CLOSED

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

    def DeployRake(self):
        #self.currentRakeState = BallRakeState.DEPLOY_BEGIN
        self.ballRakeExtend.set(True)
        self.ballRakeRetract.set(False)

    def StowRake(self):
        #self.currentRakeState = BallRakeState.STOW_BEGIN
        self.ballRakeExtend.set(False)
        self.ballRakeRetract.set(True)

    def OpenHatch(self):
        self.ballHatchExtend.set(True)
        self.ballHatchRetract.set(False)
        
    def CloseHatch(self):
        self.ballHatchExtend.set(False)
        self.ballHatchRetract.set(True)

    def Iterate(self, copilot: XBox):
        '''
        if copilot.X():
            if abs(self.motorPercent) == 0.3:
                self.motorPercent = -0.5

            if abs(self.motorPercent) == 0.5:
                self.motorPercent = -0.5

        elif self.ballHatchExtend.get() and not self.ballHatchRetract.get():
            self.motorPercent = 0.5

        else:
            self.motorPercent = 0.5
            '''

        if copilot.B():
            self.BallTicklerStart(1)
        else:
            self.BallTicklerStop()

        if copilot.Y():
            self.BottomMotorStart(1)
        else:
            self.BottomMotorStop()

        if copilot.A():
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

    def Reverse(self, copilot: XBox):
        while copilot.X():
            if copilot.B():
                self.BallTicklerStart(-1)
            else:
                self.BallTicklerStop()

            if copilot.Y():
                self.BottomMotorStart(-1)
            else:
                self.BottomMotorStop()

            if copilot.A():
                self.RakeMotorStart(-.5)
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

    def Dump(self, copilot: XBox):

        while copilot.Start():
            print("works")
            if copilot.B():
                self.BallTicklerStart(1)
            else:
                self.BallTicklerStop()

            if copilot.Y():
                self.BottomMotorStart(1)
            else:
                self.BottomMotorStop()

            if copilot.A():
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



''' 
    def     IterateStateMachine(self):
            #Deploy Rake#
            if self.currentRakeState == BallRakeState.DEPLOY_BEGIN:
                self.ballRakeExtend.set(True)
                self.ballRakeRetract.set(False)
                self.currentRakeState = BallRakeState.RAKE_DEPLOY_WAIT

                self.stateTimer.reset()
                self.stateTimer.start()

        elif self.currentRakeState == BallRakeState.RAKE_DEPLOY_WAIT:
            if self.stateTimer.hasPeriodPassed(0.5):
                self.currentRakeState = BallRakeState.RAKE_MOTOR_START
        
        elif self.currentRakeState == BallRakeState.RAKE_MOTOR_START:
            self.rakeMotor.set(0.5)

        #Stow Rake#
        elif self.currentRakeState == BallRakeState.STOW_BEGIN:
            self.rakeMotor.stopMotor()
            self.currentRakeState = BallRakeState.RAKE_STOW

        elif self.currentRakeState == BallRakeState.RAKE_STOW:
            self.ballRakeExtend(False)
            self.ballRakeRetract(True)
            self.currentRakeState = BallRakeState.RAKE_STOW_WAIT

            self.stateTimer.reset()
            self.stateTimer.start()

        elif self.currentRakeState == BallRakeState.RAKE_STOW_WAIT:
            if self.stateTimer.hasPeriodPassed(0.5):
                self.currentRakeState = BallRakeState.RAKE_STOWED
'''




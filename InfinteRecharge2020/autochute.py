from enum import Enum

import wpilib

from drive import InfiniteRechargeDrive
from ballchute import BallChute
import robotmap

class AutoState(Enum):
    DRIVE_BACK = 0
    WAIT = 1
    DEPLOY_CHUTE = 2
    DRIVE_FORWARD = 3
    END_AUTO = 4

class AutoChute():
    def __init__(self, drive: InfiniteRechargeDrive, chute: BallChute):
        self.autoTimer = wpilib.Timer()
        self.autoTimer.start()

        self.drive = drive

        self.chute = chute

        self.autoState = AutoState.DRIVE_BACK

    def DriveStraight(self, distance, speed):
        distanceTraveled = 0

        while abs(distanceTraveled) < distance:
            distanceTraveled = self.drive.frontLeftMotor.getSelectedSensorPosition() * robotmap.FEET_PER_UNIT
            self.drive.drive.driveCartesian(0, speed, 0)

        if abs(distanceTraveled) >= distance:
            for talon in self.drive.talons:
                talon.stopMotor()

    def Iterate(self):
        if self.autoState == AutoState.DRIVE_BACK:
            self.DriveStraight(10, -0.5)
            self.autoState = AutoState.WAIT

            self.autoTimer.reset()
            self.autoTimer.start()

        elif self.autoState == AutoState.WAIT:
            if self.autoTimer.hasPeriodPassed(0.5):
                self.autoState = AutoState.DEPLOY_CHUTE

                self.autoTimer.reset()
                self.autoTimer.start()
            
        elif self.autoState == AutoState.DEPLOY_CHUTE:
            self.chute.OpenHatch()
            self.chute.BallTicklerStart()
            self.chute.BottomMotorStart()

            if self.autoTimer.hasPeriodPassed(2):
                self.chute.CloseHatch()
                self.chute.BallTicklerStop()
                self.chute.BottomMotorStop()

                self.autoState = AutoState.DRIVE_FORWARD

        elif self.autoState == AutoState.DRIVE_FORWARD:
            self.DriveStraight(11, 0.5)
            self.autoState = AutoState.END_AUTO

        elif self.autoState == AutoState.END_AUTO:
            for talon in self.drive.talons:
                talon.stopMotor()
            
            self.chute.CloseHatch()
            self.chute.BallTicklerStop()
            self.chute.BottomMotorStop()





    



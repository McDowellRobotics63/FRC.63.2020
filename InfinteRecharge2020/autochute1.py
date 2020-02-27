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

    def DriveStraight(self, unitsTraveled, targetDistance, speed):
        if abs(self.UnitsToFeet(unitsTraveled)) < targetDistance:
            self.drive.drive.driveCartesian(0, speed, 0)

            return False
        else:
            for talon in self.drive.talons:
                talon.stopMotor()

            return True

        '''
        while abs(distanceTraveled) < distance:
            distanceTraveled = self.drive.frontLeftMotor.getSelectedSensorPosition() * robotmap.FEET_PER_UNIT
            self.drive.drive.driveCartesian(0, speed, 0)

        if abs(distanceTraveled) >= distance:
            for talon in self.drive.talons:
                talon.stopMotor()
                '''

    def UnitsToFeet(self, units):
        return units * robotmap.FEET_PER_UNIT

    def Iterate(self):
        if self.autoState == AutoState.DRIVE_BACK:
            #self.DriveStraight(self.drive.frontLeftMotor, 10, -.5)
            targetReached = self.DriveStraight(self.drive.frontLeftMotor.getSelectedSensorPosition(), 10, .5)
            if targetReached:
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
            self.chute.BallTicklerStart(1)

            if self.autoTimer.hasPeriodPassed(5):
                self.chute.CloseHatch()
                self.chute.ballTickler.stopMotor()
                self.chute.BottomMotorStop()

                self.autoState = AutoState.DRIVE_FORWARD
                
                for talon in self.drive.talons:
                    talon.setSelectedSensorPosition(0)

        elif self.autoState == AutoState.DRIVE_FORWARD:
            targetReached = self.DriveStraight(self.drive.frontLeftMotor.getSelectedSensorPosition(), 11, -.5)
            if targetReached:
                self.autoState = AutoState.END_AUTO

        elif self.autoState == AutoState.END_AUTO:
            for talon in self.drive.talons:
                talon.stopMotor()
                talon.setSelectedSensorPosition(0)






    



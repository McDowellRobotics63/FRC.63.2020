from enum import Enum

import wpilib

from drive import InfiniteRechargeDrive
from ballchute import BallChute
import robotmap



class AutoStateSafe(Enum):
    DRIVE_BACK = 0
    WAIT = 1
    DEPLOY_CHUTE = 2
    DRIVE_LEFT = 3
    DRIVE_FORWARD = 4
    END_AUTO = 5
    CLEAR_LINE = 6
    WAIT_CLEAR = 7
    RAM = 8

class AutoChuteSafe():
    def __init__(self, drive: InfiniteRechargeDrive, chute: BallChute):
        self.autoTimer = wpilib.Timer()
        self.autoTimer.start()

        self.drive = drive
        self.BallChute = chute

        self.chute = chute

        self.autoStateSafe = AutoStateSafe.CLEAR_LINE

    def DriveSideways(self, unitsTraveled, targetDistance, speed):
        if abs(self.UnitsToFeet(unitsTraveled)) < targetDistance:
            self.drive.drive.driveCartesian(speed, 0, 0)

            return False
        else:
            for talon in self.drive.talons:
                talon.stopMotor()

            return True

    def DriveStraight(self, unitsTraveled, targetDistance, speed):
        if abs(self.UnitsToFeet(unitsTraveled)) < targetDistance:
            self.drive.drive.driveCartesian(0, speed, 0)

            return False
        else:
            for talon in self.drive.talons:
                talon.stopMotor()

            return True

    def UnitsToFeet(self, units):
        return units * robotmap.FEET_PER_UNIT

    def Iterate(self):
        if self.autoStateSafe == AutoStateSafe.CLEAR_LINE:
            targetReached = self.DriveStraight(self.drive.frontLeftMotor.getSelectedSensorPosition(), 0.5, -0.5)
            if targetReached:
                self.autoStateSafe = AutoStateSafe.WAIT_CLEAR
                self.autoTimer.reset()
                self.autoTimer.start()

                for talon in self.drive.talons:
                    talon.setSelectedSensorPosition(0)

        elif self.autoStateSafe == AutoStateSafe.WAIT_CLEAR:
            if self.autoTimer.hasPeriodPassed(0.5):
                self.autoStateSafe = AutoStateSafe.DRIVE_BACK
                self.autoTimer.reset()
                self.autoTimer.start()
        
        elif self.autoStateSafe == AutoStateSafe.DRIVE_BACK:
            #self.DriveStraight(self.drive.frontLeftMotor, 10, -.5)
            targetReached = self.DriveStraight(self.drive.frontLeftMotor.getSelectedSensorPosition(), 9.5, .5)
            if targetReached:
                self.autoStateSafe = AutoStateSafe.WAIT

                self.autoTimer.reset()
                self.autoTimer.start()

                for talon in self.drive.talons:
                    talon.setSelectedSensorPosition(0)

        elif self.autoStateSafe == AutoStateSafe.WAIT:
            self.DriveStraight(self.drive.frontLeftMotor.getSelectedSensorPosition(), 2, 0.2)
            if self.autoTimer.hasPeriodPassed(0.5):
                self.autoStateSafe = AutoStateSafe.DEPLOY_CHUTE

                self.autoTimer.reset()
                self.autoTimer.start()

                for talon in self.drive.talons:
                    talon.setSelectedSensorPosition(0)
            
        elif self.autoStateSafe == AutoStateSafe.DEPLOY_CHUTE:
            self.chute.OpenHatch()
            self.chute.BottomMotorStart(1)
            self.chute.BallTicklerStart(1)

            if self.autoTimer.hasPeriodPassed(3):
                self.chute.CloseHatch()
                self.chute.ballTickler.stopMotor()
                self.chute.BottomMotorStop()

                self.autoStateSafe = AutoStateSafe.DRIVE_LEFT
                
                for talon in self.drive.talons:
                    talon.setSelectedSensorPosition(0)

        elif self.autoStateSafe == AutoStateSafe.DRIVE_LEFT:
            targetReached = self.DriveSideways(self.drive.frontLeftMotor.getSelectedSensorPosition(), 7, .5)
            if targetReached:
                self.autoStateSafe = AutoStateSafe.DRIVE_FORWARD

        elif self.autoStateSafe == AutoStateSafe.DRIVE_FORWARD:
            targetReached = self.DriveStraight(self.drive.frontLeftMotor.getSelectedSensorPosition(), 10, -.5)
            if targetReached:
                self.autoStateSafe = AutoStateSafe.END_AUTO

        elif self.autoStateSafe == AutoStateSafe.END_AUTO:
            for talon in self.drive.talons:
                talon.stopMotor()
                talon.setSelectedSensorPosition(0)


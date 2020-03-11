from enum import Enum

import wpilib

from drive import InfiniteRechargeDrive
from ballchute import BallChute
import robotmap



class AutoStateTrench(Enum):
    DRIVE_BACK = 0
    WAIT = 1
    DRIVE_MORE = 9
    DEPLOY_CHUTE = 2
    DEPLOY_CHUTE2 = 12
    DRIVE_LEFT = 3
    DRIVE_RIGHT = 11
    DRIVE_FORWARD = 4
    END_AUTO = 5
    CLEAR_LINE = 6
    WAIT_CLEAR = 7
    RAM = 8
    WAIT2 = 10
    WAIT3 = 13
    WAIT4 = 14

class AutoChuteTrench():
    def __init__(self, drive: InfiniteRechargeDrive, chute: BallChute):
        self.autoTimer = wpilib.Timer()
        self.autoTimer.start()

        self.drive = drive
        self.BallChute = chute

        self.chute = chute

        self.autoStateTrench = AutoStateTrench.CLEAR_LINE

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
        if self.autoStateTrench == AutoStateTrench.CLEAR_LINE:
            targetReached = self.DriveStraight(self.drive.frontLeftMotor.getSelectedSensorPosition(), 0.5, -0.5)
            if targetReached:
                self.autoStateTrench = AutoStateTrench.WAIT_CLEAR
                self.autoTimer.reset()
                self.autoTimer.start()

                for talon in self.drive.talons:
                    talon.setSelectedSensorPosition(0)

        elif self.autoStateTrench == AutoStateTrench.WAIT_CLEAR:
            if self.autoTimer.hasPeriodPassed(0.5):
                self.autoStateTrench = AutoStateTrench.DRIVE_BACK
                self.autoTimer.reset()
                self.autoTimer.start()
        
        elif self.autoStateTrench == AutoStateTrench.DRIVE_BACK:
            targetReached = self.DriveStraight(self.drive.frontLeftMotor.getSelectedSensorPosition(), 10, 0.5)
            if targetReached:
                self.autoStateTrench = AutoStateTrench.WAIT2

                self.autoTimer.reset()
                self.autoTimer.start()

                for talon in self.drive.talons:
                    talon.setSelectedSensorPosition(0)

        elif self.autoStateTrench == AutoStateTrench.WAIT2:
            if self.autoTimer.hasPeriodPassed(1):
                self.autoStateTrench = AutoStateTrench.DRIVE_MORE
                self.autoTimer.reset()
                self.autoTimer.start()


        elif self.autoStateTrench == AutoStateTrench.DRIVE_MORE:
            self.drive.drive.driveCartesian(0, 0.3, 0)
            if self.autoTimer.hasPeriodPassed(1):
                self.autoStateTrench = AutoStateTrench.WAIT
                self.autoTimer.reset()
                self.autoTimer.start()

                for talon in self.drive.talons:
                    talon.setSelectedSensorPosition(0)

        elif self.autoStateTrench == AutoStateTrench.WAIT:
            
            if self.autoTimer.hasPeriodPassed(0.5):
                self.autoStateTrench = AutoStateTrench.DEPLOY_CHUTE

                self.autoTimer.reset()
                self.autoTimer.start()
            
        elif self.autoStateTrench == AutoStateTrench.DEPLOY_CHUTE:
            self.drive.drive.driveCartesian(0, 0.3, 0)
            self.chute.OpenHatch()
            self.chute.BottomMotorStart(1)
            self.chute.BallTicklerStart(1)

            if self.autoTimer.hasPeriodPassed(1):
                self.chute.CloseHatch()
                self.chute.ballTickler.stopMotor()
                self.chute.BottomMotorStop()

                self.autoStateTrench = AutoStateTrench.DRIVE_RIGHT
                
                for talon in self.drive.talons:
                    talon.setSelectedSensorPosition(0)
                    talon.stopMotor()


        elif self.autoStateTrench == AutoStateTrench.DRIVE_RIGHT:
            targetReached = self.DriveSideways(self.drive.frontLeftMotor.getSelectedSensorPosition(), 8, -.5)
            if targetReached:
                self.autoStateTrench = AutoStateTrench.WAIT3

        elif self.autoStateTrench == AutoStateTrench.WAIT3:
            
            if self.autoTimer.hasPeriodPassed(0.5):
                self.autoStateTrench = AutoStateTrench.DRIVE_FORWARD

                self.autoTimer.reset()
                self.autoTimer.start()


        elif self.autoStateTrench == AutoStateTrench.DRIVE_LEFT:
            targetReached = self.DriveSideways(self.drive.frontLeftMotor.getSelectedSensorPosition(), 7, .5)
            if targetReached:
                self.autoStateTrench = AutoStateTrench.END_AUTO

        elif self.autoStateTrench == AutoStateTrench.DRIVE_FORWARD:
            targetReached = self.DriveStraight(self.drive.frontLeftMotor.getSelectedSensorPosition(), 8, -.5)
            if targetReached:
                self.autoStateTrench = AutoStateTrench.WAIT4

        elif self.autoStateTrench == AutoStateTrench.WAIT4:
            
            if self.autoTimer.hasPeriodPassed(0.5):
                self.autoStateTrench = AutoStateTrench.DEPLOY_CHUTE2

                self.autoTimer.reset()
                self.autoTimer.start()

        elif self.autoStateTrench == AutoStateTrench.DEPLOY_CHUTE2:
            targetReached = self.drive.drive.driveCartesian(0, 0.2, 0)
            self.chute.OpenHatch()
            self.chute.DeployRake()
            self.chute.BottomMotorStart(.5)
            self.chute.RakeMotorStart(.5)

            if self.autoTimer.hasPeriodPassed(4.5):
                self.chute.CloseHatch()
                self.chute.ballTickler.stopMotor()
                self.chute.BottomMotorStop()
                self.chute.RakeMotorStop()

                self.autoStateTrench = AutoStateTrench.END_AUTO
                
                for talon in self.drive.talons:
                    talon.setSelectedSensorPosition(0)
                    talon.stopMotor()

        elif self.autoStateTrench == AutoStateTrench.END_AUTO:
            for talon in self.drive.talons:
                talon.stopMotor()
                talon.setSelectedSensorPosition(0)


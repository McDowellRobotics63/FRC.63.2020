from enum import Enum
import wpilib
from drive import InfiniteRechargeDrive
from ballchute import BallChute
import robotmap

class AutoStateLeft(Enum):
    DRIVE_LEFT = 0
    WAIT1 = 1
    DRIVE_BACK = 2
    WAIT2 = 3
    DEPLOY_HATCH = 4
    WAIT3 = 5
    STOW_HATCH = 6
    WAIT4 = 7
    DRIVE_FORWARD = 8
    END_AUTO = 9
    CLEAR_LINE = 10
    WAIT_CLEAR = 11

class AutoChuteLeft():
    def __init__(self, drive: InfiniteRechargeDrive, chute: BallChute, logger):
        self.autoTimer = wpilib.Timer()
        self.autoTimer.start()
        self.drive = drive
        self.chute = chute
        self.autoStateLeft = AutoStateLeft.CLEAR_LINE
        self.logger = logger

    def UnitsToFeet(self, units):
        return units * robotmap.FEET_PER_UNIT

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

    def Iterate(self):
        if self.autoStateLeft == AutoStateLeft.CLEAR_LINE:
            self.logger.info("Straight")
            targetReached = self.DriveStraight(self.drive.frontLeftMotor.getSelectedSensorPosition(), 0.5, -0.5)
            if targetReached:
                self.autoStateLeft = AutoStateLeft.WAIT_CLEAR
                self.autoTimer.reset()
                self.autoTimer.start()

                for talon in self.drive.talons:
                    talon.setSelectedSensorPosition(0)

        elif self.autoStateLeft == AutoStateLeft.WAIT_CLEAR:
            self.logger.info("Wait")
            if self.autoTimer.hasPeriodPassed(0.5):
                self.autoStateLeft = AutoStateLeft.DRIVE_LEFT
                self.autoTimer.reset()
                self.autoTimer.start()

                for talon in self.drive.talons:
                    talon.setSelectedSensorPosition(0)
        
        if self.autoStateLeft == AutoStateLeft.DRIVE_LEFT:
            self.logger.info("Left")
            targetReached = self.DriveSideways(self.drive.frontLeftMotor.getSelectedSensorPosition(), 1, -.5)
            if targetReached:
                self.autoStateLeft = AutoStateLeft.WAIT1

                self.autoTimer.reset()
                self.autoTimer.start()

                for talon in self.drive.talons:
                    talon.setSelectedSensorPosition(0)

        elif self.autoStateLeft == AutoStateLeft.WAIT1:
            if self.autoTimer.hasPeriodPassed(.25):
                self.autoStateLeft = AutoStateLeft.DRIVE_BACK

                self.autoTimer.reset()
                self.autoTimer.start()

        elif self.autoStateLeft == AutoStateLeft.DRIVE_BACK:
            targetReached = self.DriveStraight(self.drive.frontLeftMotor.getSelectedSensorPosition(), 10, 0.5)
            if targetReached:
                self.autoStateLeft = AutoStateLeft.WAIT2
                self.autoTimer.reset()
                self.autoTimer.start()

        elif self.autoStateLeft == AutoStateLeft.WAIT2:

            if self.autoTimer.hasPeriodPassed(1):
                self.autoStateLeft = AutoStateLeft.DEPLOY_HATCH
                self.autoTimer.reset()
                self.autoTimer.start()

        elif self.autoStateLeft == AutoStateLeft.DEPLOY_HATCH:
            self.chute.OpenHatch()
            self.chute.BallTicklerStart(self.chute.motorPercent)
            self.chute.BottomMotorStart(self.chute.motorPercent)

            self.autoStateLeft = AutoStateLeft.WAIT3
            self.autoTimer.reset()
            self.autoTimer.start()

        elif self.autoStateLeft == AutoStateLeft.WAIT3:
            if self.autoTimer.hasPeriodPassed(3):
                self.autoStateLeft = AutoStateLeft.STOW_HATCH
                self.autoTimer.reset()
                self.autoTimer.start()    

        elif self.autoStateLeft == AutoStateLeft.STOW_HATCH:
            self.chute.CloseHatch()
            self.chute.BallTicklerStop()
            self.chute.BottomMotorStop()

            self.autoStateLeft = AutoStateLeft.DRIVE_FORWARD
            self.autoTimer.reset()
            self.autoTimer.start()
            
            for talon in self.drive.talons:
                talon.setSelectedSensorPosition(0)

        elif self.autoStateLeft == AutoStateLeft.DRIVE_FORWARD:
            targetReached = self.DriveStraight(self.drive.frontLeftMotor.getSelectedSensorPosition(), 12, -0.5)
            if targetReached:
                self.autoStateLeft = AutoStateLeft.END_AUTO

        elif self.autoStateLeft == AutoStateLeft.END_AUTO:
            for talon in self.drive.talons:
                talon.stopMotor()
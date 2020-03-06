from enum import Enum
import wpilib
from drive import InfiniteRechargeDrive
from ballchute import BallChute
import robotmap

class AutoStateRight(Enum):
    DRIVE_RIGHT = 0
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

class AutoChuteRight():
    def __init__(self, drive: InfiniteRechargeDrive, chute: BallChute):
        self.autoTimer = wpilib.Timer()
        self.autoTimer.start()
        self.drive = drive
        self.chute = chute
        self.autoStateRight = AutoStateRight.CLEAR_LINE

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
        if self.autoStateRight == AutoStateRight.CLEAR_LINE:
            targetReached = self.DriveStraight(self.drive.frontLeftMotor.getSelectedSensorPosition(), 0.5, -0.5)
            if targetReached:
                self.autoStateRight = AutoStateRight.WAIT_CLEAR
                self.autoTimer.reset()
                self.autoTimer.start()

                for talon in self.drive.talons:
                    talon.setSelectedSensorPosition(0)

        elif self.autoStateRight == AutoStateRight.WAIT_CLEAR:
            if self.autoTimer.hasPeriodPassed(0.5):
                self.autoStateRight = AutoStateRight.DRIVE_RIGHT
                self.autoTimer.reset()
                self.autoTimer.start()

        if self.autoStateRight == AutoStateRight.DRIVE_RIGHT:
            targetReached = self.DriveSideways(self.drive.frontLeftMotor.getSelectedSensorPosition(), 2, .5)
            if targetReached:
                self.autoStateRight = AutoStateRight.WAIT1

                self.autoTimer.reset()
                self.autoTimer.start()

        elif self.autoStateRight == AutoStateRight.WAIT1:
            if self.autoTimer.hasPeriodPassed(.5):
                self.autoStateRight = AutoStateRight.DRIVE_BACK

                self.autoTimer.reset()
                self.autoTimer.start()

        elif self.autoStateRight == AutoStateRight.DRIVE_BACK:
            targetReached = self.DriveStraight(self.drive.frontLeftMotor.getSelectedSensorPosition(), 10, 0.5)
            if targetReached:
                self.autoStateRight = AutoStateRight.WAIT2
                self.autoTimer.reset()
                self.autoTimer.start()

        elif self.autoStateRight == AutoStateRight.WAIT2:

            if self.autoTimer.hasPeriodPassed(2):
                self.autoStateRight = AutoStateRight.DEPLOY_HATCH
                self.autoTimer.reset()
                self.autoTimer.start()

        elif self.autoStateRight == AutoStateRight.DEPLOY_HATCH:
            self.chute.OpenHatch()
            self.chute.BallTicklerStart(self.chute.motorPercent)
            self.chute.BottomMotorStart(self.chute.motorPercent)

            self.autoStateRight = AutoStateRight.WAIT3
            self.autoTimer.reset()
            self.autoTimer.start()

        elif self.autoStateRight == AutoStateRight.WAIT3:
            if self.autoTimer.hasPeriodPassed(5):
                self.autoStateRight = AutoStateRight.STOW_HATCH
                self.autoTimer.reset()
                self.autoTimer.start()    

        elif self.autoStateRight == AutoStateRight.STOW_HATCH:
            self.chute.CloseHatch()
            self.chute.BallTicklerStop()
            self.chute.BottomMotorStop()

            self.autoStateRight = AutoStateRight.DRIVE_FORWARD
            self.autoTimer.reset()
            self.autoTimer.start()

            for talon in self.drive.talons:
                talon.setSelectedSensorPosition(0)

        elif self.autoStateRight == AutoStateRight.DRIVE_FORWARD:
            targetReached = self.DriveStraight(self.drive.frontLeftMotor.getSelectedSensorPosition(), 12, -0.5)
            if targetReached:
                self.autoStateRight = AutoStateRight.END_AUTO

        elif self.autoStateRight == AutoStateRight.END_AUTO:
            for talon in self.drive.talons:
                talon.stopMotor()
from enum import Enum
import wpilib
from drive import InfiniteRechargeDrive
from ballchute import BallChute
import robotmap
from autochute1 import AutoChute

class AutoState2(Enum):
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

class AutoChute2():
    def __init__(self, drive: InfiniteRechargeDrive, chute: BallChute):
        self.autoTimer = wpilib.Timer()
        self.autoTimer.start()
        self.drive = drive
        self.chute = chute
        self.autoState2 = AutoState2.DRIVE_LEFT

    def DriveLeft(self, speed, distance):
        distanceTraveled = 0
        while abs(distanceTraveled) < distance:
            distanceTraveled = self.drive.frontLeftMotor.getSelectedSensorPosition() * robotmap.FEET_PER_UNIT
            self.drive.drive.driveCartesian(speed, 0, 0)

        if abs(distanceTraveled) >= distance:
            for talon in self.drive.talons:
                talon.stopMotor()

    def Iterate(self):
        if self.autoState2 == AutoState2.DRIVE_LEFT:
            self.DriveLeft(.5, 10)
            self.autoState2 = AutoState2.WAIT1

            self.autoTimer.reset()
            self.autoTimer.start()

        elif self.AutoState2 == AutoState2.WAIT1:
            if self.autoTimer.hasPeriodPassed(.5):
                self.autoState2 = AutoState2.DRIVE_BACK

                self.autoTimer.reset()
                self.autoTimer.start()

        elif self.autoState2 == AutoState2.DRIVE_BACK:
            targetReached = AutoChute.DriveStraight(self.drive.frontLeftMotor.getSelectedSensorPosition(), 10, -0.5)
            if targetReached:
                self.autoState2 = AutoState2.WAIT2
                self.autoTimer.reset()
                self.autoTimer.start()

        elif self.autoState2 == AutoState2.WAIT2:

            if self.autoTimer.hasPeriodPassed(2):
                self.autoState2 = AutoState2.STOW_HATCH
                self.autoTimer.reset()
                self.autoTimer.start()

        elif self.autoState2 == AutoState2.STOW_HATCH:

            BallChute.CloseHatch()
            self.autoState2 = AutoState2.DRIVE_FORWARD
            self.autoTimer.reset()
            self.autoTimer.start()
        elif self.autoState2 == AutoState2.DRIVE_FORWARD:
            AutoChute.DriveStraight(12, .5)
            self.AutoState2 = AutoState2.END_AUTO

        elif self.autoState2 == AutoState2.END_AUTO:
            for talon in self.drive.talons:
                talon.stopMotor()




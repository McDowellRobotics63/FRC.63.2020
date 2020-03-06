from enum import Enum

import wpilib

from drive import InfiniteRechargeDrive
from ballchute import BallChute
import robotmap

class AutoState(Enum):
    DRIVE_FORWARD = 0
    LITERALLY_NOTHING = 1

class AutoChuteClear():
    def __init__(self, drive: InfiniteRechargeDrive, chute: BallChute):
        self.autoTimer = wpilib.Timer()
        self.autoTimer.start()

        self.drive = drive
        self.BallChute = chute

        self.chute = chute

        self.autoState = AutoState.DRIVE_FORWARD

        for talon in self.drive.talons:
            talon.setSelectedSensorPosition(0)


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
        if self.autoState == AutoState.DRIVE_FORWARD:
            targetReached = self.DriveStraight(self.drive.frontLeftMotor.getSelectedSensorPosition(), 4, -0.5)
            if targetReached:
                self.autoState = AutoState.LITERALLY_NOTHING

                self.autoTimer.reset()
                self.autoTimer.start()

                for talon in self.drive.talons:
                    talon.setSelectedSensorPosition(0)

        elif self.autoState == AutoState.LITERALLY_NOTHING:
            for talon in self.drive.talons:
                talon.stopMotor()

                pass



from wpilib.command import Command
from wpilib import Timer
from wpilib import SmartDashboard

import math

import robotmap

class AutoRotate(Command):
    def __init__(self, robot, d):
        super().__init__()
        self.robot = robot
        self.requires(robot.drive)

        self.setpoint = d #inches
        self.total_timer = Timer()

    # Called just before this Command runs the first time
    def initialize(self):
        self.total_timer.reset()
        self.total_timer.start()
        self.robot.drive.resetEncoders()
        self.robot.drive.configGains(
            robotmap.DRIVE_F, robotmap.DRIVE_P, robotmap.DRIVE_I, robotmap.DRIVE_D,
            robotmap.DRIVE_RIZONE, robotmap.DRIVE_RCRUISE, robotmap.DRIVE_RACCEL)
        self.setpoint = self.degrees_to_inches(self.setpoint)
        self.robot.drive.setMotionMagicLeft(self.setpoint)
        self.robot.drive.setMotionMagicRight(-self.setpoint)

    # Make this return true when this Command no longer needs to run execute()
    def isFinished(self):
        returnval = False
        if self.total_timer > 5.0:
            returnval = True
        elif self.total_timer > 1.0:
            if self.robot.drive.isMotionMagicNearTarget():
                returnval = True
        return returnval

    # Called once after isFinished returns true
    def end(self):
        self.robot.drive.stop()

    # Called when another command which requires one or more of the same
    # subsystems is scheduled to run
    def interrupted(self):
        self.robot.drive.stop()

    @staticmethod
    def degrees_to_inches(degrees):
        return degrees/180*math.pi*(SmartDashboard.getNumber("drive_track", 0)/2)

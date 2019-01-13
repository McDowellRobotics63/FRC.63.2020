from wpilib.command import Command
from wpilib import Timer

import robotmap

class AutoDriveFixedDistance(Command):
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
            robotmap.DRIVE_IZONE, robotmap.DRIVE_CRUISE, robotmap.DRIVE_ACCEL)
        self.robot.drive.setMotionMagicLeft(self.setpoint)
        self.robot.drive.setMotionMagicRight(self.setpoint)

    # Make this return true when this Command no longer needs to run execute()
    def isFinished(self):
        retval = False
        if self.total_timer.get() > 10.0:
            retval = True
        elif self.total_timer.get() > 1.0:
            if self.robot.drive.isMotionMagicNearTarget():
                retval = True
        return retval

    # Called once after isFinished returns true
    def end(self):
        self.robot.drive.stop()

    # Called when another command which requires one or more of the same
    # subsystems is scheduled to run
    def interrupted(self):
        self.robot.drive.stop()

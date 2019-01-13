from wpilib.command import Command
from wpilib import Timer

import robotmap

class AutoSetLiftPosition(Command):
    def __init__(self, robot, d):
        super().__init__()
        self.robot = robot
        self.requires(robot.lift)

        self.m_setpoint = d #inches
        self.total_timer = Timer()

    # Called just before this Command runs the first time
    def initialize(self):
        self.total_timer.reset()
        self.total_timer.start()
        self.robot.lift.setMotionMagicSetpoint(self.m_setpoint)

    # Make this return true when this Command no longer needs to run execute()
    def isFinished(self):
        returnval = False
        if self.total_timer.get() > 1.0:
            if self.robot.lift.isMotionMagicNearTarget():
                returnval = True
        elif self.total_timer > 9.0:
            returnval = True

        return returnval

    # Called when another command which requires one or more of the same
    # subsystems is scheduled to run
    def interrupted(self):
        self.robot.lift.hold()
        self.robot.debug.Stop()

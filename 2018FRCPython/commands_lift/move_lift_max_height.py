from wpilib.command import Command
from wpilib import Timer
from wpilib import SmartDashboard

import robotmap

class MoveLiftMaxHeight(Command):
    def __init__(self, robot):
        super().__init__()
        self.robot = robot
        self.requires(robot.lift)

        self.total_timer = Timer()

    # Called just before this Command runs the first time
    def initialize(self):
        self.robot.lift.setMotionMagicSetpoint(SmartDashboard.getNumber("max_lift_inches", 79))
        self.total_timer.reset()
        self.total_timer.start()

    # Make this return true when this Command no longer needs to run execute()
    def isFinished(self):
        return self.robot.lift.isMotionMagicNearTarget() or self.total_timer.get() > 9.0

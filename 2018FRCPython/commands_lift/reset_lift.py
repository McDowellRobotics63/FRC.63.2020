from wpilib.command import Command

import robotmap

class ResetLift(Command):
    def __init__(self, robot):
        super().__init__()
        self.robot = robot
        self.requires(robot.lift)

    # Called just before this Command runs the first time
    def initialize(self):
        self.robot.lift.setPercentOutput(-0.1)

    # Make this return true when this Command no longer needs to run execute()
    def isFinished(self):
        return self.robot.lift.isBottomedOut()

    # Called once after isFinished returns true
    def end(self):
        self.robot.lift.stop()
        self.robot.lift.resetEncoder()

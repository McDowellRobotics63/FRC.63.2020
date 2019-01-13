from wpilib.command import Command
from wpilib import Timer

from subsystems.liftsubsystem import Direction

import robotmap

class MoveLiftOneBoxHeight(Command):
    def __init__(self, robot, d):
        super().__init__()
        self.robot = robot
        self.requires(robot.lift)

        self.total_timer = Timer()
        self.direction = d

    # Called just before this Command runs the first time
    def initialize(self):
        self.total_timer.reset()
        self.total_timer.start()

    # Called repeatedly when this Command is scheduled to run
    def execute(self):
        setpoint = self.robot.lift.getCurrentSetpoint()
        if self.direction == Direction.UP:
            setpoint = setpoint + robotmap.BOX_HEIGHT_INCHES
        elif self.direction == Direction.DOWN:
            setpoint = setpoint - robotmap.BOX_HEIGHT_INCHES

        self.robot.lift.setMotionMagicSetpoint(setpoint)

    # Make this return true when this Command no longer needs to run execute()
    def isFinished(self):
        return True

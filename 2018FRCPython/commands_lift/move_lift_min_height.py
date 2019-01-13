from wpilib.command import Command
from wpilib import Timer

class MoveLiftMinHeight(Command):
    def __init__(self, robot):
        super().__init__()
        self.robot = robot
        self.requires(robot.lift)

        self.total_timer = Timer()

    # Called just before this Command runs the first time
    def initialize(self):
        self.robot.lift.setMotionMagicSetpoint(0)

        self.total_timer.reset()
        self.total_timer.start()

    # Make this return true when this Command no longer needs to run execute()
    def isFinished(self):
        return self.robot.lift.isMotionMagicNearTarget() or self.total_timer.get() > 5.0

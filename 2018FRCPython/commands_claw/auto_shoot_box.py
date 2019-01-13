
from wpilib.command import Command
from wpilib import Timer

import robotmap

class AutoShootBox(Command):
    def __init__(self, robot):
        super().__init__()
        self.robot = robot

        self.requires(robot.claw)
        self.total_timer = Timer()

    # Called just before this Command runs the first time
    def initialize(self):
        self.total_timer.reset()
        self.total_timer.start()

    # Called repeatedly when this Command is scheduled to run
    def execute(self):
        self.robot.claw.setSpeed(robotmap.BOX_OUT_SPEED)
        self.robot.claw.close()

    # Make this return true when this Command no longer needs to run execute()
    def isFinished(self):
        return self.total_timer.get() > 0.25

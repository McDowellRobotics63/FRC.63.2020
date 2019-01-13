from wpilib.command import Command

import robotmap

class ClimbUp(Command):
    def __init__(self, robot):
        super().__init__()
        self.robot = robot
        self.requires(robot.climb)
        self.requires(robot.claw)

    # Called repeatedly when this Command is scheduled to run
    def execute(self):
        self.robot.climb.armRetract()
        self.robot.climb.pullyclimb(robotmap.CLIMB_UP_SPEED)
        self.robot.claw.close()

    # Make this return true when this Command no longer needs to run execute()
    def isFinished(self):
        return True

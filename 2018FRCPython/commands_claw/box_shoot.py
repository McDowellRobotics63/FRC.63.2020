from wpilib.command import Command

import robotmap

class BoxShoot(Command):
    def __init__(self, robot):
        super().__init__()
        self.robot = robot

    # Called repeatedly when this Command is scheduled to run
    def execute(self):
        self.robot.claw.setSpeed(robotmap.BOX_OUT_SPEED)
        self.robot.claw.open()

    # Make this return true when this Command no longer needs to run execute()
    def isFinished(self):
        return True

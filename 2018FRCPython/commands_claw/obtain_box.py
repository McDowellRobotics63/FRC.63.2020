from wpilib.command import Command

import robotmap

class ObtainBox(Command):
    def __init__(self, robot):
        super().__init__()
        self.robot = robot
        self.requires(self.robot.claw)

    # Called just before this Command runs the first time
    def initialize(self):
        self.robot.claw.close()
        self.robot.claw.setSpeed(0)

    # Called repeatedly when this Command is scheduled to run
    def execute(self):
        self.robot.claw.setSpeed(robotmap.BOX_IN_SPEED)
        if self.robot.claw.boxIsClose():
            self.robot.claw.close()
        else:
            self.robot.claw.open()

    # Make this return true when this Command no longer needs to run execute()
    def isFinished(self):
        return self.robot.claw.boxIsReallyClose()

    # Called once after isFinished returns true
    def end(self):
        self.robot.claw.close()
        self.robot.claw.setSpeed(0)

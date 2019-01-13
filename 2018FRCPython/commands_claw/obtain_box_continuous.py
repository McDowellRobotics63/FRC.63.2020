from wpilib.command import Command

import robotmap

class ObtainBoxContinuous(Command):
    def __init__(self, robot):
        super().__init__()
        self.robot = robot
        self.requires(robot.claw)
        self.setInterruptible(True)

    # Called just before this Command runs the first time
    def initialize(self):
        self.robot.claw.close()
        self.robot.claw.setSpeed(0)

    # Called repeatedly when this Command is scheduled to run
    def execute(self):
        if self.robot.claw.boxIsReallyClose():
            self.robot.claw.setSpeed(0)
        else:
            self.robot.claw.setSpeed(robotmap.BOX_IN_SPEED)
            if self.robot.claw.boxIsClose():
                self.robot.claw.close()
            else:
                self.robot.claw.open()

    # Make this return true when this Command no longer needs to run execute()
    def isFinished(self):
        return False

    # Called once after isFinished returns true
    def end(self):
        self.robot.claw.close()
        self.robot.claw.setSpeed(0)

    # Called when another command which requires one or more of the same
    # subsystems is scheduled to run
    def interrupted(self):
        self.robot.claw.close()
        self.robot.claw.setSpeed(0)

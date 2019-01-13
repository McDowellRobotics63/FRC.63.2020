from wpilib.command import Command

import robotmap

class ClawAndLift(Command):
    def __init__(self, robot):
        super().__init__()
        self.robot = robot
        self.requires(robot.claw)
        self.requires(robot.lift)
        self.setInterruptible(True)

    # Called just before this Command runs the first time
    def initialize(self):
        self.robot.claw.close()
        self.robot.claw.setSpeed(0)

    # Called repeatedly when this Command is scheduled to run
    def execute(self):
        if self.robot.claw.boxIsReallyClose(): 
            if self.robot.lift.getCurrentPosition() < robotmap.BOX_HEIGHT_INCHES:
                self.robot.lift.setMotionMagicSetpoint(robotmap.BOX_HEIGHT_INCHES)
            self.robot.claw.setSpeed(0)
        else:
            self.robot.claw.setSpeed(robotmap.BOX_IN_SPEED)
            if self.robot.claw.boxIsClose():
                self.robot.claw.close()
            else:
                self.robot.claw.open()

        if self.robot.lift.isMotionMagicNearTarget():
            if self.robot.lift.getCurrentPosition() > 60:
                self.robot.lift.stop()
            else:
                self.robot.lift.hold()

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

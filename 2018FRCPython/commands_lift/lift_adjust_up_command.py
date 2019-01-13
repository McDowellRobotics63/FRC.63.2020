from wpilib.command import Command

import robotmap

class LiftAdjustUpCommand(Command):
    def __init__(self, robot):
        super().__init__()
        self.robot = robot
        self.requires(robot.lift)

    # Called repeatedly when this Command is scheduled to run
    def execute(self):
        self.robot.lift.setMotionMagicSetpoint(
            self.robot.lift.getCurrentSetpoint() + 
            robotmap.MAX_LIFT_ADJUST_SPEED * 0.02)

    # Make this return true when this Command no longer needs to run execute()
    def isFinished(self):
        return True

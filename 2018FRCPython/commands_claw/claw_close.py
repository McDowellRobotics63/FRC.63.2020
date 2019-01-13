from wpilib.command import Command

class ClawClose(Command):
    def __init__(self, robot):
        super().__init__()
        self.robot = robot
        self.requires(robot.claw)

    # Called repeatedly when this Command is scheduled to run
    def execute(self):
        self.robot.claw.close()

    # Make this return true when this Command no longer needs to run execute()
    def isFinished(self):
        return True

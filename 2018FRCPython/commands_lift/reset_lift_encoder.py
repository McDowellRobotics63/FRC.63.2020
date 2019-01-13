from wpilib.command import Command

class ResetLiftEncoder(Command):
    def __init__(self, robot):
        super().__init__()
        self.robot = robot
        self.requires(robot.lift)

    # Called repeatedly when this Command is scheduled to run
    def execute(self):
        self.robot.lift.initSubsystemAuto()

    # Make this return true when this Command no longer needs to run execute()
    def isFinished(self):
        return True

from wpilib.command import Command

class ClimbStop(Command):
    def __init__(self, robot):
        super().__init__()
        self.robot = robot
        self.requires(robot.climb)
        self.requires(robot.claw)
        self.setInterruptible(True)

    # Called repeatedly when this Command is scheduled to run
    def execute(self):
        self.robot.climb.pullyclimb(0)
        self.robot.claw.close()

    # Make this return true when this Command no longer needs to run execute()
    def isFinished(self):
        return False

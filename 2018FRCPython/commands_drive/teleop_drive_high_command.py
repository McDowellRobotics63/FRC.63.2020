from wpilib.command import Command

class TeleopDriveHighCommand(Command):
    def __init__(self, robot):
        super().__init__()
        self.robot = robot
        self.requires(robot.drive)
        self.setInterruptible(True)

    # Called repeatedly when this Command is scheduled to run
    def execute(self):
        self.robot.drive.shiftHigh()
        self.robot.drive.teleDrive(
            self.robot.oi.controller1.LeftStickY(),
            self.robot.oi.controller1.RightStickX()
            )

    # Make this return true when this Command no longer needs to run execute()
    def isFinished(self):
        return False

    # Called once after isFinished returns true
    def end(self):
        self.robot.drive.stop()

    # Called when another command which requires one or more of the same
    # subsystems is scheduled to run
    def interrupted(self):
        self.robot.drive.stop()

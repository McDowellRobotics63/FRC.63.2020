
import wpilib

from wpilib import Timer

class Auto1():

    CLAW_DEPLOY = 1
    DRIVE_OFF_PLATFORM = 2
    LIFT_DEPLOY = 3
    def __init__(self, _robot):
        self.robot = _robot
        self.timer = Timer()

    def init(self):
        self.state = 0
        self.timer.start()

    def iterate(self):
        if self.state == 0:
            self.state = 1
        elif self.state == 1:
            self.state = 2
            self.robot.robot_drive.tankDrive(0, 1.0)
        elif self.state == 2:
            self.state = 3
        else:
            pass
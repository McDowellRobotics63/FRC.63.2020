import wpilib

from drive import InfiniteRechargeDrive
from ballchute import BallChute
from colorwheel import ColorWheel
from climb import Climb
from autochute import AutoChute

from xboxcontroller import XBox
import robotmap

class MyRobot(wpilib.TimedRobot):
    def robotInit(self):
        self.timer = wpilib.Timer()

        self.compressor = wpilib.Compressor(robotmap.PCM_ID)
        self.compressor.start()

        self.pilot = XBox(0)
        self.copilot = XBox(1)

        self.drive = InfiniteRechargeDrive()
        self.ballChute = BallChute()
        self.colorWheel = ColorWheel()
        self.climb = Climb()

        

    def disabledInit(self):
        self.logger.info("Disabled::Init()")

    def disabledPeriodic(self):
        if self.timer.hasPeriodPassed(1):
            self.logger.info("Disabled::Periodic()")

    def autonomousInit(self):
        self.drive.Config()
        self.auto = AutoChute(self.drive, self.ballChute)

    def autonomousPeriodic(self):
        self.auto.Iterate()

    def teleopInit(self):
        self.drive.Config()

    def teleopPeriodic(self):
        self.drive.Iterate(self.pilot)
        self.ballChute.Iterate(self.copilot)
        self.colorWheel.Iterate(self.copilot)
        self.climb.Iterate(self.pilot)

if __name__ == "__main__":
    wpilib.run(MyRobot, physics_enabled=True)
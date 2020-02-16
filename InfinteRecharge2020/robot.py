import wpilib

from drive import InfiniteRechargeDrive
from ballchute import BallChute
from colorwheel import ColorWheel

from xboxcontroller import XBox
import robotmap

class MyRobot(wpilib.TimedRobot):
    def robotInit(self):
        self.compressor = wpilib.Compressor(robotmap.PCM_ID)
        self.compressor.start()

        self.pilot = XBox(0)
        self.copilot = XBox(1)

        self.drive = InfiniteRechargeDrive()
        self.ballChute = BallChute()
        self.colorWheel = ColorWheel()

    def disabledInit(self):
        pass

    def disabledPeriodic(self):
        pass

    def autonomousInit(self):
        pass

    def autonomousPeriodic(self):
        pass

    def teleopInit(self):
        pass

    def teleopPeriodic(self):
        self.drive.Iterate(self.pilot)
        self.ballChute.Iterate(self.copilot)
        self.colorWheel.Iterate(self.copilot)

if __name__ == "__main__":
    wpilib.run(MyRobot, physics_enabled=True)
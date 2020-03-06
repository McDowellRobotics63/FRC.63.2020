import wpilib
from wpilib import SmartDashboard
from wpilib import SendableChooser

from drive import InfiniteRechargeDrive
from ballchute import BallChute
from colorwheel import ColorWheel
from climb import Climb
#from autochute1 import AutoChute
from autochuteLeft import AutoChuteLeft
from autochuteRight import AutoChuteRight
from autochuteSafe import AutoChuteSafe
from autochuteClear import AutoChuteClear


from xboxcontroller import XBox
import robotmap

class MyRobot(wpilib.TimedRobot):
    def robotInit(self):
        self.timer = wpilib.Timer()

        wpilib.CameraServer.launch()

        #Initialize limit swithces
        self.autoChuteLeft = wpilib.DigitalInput(0)
        #self.autoChuteStraight = wpilib.DigitalInput(3)
        self.autoChuteRight = wpilib.DigitalInput(2)
        self.autoChuteSafe = wpilib.DigitalInput(1)

        self.compressor = wpilib.Compressor(robotmap.PCM_ID)
        self.compressor.setClosedLoopControl(True)

        self.pilot = XBox(0)
        self.copilot = XBox(1)

        self.drive = InfiniteRechargeDrive()
        self.ballChute = BallChute()
        self.colorWheel = ColorWheel()
        self.climb = Climb()

        #self.autochute1 = AutoChute(self.drive, self.ballChute)
        self.autochuteLeft = AutoChuteLeft(self.drive, self.ballChute, self.logger)
        self.autochuteRight = AutoChuteRight(self.drive, self.ballChute)
        self.autochuteSafe = AutoChuteSafe(self.drive, self.ballChute)
        self.autochuteClear = AutoChuteClear(self.drive, self.ballChute)

        self.auto_chooser = SendableChooser()
        self.auto_chooser.setDefaultOption('AutochuteClear', self.autochuteClear)
        self.auto_chooser.addOption('AutochuteLeft', self.autochuteLeft)
        self.auto_chooser.addOption('AutochuteRight', self.autochuteRight)
        self.auto_chooser.addOption("AutochuteSafe", self.autochuteSafe)

        SmartDashboard.putData("AutoChooser", self.auto_chooser)

    def disabledInit(self):
        self.logger.info("Disabled::Init()")

    def disabledPeriodic(self):
        if self.timer.hasPeriodPassed(1):
            self.logger.info("Disabled::Periodic()")

        self.colorWheel.Iterate(self.pilot)

    def autonomousInit(self):
        self.drive.Config()
        '''
        self.auto = AutoChute(self.drive, self.ballChute)
        self.autoL = AutoChuteLeft(self.drive, self.ballChute)
        self.autoR = AutoChuteRight(self.drive, self.ballChute)
        self.autoS = AutoChuteSafe(self.drive, self.ballChute)
        '''

        self.compressor.setClosedLoopControl(True)

        self.auto_selected = self.auto_chooser.getSelected()

        #self.autochute1.__init__(self.drive, self.ballChute)
        self.autochuteLeft.__init__(self.drive, self.ballChute, self.logger)
        self.autochuteRight.__init__(self.drive, self.ballChute)
        self.autochuteSafe.__init__(self.drive, self.ballChute)
        self.autochuteClear.__init__(self.drive, self.ballChute)


    def autonomousPeriodic(self):
        
        if self.autoChuteLeft.get() and self.autoChuteSafe.get() and self.autoChuteRight.get():
            self.autochuteClear.Iterate()
        elif self.autoChuteLeft.get():
            self.autochuteLeft.Iterate()
        elif self.autoChuteSafe.get():
            self.autochuteSafe.Iterate()
        elif self.autoChuteRight.get():
            self.autochuteRight.Iterate()
        else:
            #self.auto_selected.Iterate()
            pass
        
        #self.auto_selected.Iterate()

    def teleopInit(self):
        self.compressor.setClosedLoopControl(True)

        self.drive.Config()

    def teleopPeriodic(self):
        self.drive.Iterate(self.pilot)
        self.ballChute.Iterate(self.copilot)
        self.colorWheel.Iterate(self.pilot)
        self.climb.Iterate(self.pilot)
        self.ballChute.Reverse(self.copilot)
        self.ballChute.Dump(self.copilot)

if __name__ == "__main__":
    wpilib.run(MyRobot, physics_enabled=True)
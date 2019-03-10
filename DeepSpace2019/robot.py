
import wpilib

import robotmap

from wpilib import Compressor
from wpilib import sendablechooser
from wpilib import SmartDashboard

from robotsettings import DeepSpaceSettings
from xboxcontroller import XboxController
from drive import DeepSpaceDrive
from lift import DeepSpaceLift
from claw import DeepSpaceClaw
from harpoon import DeepSpaceHarpoon

from auto1 import Auto1
from auto2 import Auto2
from auto3 import Auto3

from robotenums import RobotMode

class MyRobot(wpilib.TimedRobot):

  robot_mode = RobotMode.AUTO

  def robotInit(self):
    self.timer = wpilib.Timer()
    self.timer.start()

    self.settings = DeepSpaceSettings()

    self.auto1 = Auto1(self, self.logger)
    self.auto2 = Auto2(self, self.logger)
    self.auto3 = Auto3(self, self.logger)

    self.auto_chooser = sendablechooser.SendableChooser()
    self.auto_chooser.setDefaultOption('Auto1', self.auto1)
    self.auto_chooser.addOption('Auto2', self.auto2)
    self.auto_chooser.addOption('Auto3', self.auto3)

    SmartDashboard.putData("AutoChooser", self.auto_chooser)
    
    if self.isReal():
      self.compressor = Compressor(robotmap.PCM2_CANID)
    else:
      self.compressor = Compressor(0)

    self.pilot_stick = XboxController(0, self.settings)
    self.copilot_stick = XboxController(1, self.settings)

    self.drive = DeepSpaceDrive(self.logger, self.settings)
    self.drive.init()

    self.lift = DeepSpaceLift(self.logger, self.settings)
    self.lift.init()

    self.claw = DeepSpaceClaw(self.logger, self.settings)
    self.claw.init()

    self.harpoon = DeepSpaceHarpoon(self.logger, self.settings)
    self.harpoon.init()


  def autonomousInit(self):
    self.robot_mode = RobotMode.AUTO
    self.logger.info("MODE: autonomousInit")

    self.auto_selected = self.auto_chooser.getSelected()
    self.pilot_stick.config()
    self.copilot_stick.config()
    self.drive.config(self.isSimulation())
    self.lift.config(self.isSimulation())
    self.claw.config(self.isSimulation())
    self.harpoon.config(self.isSimulation())

    self.auto_selected.init()

  def autonomousPeriodic(self):
    self.robot_mode = RobotMode.AUTO
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: autonomousPeriodic")

    self.auto_selected.iterate()

    self.drive.iterate(self.robot_mode, self.pilot_stick, self.copilot_stick)
    self.lift.iterate(self.robot_mode, self.isSimulation(), self.pilot_stick, self.copilot_stick)
    self.claw.iterate(self.robot_mode, self.pilot_stick, self.copilot_stick)
    self.harpoon.iterate(self.robot_mode, self.pilot_stick, self.copilot_stick)
  
  def teleopInit(self):
    self.robot_mode = RobotMode.TELE
    self.logger.info("MODE: teleopInit")
    self.pilot_stick.config()
    self.copilot_stick.config()
    self.drive.config(self.isSimulation())
    self.lift.config(self.isSimulation())
    self.claw.config(self.isSimulation())
    self.harpoon.config(self.isSimulation())

  def teleopPeriodic(self):
    self.robot_mode = RobotMode.TELE
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: teleopPeriodic")

    self.drive.iterate(self.robot_mode, self.pilot_stick, self.copilot_stick)
    self.lift.iterate(self.robot_mode, self.isSimulation(), self.pilot_stick, self.copilot_stick)
    self.claw.iterate(self.robot_mode, self.pilot_stick, self.copilot_stick)
    self.harpoon.iterate(self.robot_mode, self.pilot_stick, self.copilot_stick)

  def disabledInit(self):
    self.robot_mode = RobotMode.DISABLED
    self.logger.info("MODE: disabledInit")
    self.drive.disable()
    self.lift.disable()
    self.claw.disable()
    self.harpoon.disable()

  def disabledPeriodic(self):
    self.robot_mode = RobotMode.DISABLED
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: disabledPeriodic")

  def testInit(self):
    self.robot_mode = RobotMode.TEST
    self.logger.info("MODE: testInit")
    self.pilot_stick.config()
    self.copilot_stick.config()
    self.drive.config(self.isSimulation())
    self.lift.config(self.isSimulation())
    self.claw.config(self.isSimulation())
    self.harpoon.config(self.isSimulation())

  def testPeriodic(self):
    self.robot_mode = RobotMode.TEST
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: testPeriodic")

    self.drive.iterate(self.robot_mode, self.pilot_stick, self.copilot_stick)
    self.lift.iterate(self.robot_mode, self.isSimulation(), self.pilot_stick, self.copilot_stick)
    self.claw.iterate(self.robot_mode, self.pilot_stick, self.copilot_stick)
    self.harpoon.iterate(self.robot_mode, self.pilot_stick, self.copilot_stick)

if __name__ == "__main__":
    wpilib.run(MyRobot, physics_enabled=True)

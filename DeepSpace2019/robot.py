
import wpilib

import robotmap

from wpilib import Compressor

from drive import DeepSpaceDrive
from lift import DeepSpaceLift
from claw import DeepSpaceClaw
from harpoon import DeepSpaceHarpoon

class MyRobot(wpilib.TimedRobot):

  def robotInit(self):
    self.timer = wpilib.Timer()
    self.timer.start()

    if self.isReal():
      self.compressor = Compressor(robotmap.PCM2_CANID)
    else:
      self.compressor = Compressor(0)

    self.pilot_stick = wpilib.Joystick(0)
    self.copilot_stick = wpilib.Joystick(1)

    self.drive = DeepSpaceDrive(self.logger)
    self.drive.init()

    self.lift = DeepSpaceLift(self.logger)
    self.lift.init()

    self.claw = DeepSpaceClaw(self.logger)
    self.claw.init()

    self.harpoon = DeepSpaceHarpoon(self.logger)
    self.harpoon.init()

  def autonomousInit(self):
    self.logger.info("MODE: autonomousInit")
    self.drive.config(self.isSimulation())
    self.lift.config(self.isSimulation())
    self.claw.config(self.isSimulation())
    self.harpoon.config(self.isSimulation())

  def autonomousPeriodic(self):
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: autonomousPeriodic")
  
  def teleopInit(self):
    self.logger.info("MODE: teleopInit")
    self.drive.config(self.isSimulation())
    self.lift.config(self.isSimulation())
    self.claw.config(self.isSimulation())
    self.harpoon.config(self.isSimulation())

  def teleopPeriodic(self):
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: teleopPeriodic")

    if self.pilot_stick.getRawButtonPressed(robotmap.XBOX_BACK):
      self.harpoon.stow_harpoon()

    if self.pilot_stick.getRawButtonPressed(robotmap.XBOX_START):
      self.harpoon.deploy_harpoon()

    if self.pilot_stick.getRawButtonPressed(robotmap.XBOX_A):
      self.claw.shoot_ball()

    #Do we need a boolean to look for pressed edge?
    if self.pilot_stick.getPOV() == 0: #Dpad Up
      self.claw.stow_claw()

    #Do we need a boolean to look for pressed edge?
    if self.pilot_stick.getPOV() == 180: #Dpad Down
      self.claw.deploy_claw()

    self.drive.iterate(False, self.pilot_stick, self.copilot_stick)
    self.lift.iterate(True, self.pilot_stick, self.copilot_stick)
    self.claw.iterate(False, self.pilot_stick, self.copilot_stick)
    self.harpoon.iterate(False, self.pilot_stick, self.copilot_stick)

  def disabledInit(self):
    self.logger.info("MODE: disabledInit")
    self.drive.disable()
    self.lift.disable()
    self.claw.disable()
    self.harpoon.disable()

  def disabledPeriodic(self):
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: disabledPeriodic")

  def testInit(self):
    self.logger.info("MODE: testInit")
    self.drive.config(self.isSimulation())
    self.lift.config(self.isSimulation())
    self.claw.config(self.isSimulation())
    self.harpoon.config(self.isSimulation())

  def testPeriodic(self):
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: testPeriodic")

    self.drive.iterate(True, self.pilot_stick, self.copilot_stick)
    self.lift.iterate(True, self.pilot_stick, self.copilot_stick)
    self.claw.iterate(True, self.pilot_stick, self.copilot_stick)
    self.harpoon.iterate(True, self.pilot_stick, self.copilot_stick)

if __name__ == "__main__":
    wpilib.run(MyRobot, physics_enabled=True)

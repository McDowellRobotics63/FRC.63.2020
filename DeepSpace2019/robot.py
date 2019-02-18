
import wpilib

import robotmap

from wpilib import Compressor

from drive import DeepSpaceDrive
from lift import DeepSpaceLift
from claw import DeepSpaceClaw

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

  def autonomousInit(self):
    self.logger.info("MODE: autonomousInit")
    self.drive.config()
    self.lift.config()
    self.claw.config()

  def autonomousPeriodic(self):
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: autonomousPeriodic")
  
  def teleopInit(self):
    self.logger.info("MODE: teleopInit")
    self.drive.config()
    self.lift.config()
    self.claw.config()

  def teleopPeriodic(self):
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: teleopPeriodic")
    
    self.drive.iterate(self.pilot_stick, self.copilot_stick)
    self.lift.iterate(self.pilot_stick, self.copilot_stick)
    self.claw.iterate(self.pilot_stick, self.copilot_stick)

  def disabledInit(self):
    self.logger.info("MODE: disabledInit")
    self.drive.disable()
    self.lift.disable()
    self.claw.disable()

  def disabledPeriodic(self):
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: disabledPeriodic")

  def testInit(self):
    self.logger.info("MODE: testInit")
    self.drive.config()
    self.lift.config()
    self.claw.config()

  def testPeriodic(self):
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: testPeriodic")

if __name__ == "__main__":
    wpilib.run(MyRobot, physics_enabled=True)

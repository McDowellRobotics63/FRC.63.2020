
import wpilib

import robotmap

from wpilib import Compressor
from wpilib import PowerDistributionPanel

from lift import DeepSpaceLift

class MyRobot(wpilib.TimedRobot):

  def robotInit(self):
    self.timer = wpilib.Timer()
    self.timer.start()

    if self.isReal():
      self.compressor = Compressor(robotmap.PCM2_CANID)
      self.pdp = PowerDistributionPanel(robotmap.LIFT_CAN_ID)
    else:
      self.compressor = Compressor(0)

    self.pilot_stick = wpilib.Joystick(0)
    self.copilot_stick = wpilib.Joystick(1)

    self.lift = DeepSpaceLift(self.logger)
    self.lift.init()

  def autonomousInit(self):
    self.logger.info("MODE: autonomousInit")
    self.lift.config(self.isSimulation())

  def autonomousPeriodic(self):
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: autonomousPeriodic")
  
  def teleopInit(self):
    self.logger.info("MODE: teleopInit")
    self.lift.config(self.isSimulation())

  def teleopPeriodic(self):
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: teleopPeriodic")

    self.lift.iterate(False, self.pilot_stick, self.copilot_stick)

  def disabledInit(self):
    self.logger.info("MODE: disabledInit")
    self.lift.disable()

  def disabledPeriodic(self):
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: disabledPeriodic")

  def testInit(self):
    self.logger.info("MODE: testInit")
    self.lift.config(self.isSimulation())

  def testPeriodic(self):
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: testPeriodic")

    self.lift.iterate(True, self.pilot_stick, self.copilot_stick)

if __name__ == "__main__":
    wpilib.run(MyRobot, physics_enabled=True)

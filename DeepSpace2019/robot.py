
import wpilib

import robotmap
import statistics
import numpy

from wpilib import Compressor
from wpilib import sendablechooser
from wpilib import SmartDashboard

from xboxcontroller import XboxController
from drive import DeepSpaceDrive
from lift import DeepSpaceLift
from claw import DeepSpaceClaw
from harpoon import DeepSpaceHarpoon

from robotenums import RobotMode
from robotenums import LiftPreset

class MyRobot(wpilib.TimedRobot):

  robot_mode = RobotMode.AUTO

  def robotInit(self):
    self.timer = wpilib.Timer()
    self.timer.start()
    
    if self.isReal():
      self.compressor = Compressor(robotmap.PCM2_CANID)
      self.compressor.setClosedLoopControl(True)
      self.logger.info("Compressor enabled: " + str(self.compressor.enabled()))
    else:
      self.compressor = Compressor(0)

    self.pilot_stick = XboxController(0)
    self.copilot_stick = XboxController(1)

    self.drive = DeepSpaceDrive(self.logger)
    self.drive.init()

    self.lift = DeepSpaceLift(self.logger)
    self.lift.init()

    self.claw = DeepSpaceClaw(self.logger)
    self.claw.init()

    self.harpoon = DeepSpaceHarpoon(self.logger)
    self.harpoon.init()
  
  def teleopInit(self):
    self.compressor.setClosedLoopControl(True)
    self.logger.info("teleopInit Compressor enabled: " + str(self.compressor.enabled()))

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

  def autonomousInit(self):
    self.compressor.setClosedLoopControl(True)
    self.logger.info("teleopInit Compressor enabled: " + str(self.compressor.enabled()))

    self.robot_mode = RobotMode.TELE
    self.logger.info("MODE: autonomousInit")
    self.pilot_stick.config()
    self.copilot_stick.config()
    self.drive.config(self.isSimulation())
    self.lift.config(self.isSimulation())
    self.claw.config(self.isSimulation())
    self.harpoon.config(self.isSimulation())

  def autonomousPeriodic(self):
    self.robot_mode = RobotMode.TELE
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: autonomousPeriodic")

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
  
    self.harpoon.ir_data.append(self.harpoon.ir_harpoon.getVoltage())

    if len(self.harpoon.ir_data) == 10:
      self.harpoon.ir_data.sort()
      med = statistics.median(self.harpoon.ir_data)
      val = numpy.interp(med, self.harpoon.ir_loookup.keys(), self.harpoon.ir_loookup.values())
      SmartDashboard.putNumber("IRVolts", val)
      self.harpoon.ir_data.clear()
      
      

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

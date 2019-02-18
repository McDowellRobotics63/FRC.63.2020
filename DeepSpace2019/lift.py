
import wpilib

from wpilib import Solenoid

import robotmap

from ctre import TalonSRX
from ctre import ControlMode
from ctre import FeedbackDevice
from ctre._impl import StatusFrame

class DeepSpaceLift():

  def __init__(self, logger):
    self.logger = logger

  def init(self):
    self.logger.info("DeepSpaceLift::init()")
    self.timer = wpilib.Timer()
    self.timer.start()

    self.talon = TalonSRX(robotmap.LIFT_CAN_ID)

    self.lift_pneumatic_extend = Solenoid(robotmap.PCM1_CANID, robotmap.LIFT_RAISE_SOLENOID)
    self.lift_pneumatic_retract = Solenoid(robotmap.PCM1_CANID, robotmap.LIFT_LOWER_SOLENOID)

    self.lift_pneumatic_extend.set(False)
    self.lift_pneumatic_retract.set(True)


  def config(self):
    self.logger.info("DeepSpaceLift::config()")
    self.talon.configNominalOutputForward(0.0, 10)
    self.talon.configNominalOutputReverse(0.0, 10)
    self.talon.configPeakOutputForward(1.0, 10)
    self.talon.configPeakOutputReverse(-1.0, 10)
    self.talon.enableVoltageCompensation(True)
    self.talon.configVoltageCompSaturation(11.5, 10)
    self.talon.configOpenLoopRamp(0.125, 10)
    self.talon.setInverted(False)

  def iterate(self, pilot_stick, copilot_stick):
    if self.timer.hasPeriodPassed(0.5):
      self.logger.info("DeepSpaceLift::iterate()")

    self.talon.set(ControlMode.PercentOutput, copilot_stick.getRawAxis(robotmap.XBOX_LEFT_Y_AXIS))

    if copilot_stick.getRawButton(robotmap.XBOX_LEFT_BUMPER): #left bumper
      self.lift_pneumatic_extend.set(True) 
      self.lift_pneumatic_retract.set(False)
    elif copilot_stick.getRawButton(robotmap.XBOX_RIGHT_BUMPER): #right bumper
      self.lift_pneumatic_extend.set(False)
      self.lift_pneumatic_retract.set(True)

  def disable(self):
    self.logger.info("DeepSpaceLift::disable()")


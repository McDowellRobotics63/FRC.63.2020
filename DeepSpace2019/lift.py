
import wpilib

from wpilib import Solenoid

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

    self.talon = TalonSRX(7)

    self.lift_pneumatic_extend = Solenoid(9, 0)
    self.lift_pneumatic_retract = Solenoid(9, 1)

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
    self.logger.info("DeepSpaceLift::iterate()")
    self.talon.set(ControlMode.PercentOutput, copilot_stick.getRawAxis(1))

    if copilot_stick.getRawButton(5): #left bumper
      self.lift_pneumatic_extend.set(True) 
      self.lift_pneumatic_retract.set(False)
    elif copilot_stick.getRawButton(6): #right bumper
      self.lift_pneumatic_extend.set(False)
      self.lift_pneumatic_retract.set(True)

  def disable(self):
    self.logger.info("DeepSpaceLift::disable()")


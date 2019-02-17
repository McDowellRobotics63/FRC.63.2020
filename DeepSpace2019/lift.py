
import wpilib

from ctre import TalonSRX
from ctre import ControlMode
from ctre import FeedbackDevice
from ctre._impl import StatusFrame

class DeepSpaceLift():

  def __init__(self, logger):
    self.logger = logger

  def init(self):
    self.logger.info("DeepSpaceLift::init()")
    self.talon = TalonSRX(7)
    self.timer = wpilib.Timer()
    self.timer.start()

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
    self.talon.set(ControlMode.PercentOutput, pilot_stick.getRawAxis(1))

  def disable(self):
    self.logger.info("DeepSpaceLift::disable()")


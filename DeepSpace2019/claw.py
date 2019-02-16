
import wpilib

from ctre import TalonSRX
from ctre import FeedbackDevice
from ctre._impl import StatusFrame
from ctre import ControlMode

class DeepSpaceClaw():

  def __init__(self, logger):
    self.logger = logger

  def init(self):
    self.logger.info("DeepSpaceClaw::init()")
    self.timer = wpilib.Timer()
    self.timer.start()

    self.talon = TalonSRX(8)

  def config(self):
    self.logger.info("DeepSpaceClaw::config()")
    self.talon.configSelectedFeedbackSensor(FeedbackDevice.Analog, 0, 10)
    self.talon.configSelectedFeedbackCoefficient(1.0, 0, 10)
    self.talon.setSensorPhase(False)
    self.talon.setStatusFramePeriod(StatusFrame.Status_2_Feedback0, 10, 10)
    self.talon.configNominalOutputForward(0.0, 10)
    self.talon.configNominalOutputReverse(0.0, 10)
    self.talon.configPeakOutputForward(1.0, 10)
    self.talon.configPeakOutputReverse(-1.0, 10)
    self.talon.enableVoltageCompensation(True)
    self.talon.configVoltageCompSaturation(11.5, 10)
    self.talon.configOpenLoopRamp(0.125, 10)


  def iterate(self, pilot_stick, copilot_stick):
    if self.timer.hasPeriodPassed(0.5):
      self.logger.info("DeepSpaceClaw::iterate()")
      self.logger.info("Claw current: " + str(self.talon.getOutputCurrent()))
      self.logger.info("Claw position: " + str(self.talon.getSelectedSensorPosition(0)))
      self.logger.info("Claw analog in: " + str(self.talon.getAnalogInRaw()))
    self.talon.set(ControlMode.PercentOutput, pilot_stick.getRawAxis(1))

  def disable(self):
    self.logger.info("DeepSpaceClaw::disable()")


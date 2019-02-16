
import wpilib

from ctre import TalonSRX
from ctre import ControlMode
from ctre import FeedbackDevice
from ctre._impl import StatusFrame

class DeepSpaceDrive():

  def __init__(self, logger):
    self.logger = logger

  def init(self):
    self.logger.info("DeepSpaceDrive::init()")
    self.timer = wpilib.Timer()
    self.timer.start()

    self.leftTalonMaster = TalonSRX(2)
    self.leftTalonSlave = TalonSRX(1)

    self.rightTalonMaster = TalonSRX(3)
    self.rightTalonSlave = TalonSRX(4)

  def config(self):
    self.logger.info("DeepSpaceDrive::config()")
    
    self.leftTalonMaster.configNominalOutputForward(0.0, 10)
    self.leftTalonMaster.configNominalOutputReverse(0.0, 10)
    self.leftTalonMaster.configPeakOutputForward(1.0, 10)
    self.leftTalonMaster.configPeakOutputReverse(-1.0, 10)
    self.leftTalonMaster.enableVoltageCompensation(True)
    self.leftTalonMaster.configVoltageCompSaturation(11.5, 10)
    self.leftTalonMaster.configOpenLoopRamp(0.125, 10)
    self.leftTalonMaster.setInverted(True)

    self.rightTalonMaster.configNominalOutputForward(0.0, 10)
    self.rightTalonMaster.configNominalOutputReverse(0.0, 10)
    self.rightTalonMaster.configPeakOutputForward(1.0, 10)
    self.rightTalonMaster.configPeakOutputReverse(-1.0, 10)
    self.rightTalonMaster.enableVoltageCompensation(True)
    self.rightTalonMaster.configVoltageCompSaturation(11.5, 10)
    self.rightTalonMaster.configOpenLoopRamp(0.125, 10)

    self.leftTalonSlave.configSelectedFeedbackSensor(FeedbackDevice.QuadEncoder, 0, 10)
    self.leftTalonSlave.configSelectedFeedbackCoefficient(1.0, 0, 10)
    self.leftTalonSlave.setSensorPhase(True)
    self.leftTalonSlave.setStatusFramePeriod(StatusFrame.Status_2_Feedback0, 10, 10)
    self.leftTalonSlave.set(ControlMode.Follower, 2)
    self.leftTalonSlave.setInverted(True)

    self.rightTalonSlave.configSelectedFeedbackSensor(FeedbackDevice.QuadEncoder, 0, 10)
    self.rightTalonSlave.configSelectedFeedbackCoefficient(1.0, 0, 10)
    self.rightTalonSlave.setSensorPhase(True)
    self.rightTalonSlave.setStatusFramePeriod(StatusFrame.Status_2_Feedback0, 10, 10)
    self.rightTalonSlave.set(ControlMode.Follower, 3)

  def iterate(self, pilot_stick, copilot_stick):
    if self.timer.hasPeriodPassed(0.5):
      self.logger.info("DeepSpaceDrive::iterate()")
      self.logger.info("vleft: " + str(self.leftTalonSlave.getSelectedSensorVelocity(0)) + ", vright: " + str(self.rightTalonSlave.getSelectedSensorVelocity(0)))
      self.logger.info("amps_left: " + str(self.leftTalonMaster.getOutputCurrent()) + ", amps_right: " + str(self.rightTalonMaster.getOutputCurrent()))
      self.logger.info("output_left: " + str(self.leftTalonMaster.getMotorOutputPercent()) + ", output_right: " + str(self.rightTalonMaster.getMotorOutputPercent()))
    self.leftTalonMaster.set(ControlMode.PercentOutput, -1.0 * pilot_stick.getRawAxis(1))
    self.rightTalonMaster.set(ControlMode.PercentOutput, -1.0 * pilot_stick.getRawAxis(5))

  def disable(self):
    self.logger.info("DeepSpaceDrive::disable()")



import wpilib

import robotmap

from wpilib import Solenoid
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

    self.leftTalonMaster = TalonSRX(robotmap.DRIVE_LEFT_MASTER_CAN_ID)
    self.leftTalonSlave = TalonSRX(robotmap.DRIVE_LEFT_SLAVE_CAN_ID)

    self.rightTalonMaster = TalonSRX(robotmap.DRIVE_RIGHT_MASTER_CAN_ID)
    self.rightTalonSlave = TalonSRX(robotmap.DRIVE_RIGHT_SLAVE_CAN_ID)

    self.drive_front_extend = Solenoid(robotmap.PCM1_CANID, robotmap.DRIVE_FRONT_EXTEND_SOLENOID)
    self.drive_front_retract = Solenoid(robotmap.PCM1_CANID, robotmap.DRIVE_FRONT_RETRACT_SOLENOID)
    self.drive_back_extend = Solenoid(robotmap.PCM1_CANID, robotmap.DRIVE_REAR_EXTEND_SOLENOID)
    self.drive_back_retract = Solenoid(robotmap.PCM1_CANID, robotmap.DRIVE_REAR_RETRACT_SOLENOID)

  def config(self):
    self.logger.info("DeepSpaceDrive::config()")
    
    self.leftTalonMaster.configNominalOutputForward(0.0, robotmap.CAN_TIMEOUT_MS)
    self.leftTalonMaster.configNominalOutputReverse(0.0, robotmap.CAN_TIMEOUT_MS)
    self.leftTalonMaster.configPeakOutputForward(1.0, robotmap.CAN_TIMEOUT_MS)
    self.leftTalonMaster.configPeakOutputReverse(-1.0, robotmap.CAN_TIMEOUT_MS)
    self.leftTalonMaster.enableVoltageCompensation(True)
    self.leftTalonMaster.configVoltageCompSaturation(11.5, robotmap.CAN_TIMEOUT_MS)
    self.leftTalonMaster.configOpenLoopRamp(0.125, robotmap.CAN_TIMEOUT_MS)
    self.leftTalonMaster.setInverted(False)

    self.rightTalonMaster.configNominalOutputForward(0.0, robotmap.CAN_TIMEOUT_MS)
    self.rightTalonMaster.configNominalOutputReverse(0.0, robotmap.CAN_TIMEOUT_MS)
    self.rightTalonMaster.configPeakOutputForward(1.0, robotmap.CAN_TIMEOUT_MS)
    self.rightTalonMaster.configPeakOutputReverse(-1.0, robotmap.CAN_TIMEOUT_MS)
    self.rightTalonMaster.enableVoltageCompensation(True)
    self.rightTalonMaster.configVoltageCompSaturation(11.5, robotmap.CAN_TIMEOUT_MS)
    self.rightTalonMaster.configOpenLoopRamp(0.125, robotmap.CAN_TIMEOUT_MS)
    self.rightTalonMaster.setInverted(True)

    self.leftTalonSlave.configSelectedFeedbackSensor(FeedbackDevice.QuadEncoder, 0, robotmap.CAN_TIMEOUT_MS)
    self.leftTalonSlave.configSelectedFeedbackCoefficient(1.0, 0, robotmap.CAN_TIMEOUT_MS)
    self.leftTalonSlave.setSensorPhase(True)
    self.leftTalonSlave.setStatusFramePeriod(StatusFrame.Status_2_Feedback0, 10, robotmap.CAN_TIMEOUT_MS)
    self.leftTalonSlave.set(ControlMode.Follower, 3)
    self.leftTalonSlave.setInverted(False)

    self.rightTalonSlave.configSelectedFeedbackSensor(FeedbackDevice.QuadEncoder, 0, robotmap.CAN_TIMEOUT_MS)
    self.rightTalonSlave.configSelectedFeedbackCoefficient(1.0, 0, robotmap.CAN_TIMEOUT_MS)
    self.rightTalonSlave.setSensorPhase(True)
    self.rightTalonSlave.setStatusFramePeriod(StatusFrame.Status_2_Feedback0, 10, robotmap.CAN_TIMEOUT_MS)
    self.rightTalonSlave.set(ControlMode.Follower, 2)
    self.rightTalonSlave.setInverted(True)

    self.drive_front_extend.set(False)
    self.drive_front_retract.set(True)
    self.drive_back_extend.set(False)
    self.drive_back_retract.set(True)

  def iterate(self, pilot_stick, copilot_stick):
    if self.timer.hasPeriodPassed(0.5):
      self.logger.info("DeepSpaceDrive::iterate()")
      self.logger.info("vleft: " + str(self.leftTalonSlave.getSelectedSensorVelocity(0)) + ", vright: " + str(self.rightTalonSlave.getSelectedSensorVelocity(0)))
      self.logger.info("amps_left: " + str(self.leftTalonMaster.getOutputCurrent()) + ", amps_right: " + str(self.rightTalonMaster.getOutputCurrent()))
      self.logger.info("output_left: " + str(self.leftTalonMaster.getMotorOutputPercent()) + ", output_right: " + str(self.rightTalonMaster.getMotorOutputPercent()))
    
    self.leftTalonMaster.set(ControlMode.PercentOutput, -1.0 * pilot_stick.getRawAxis(robotmap.XBOX_LEFT_Y_AXIS))
    self.rightTalonMaster.set(ControlMode.PercentOutput, -1.0 * pilot_stick.getRawAxis(robotmap.XBOX_RIGHT_Y_AXIS))

    if copilot_stick.getRawButton(robotmap.XBOX_X): #X
      self.drive_front_extend.set(False)
      self.drive_front_retract.set(True)
    elif copilot_stick.getRawButton(robotmap.XBOX_Y): #Y
      self.drive_front_extend.set(True)
      self.drive_front_retract.set(False)

    if copilot_stick.getRawButton(robotmap.XBOX_A):  #A
      self.drive_back_extend.set(False)
      self.drive_back_retract.set(True)
    elif copilot_stick.getRawButton(robotmap.XBOX_B): #B
      self.drive_back_extend.set(True)
      self.drive_back_retract.set(False)

  def disable(self):
    self.logger.info("DeepSpaceDrive::disable()")


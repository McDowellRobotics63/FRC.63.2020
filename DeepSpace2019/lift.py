
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

    self.lift_setpoint = 0

    self.lift_talon = TalonSRX(robotmap.LIFT_CAN_ID)

    '''Select and zero sensor in init() function.  That way the zero position doesn't get reset every time we enable/disable robot'''
    self.lift_talon.configSelectedFeedbackSensor(FeedbackDevice.Analog, 0, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.setSelectedSensorPosition(0, 0, robotmap.CAN_TIMEOUT_MS)

    self.lift_pneumatic_extend = Solenoid(robotmap.PCM1_CANID, robotmap.LIFT_RAISE_SOLENOID)
    self.lift_pneumatic_retract = Solenoid(robotmap.PCM1_CANID, robotmap.LIFT_LOWER_SOLENOID)

    self.lift_pneumatic_extend.set(False)
    self.lift_pneumatic_retract.set(True)

  def config(self, simulation):
    self.logger.info("DeepSpaceLift::config()")

    '''Generic config'''
    self.lift_talon.configNominalOutputForward(0.0, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.configNominalOutputReverse(0.0, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.configPeakOutputForward(1.0, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.configPeakOutputReverse(-1.0, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.enableVoltageCompensation(True)
    self.lift_talon.configVoltageCompSaturation(11.5, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.configOpenLoopRamp(0.125, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.setInverted(False)

    '''Closed-loop feedback config'''
    self.lift_talon.configSelectedFeedbackCoefficient(1.0, 0, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.setSensorPhase(False)
    self.lift_talon.setStatusFramePeriod(StatusFrame.Status_2_Feedback0, 10, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.setStatusFramePeriod(StatusFrame.Status_10_MotionMagic, 10, robotmap.CAN_TIMEOUT_MS)

    '''Closed-loop gains config'''
    self.lift_talon.selectProfileSlot(0, 0)
    self.lift_talon.config_kF(0, robotmap.GAIN_F_LIFT, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.config_kP(0, robotmap.GAIN_P_LIFT, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.config_kI(0, robotmap.GAIN_I_LIFT, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.config_kD(0, robotmap.GAIN_D_LIFT, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.config_IntegralZone(0, robotmap.GAIN_IZONE_LIFT, robotmap.CAN_TIMEOUT_MS)
    if not simulation:
      self.lift_talon.configMotionCruiseVelocity(robotmap.CRUISE_VELOCITY_LIFT, robotmap.CAN_TIMEOUT_MS)
      self.lift_talon.configMotionAcceleration(robotmap.ACCELERATION_LIFT, robotmap.CAN_TIMEOUT_MS)

  def iterate(self, test_mode, pilot_stick, copilot_stick):
    if self.timer.hasPeriodPassed(0.5):
      self.logger.info("DeepSpaceLift::iterate()")

    if copilot_stick.getRawButton(robotmap.XBOX_LEFT_BUMPER): #left bumper
      self.lift_pneumatic_extend.set(True) 
      self.lift_pneumatic_retract.set(False)
    elif copilot_stick.getRawButton(robotmap.XBOX_RIGHT_BUMPER): #right bumper
      self.lift_pneumatic_extend.set(False)
      self.lift_pneumatic_retract.set(True)

    if pilot_stick.getRawButtonPressed(robotmap.XBOX_LEFT_BUMPER): #left bumper
      self.lift_setpoint = min(self.lift_setpoint + 5, robotmap.MAX_POSITION_LIFT)
      print("lift_setpoint: " + str(self.lift_setpoint))
    elif pilot_stick.getRawButtonPressed(robotmap.XBOX_RIGHT_BUMPER): #right bumper
      self.lift_setpoint = max(self.lift_setpoint - 5, robotmap.MIN_POSITION_LIFT)
      print("lift_setpoint: " + str(self.lift_setpoint))

    if test_mode == True:
      self.lift_talon.set(ControlMode.PercentOutput, copilot_stick.getRawAxis(robotmap.XBOX_LEFT_Y_AXIS))
    else:
      self.setLiftSetpoint(self.lift_setpoint)

  def disable(self):
    self.logger.info("DeepSpaceLift::disable()")
    self.lift_talon.set(ControlMode.PercentOutput, 0)

  def setLiftSetpoint(self, ticks):
    ticks = max(min(ticks, robotmap.MAX_POSITION_LIFT), robotmap.MIN_POSITION_LIFT)
    self.lift_talon.set(ControlMode.MotionMagic, ticks)


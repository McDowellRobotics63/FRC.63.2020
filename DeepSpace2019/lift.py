
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
    self.lift_talon.setInverted(True)

    '''sensor config'''
    self.lift_talon.configSelectedFeedbackCoefficient(1.0, 0, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.setSensorPhase(False)
    self.lift_talon.setStatusFramePeriod(StatusFrame.Status_2_Feedback0, 10, robotmap.CAN_TIMEOUT_MS)

  def iterate(self, manual_mode, pilot_stick, copilot_stick):
    if self.timer.hasPeriodPassed(0.5):
      self.logger.info("DeepSpaceLift::iterate()")

    if copilot_stick.getRawButton(robotmap.XBOX_LEFT_BUMPER): #left bumper
      self.lift_pneumatic_extend.set(False)
      self.lift_pneumatic_retract.set(True)
    elif copilot_stick.getRawButton(robotmap.XBOX_RIGHT_BUMPER): #right bumper
      self.lift_pneumatic_extend.set(True) 
      self.lift_pneumatic_retract.set(False)

    lift_position = self.lift_talon.getSelectedSensorPosition(0)

    if manual_mode == True:
      #need to check these separately so we don't disable the mechanism completely if we end up one tick outside our allowable range
      if lift_position > robotmap.MIN_POSITION_LIFT:
        #allow downward motion
        self.lift_talon.set(ControlMode.PercentOutput, min(-1.0 * copilot_stick.getRawAxis(robotmap.XBOX_LEFT_Y_AXIS), 0))
      elif lift_position < robotmap.MAX_POSITION_LIFT:
        #allow upward motion
        self.lift_talon.set(ControlMode.PercentOutput, max(-1.0 * copilot_stick.getRawAxis(robotmap.XBOX_LEFT_Y_AXIS), 0))
      else:
        self.lift_talon.set(ControlMode.PercentOutput, 0.0)
    else:
      err = abs(lift_position - self.lift_setpoint)
      if  err > 1:
        if lift_position < self.lift_setpoint:
          self.lift_talon.set(ControlMode.PercentOutput, 1.0)
        elif lift_position > self.lift_setpoint:
          self.lift_talon.set(ControlMode.PercentOutput, -1.0)
      else:
        self.lift_talon.set(ControlMode.PercentOutput, 0.0)

  def disable(self):
    self.logger.info("DeepSpaceLift::disable()")
    self.lift_talon.set(ControlMode.PercentOutput, 0)

  def setLiftSetpoint(self, ticks):
    self.lift_setpoint = max(min(ticks, robotmap.MAX_POSITION_LIFT), robotmap.MIN_POSITION_LIFT)


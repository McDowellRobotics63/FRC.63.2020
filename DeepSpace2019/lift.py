
import wpilib

from wpilib import Solenoid
from wpilib import SmartDashboard

import robotmap

from ctre import TalonSRX
from ctre import ControlMode
from ctre import FeedbackDevice
from ctre._impl import StatusFrame

from robotenums import RobotMode
from robotenums import LiftState
from robotenums import LiftPreset

class DeepSpaceLift():

  def __init__(self, logger, settings):
    self.logger = logger
    self.settings = settings

  def init(self):
    self.logger.info("DeepSpaceLift::init()")
    self.timer = wpilib.Timer()
    self.timer.start()

    self.state_timer = wpilib.Timer()
    self.current_state = LiftState.LIFT_START_CONFIGURATION
    self.current_lift_preset = LiftPreset.LIFT_PRESET_STOW

    self.min_lift_position = int(self.settings.min_lift_position.getEntry().getNumber(1))
    self.max_lift_position = int(self.settings.max_lift_position.getEntry().getNumber(1))

    self.lift_stow_position = int(self.settings.lift_stow_position.getEntry().getNumber(1))

    self.lift_front_port_low = int(self.settings.lift_front_port_low.getEntry().getNumber(1))
    self.lift_front_port_middle = int(self.settings.lift_front_port_middle.getEntry().getNumber(1))
    self.lift_front_port_high = int(self.settings.lift_front_port_high.getEntry().getNumber(1))
    
    self.lift_side_hatch_low = int(self.settings.lift_side_hatch_low.getEntry().getNumber(1))
    self.lift_side_hatch_middle = int(self.settings.lift_side_hatch_middle.getEntry().getNumber(1))
    self.lift_side_hatch_high = int(self.settings.lift_side_hatch_high.getEntry().getNumber(1))

    self.lift_setpoint = self.min_lift_position

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

  def deploy_lift(self):
    self.current_state = LiftState.LIFT_DEPLOY_BEGIN

  def iterate(self, robot_mode, simulation, pilot_stick, copilot_stick):
    if self.timer.hasPeriodPassed(0.5):
      self.logger.info("DeepSpaceLift::iterate()")

    if simulation:
      self.lift_talon.setAnalogPosition(self.lift_setpoint)

    lift_position = self.lift_talon.getSelectedSensorPosition(0)

    if robot_mode == RobotMode.TEST:
      #need to check these separately so we don't disable the mechanism completely if we end up one tick outside our allowable range
      if lift_position > self.min_lift_position or lift_position < self.max_lift_position:
        self.lift_talon.set(ControlMode.PercentOutput, -1.0 * pilot_stick.getRawAxis(robotmap.XBOX_RIGHT_Y_AXIS))
      elif lift_position < self.min_lift_position:
        #allow upward motion
        self.lift_talon.set(ControlMode.PercentOutput, max(-1.0 * pilot_stick.getRawAxis(robotmap.XBOX_RIGHT_Y_AXIS), 0))
      elif lift_position > self.max_lift_position:
        #allow downward motion
        self.lift_talon.set(ControlMode.PercentOutput, min(-1.0 * pilot_stick.getRawAxis(robotmap.XBOX_RIGHT_Y_AXIS), 0))
      else:
        self.lift_talon.set(ControlMode.PercentOutput, 0.0)
    else:
      self.iterate_state_machine(copilot_stick)

    SmartDashboard.putString("Lift State", self.current_state.name)
    SmartDashboard.putString("Lift Preset", self.current_lift_preset.name)
    SmartDashboard.putNumber("Lift Setpoint", self.lift_setpoint)
    SmartDashboard.putNumber("Lift Position", lift_position)

  def iterate_state_machine(self, copilot_stick):
    #****************DEPLOY SEQUENCE**************************
    if self.current_state == LiftState.LIFT_DEPLOY_EXTEND_PNEUMATIC:
      self.lift_pneumatic_extend.set(True) 
      self.lift_pneumatic_retract.set(False)
      self.state_timer.reset()
      self.state_timer.start()
      self.current_state = LiftState.LIFT_DEPLOY_WAIT1

    elif self.current_state == LiftState.LIFT_DEPLOY_WAIT1:
      if self.state_timer.hasPeriodPassed(0.5):
        self.current_state = LiftState.LIFT_DEPLOY_MOVE_TO_PRESET
    
    elif self.current_state == LiftState.LIFT_DEPLOY_MOVE_TO_PRESET:
      self.lift_setpoint = self.lift_side_hatch_low
      if self.bang_bang_to_setpoint():
        self.current_state = LiftState.LIFT_DEPLOY_RETRACT_PNEUMATIC

    if self.current_state == LiftState.LIFT_DEPLOY_RETRACT_PNEUMATIC:
      self.lift_pneumatic_extend.set(False)
      self.lift_pneumatic_retract.set(True)
      self.state_timer.reset()
      self.state_timer.start()
      self.current_state = LiftState.LIFT_DEPLOY_WAIT2

    elif self.current_state == LiftState.LIFT_DEPLOY_WAIT2:
      if self.state_timer.hasPeriodPassed(0.25):
        self.current_state = LiftState.LIFT_DEPLOY_MOVE_TO_STOW

    elif self.current_state == LiftState.LIFT_DEPLOY_MOVE_TO_STOW:
      self.lift_setpoint = self.lift_stow_position
      if self.bang_bang_to_setpoint():
        self.current_state = LiftState.LIFT_DEPLOYED
    #****************DEPLOY SEQUENCE**************************

    #****************DEPLOYED*********************************
    if self.state_timer.get() > 1.0:
      self.lift_setpoint = self.lift_stow_position
      self.state_timer.stop()
      self.state_timer.reset()
    elif copilot_stick.LeftBumper().get() and copilot_stick.X().get():
      if not self.current_lift_preset == LiftPreset.LIFT_PRESET_PORT_LOW:
        self.current_lift_preset = LiftPreset.LIFT_PRESET_PORT_LOW
        self.lift_setpoint = self.lift_front_port_low
        self.state_timer.stop()
        self.state_timer.reset()
    elif copilot_stick.LeftBumper().get() and copilot_stick.Y().get():
      if not self.current_lift_preset == LiftPreset.LIFT_PRESET_PORT_MIDDLE:
        self.current_lift_preset = LiftPreset.LIFT_PRESET_PORT_MIDDLE
        self.lift_setpoint = self.lift_front_port_middle
        self.state_timer.stop()
        self.state_timer.reset()
    elif copilot_stick.LeftBumper().get() and copilot_stick.B().get():
      if not self.current_lift_preset == LiftPreset.LIFT_PRESET_PORT_HIGH:
        self.current_lift_preset = LiftPreset.LIFT_PRESET_PORT_HIGH
        self.lift_setpoint = self.lift_front_port_high
        self.state_timer.stop()
        self.state_timer.reset()
    elif copilot_stick.RightBumper().get() and copilot_stick.X().get():
      if not self.current_lift_preset == LiftPreset.LIFT_PRESET_HATCH_LOW:
        self.current_lift_preset = LiftPreset.LIFT_PRESET_HATCH_LOW
        self.lift_setpoint = self.lift_side_hatch_low
        self.state_timer.stop()
        self.state_timer.reset()
    elif copilot_stick.RightBumper().get() and copilot_stick.Y().get():
      if not self.current_lift_preset == LiftPreset.LIFT_PRESET_HATCH_MIDDLE:
        self.current_lift_preset = LiftPreset.LIFT_PRESET_HATCH_MIDDLE
        self.lift_setpoint = self.lift_side_hatch_middle
        self.state_timer.stop()
        self.state_timer.reset()
    elif copilot_stick.RightBumper().get() and copilot_stick.B().get():
      if not self.current_lift_preset == LiftPreset.LIFT_PRESET_HATCH_HIGH:
        self.current_lift_preset = LiftPreset.LIFT_PRESET_HATCH_HIGH
        self.lift_setpoint = self.lift_side_hatch_high
        self.state_timer.stop()
        self.state_timer.reset()
    else:
      if not self.current_lift_preset == LiftPreset.LIFT_PRESET_STOW:
        self.current_lift_preset = LiftPreset.LIFT_PRESET_STOW
        self.state_timer.reset()
        self.state_timer.start()


    #****************DEPLOYED*********************************

  def bang_bang_to_setpoint(self):
    on_target = False
    lift_position = self.lift_talon.getSelectedSensorPosition(0)
    err = abs(lift_position - self.lift_setpoint)
    if  err > 1:
      if lift_position < self.lift_setpoint:
        self.lift_talon.set(ControlMode.PercentOutput, 1.0)
      elif lift_position > self.lift_setpoint:
        self.lift_talon.set(ControlMode.PercentOutput, -1.0)
    else:
      self.lift_talon.set(ControlMode.PercentOutput, 0.0)
      on_target = True

    return on_target

  def disable(self):
    self.logger.info("DeepSpaceLift::disable()")
    self.lift_talon.set(ControlMode.PercentOutput, 0)

  def set_lift_setpoint(self, ticks):
    self.lift_setpoint = max(min(ticks, self.max_lift_position), self.min_lift_position)


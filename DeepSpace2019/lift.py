
import wpilib

from wpilib import Solenoid
from wpilib import SmartDashboard
from networktables.util import ntproperty
from wpilib import sendablechooser

import robotmap

from ctre import TalonSRX
from ctre import ControlMode
from ctre import FeedbackDevice
from ctre._impl import StatusFrame

from robotenums import RobotMode
from robotenums import LiftState
from robotenums import LiftPreset

class DeepSpaceLift():
  min_lift_position = ntproperty("/LiftSettings/MinLiftPosition", 75, persistent = True)
  max_lift_position = ntproperty("/LiftSettings/MaxLiftPosition", 225, persistent = True)
  max_lift_adjust_rate = ntproperty("/LiftSettings/MaxLiftAdjustRate", 10, persistent = True)
  max_lift_adjust_value = ntproperty("/LiftSettings/MaxLiftAdjustValue", 15, persistent = True)

  lift_stow_position = ntproperty("/LiftSettings/LiftStowPosition", 90, persistent = True)

  lift_front_port_low = ntproperty("/LiftSettings/LiftFrontPortLow", 150, persistent = True)
  lift_front_port_middle = ntproperty("/LiftSettings/LiftFrontPortMiddle", 175, persistent = True)
  lift_front_port_high = ntproperty("/LiftSettings/LiftFrontPortHigh", 200, persistent = True)
  
  lift_side_hatch_low = ntproperty("/LiftSettings/LiftSideHatchLow", 135, persistent = True)
  lift_side_hatch_middle = ntproperty("/LiftSettings/LiftSideHatchMiddle", 160, persistent = True)
  lift_side_hatch_high = ntproperty("/LiftSettings/LiftSideHatchHigh", 185, persistent = True)

  on_target = False

  def __init__(self, logger):
    self.logger = logger

  def init(self):
    self.logger.info("DeepSpaceLift::init()")
    self.timer = wpilib.Timer()
    self.timer.start()

    self.robot_mode = RobotMode.TEST

    self.last_lift_adjust_time = 0
    self.lift_adjust_timer = wpilib.Timer()
    self.lift_adjust_timer.start()

    self.state_timer = wpilib.Timer()
    self.current_state = LiftState.LIFT_START_CONFIGURATION
    self.current_lift_preset = LiftPreset.LIFT_PRESET_STOW
    self.current_lift_preset_val = self.lift_stow_position

    self.lift_setpoint = self.min_lift_position
    self.lift_adjust_val = 0

    self.lift_talon = TalonSRX(robotmap.LIFT_CAN_ID)

    '''Select and zero sensor in init() function.  That way the zero position doesn't get reset every time we enable/disable robot'''
    self.lift_talon.configSelectedFeedbackSensor(FeedbackDevice.Analog, 0, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.setSelectedSensorPosition(0, 0, robotmap.CAN_TIMEOUT_MS)

    self.lift_pneumatic_extend = Solenoid(robotmap.PCM1_CANID, robotmap.LIFT_RAISE_SOLENOID)
    self.lift_pneumatic_retract = Solenoid(robotmap.PCM1_CANID, robotmap.LIFT_LOWER_SOLENOID)

    self.lift_pneumatic_extend.set(False)
    self.lift_pneumatic_retract.set(True)

    self.test_lift_pneumatic = sendablechooser.SendableChooser()
    self.test_lift_pneumatic.setDefaultOption("Retract", 1)
    self.test_lift_pneumatic.addOption("Extend", 2)

    SmartDashboard.putData("TestLiftPneumatic", self.test_lift_pneumatic)

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

  def go_to_preset(self, preset):
    self.lift_adjust_val = 0

    if preset == LiftPreset.LIFT_PRESET_PORT_LOW:
      self.current_lift_preset = LiftPreset.LIFT_PRESET_PORT_LOW
      self.current_lift_preset_val = self.lift_front_port_low
      self.lift_pneumatic_extend.set(False) 
      self.lift_pneumatic_retract.set(True)
      self.state_timer.stop()
      self.state_timer.reset()

    elif preset == LiftPreset.LIFT_PRESET_PORT_MIDDLE:
      self.current_lift_preset = LiftPreset.LIFT_PRESET_PORT_MIDDLE
      self.current_lift_preset_val = self.lift_front_port_middle
      self.lift_pneumatic_extend.set(False) 
      self.lift_pneumatic_retract.set(True)
      self.state_timer.stop()
      self.state_timer.reset()

    elif preset == LiftPreset.LIFT_PRESET_PORT_HIGH:
      self.current_lift_preset = LiftPreset.LIFT_PRESET_PORT_HIGH
      self.current_lift_preset_val = self.lift_front_port_high
      self.lift_pneumatic_extend.set(True) 
      self.lift_pneumatic_retract.set(False)
      self.state_timer.stop()
      self.state_timer.reset()

    elif preset == LiftPreset.LIFT_PRESET_HATCH_LOW:
      self.current_lift_preset = LiftPreset.LIFT_PRESET_HATCH_LOW
      self.current_lift_preset_val = self.lift_side_hatch_low
      self.lift_pneumatic_extend.set(False) 
      self.lift_pneumatic_retract.set(True)
      self.state_timer.stop()
      self.state_timer.reset()

    elif preset == LiftPreset.LIFT_PRESET_HATCH_MIDDLE:
      self.current_lift_preset = LiftPreset.LIFT_PRESET_HATCH_MIDDLE
      self.current_lift_preset_val = self.lift_side_hatch_middle
      self.lift_pneumatic_extend.set(False) 
      self.lift_pneumatic_retract.set(True)
      self.state_timer.stop()
      self.state_timer.reset()

    elif preset == LiftPreset.LIFT_PRESET_HATCH_HIGH:
      self.current_lift_preset = LiftPreset.LIFT_PRESET_HATCH_HIGH
      self.current_lift_preset_val = self.lift_side_hatch_high
      self.lift_pneumatic_extend.set(True) 
      self.lift_pneumatic_retract.set(False)
      self.state_timer.stop()
      self.state_timer.reset()

    elif preset == LiftPreset.LIFT_PRESET_STOW:
      self.current_lift_preset = LiftPreset.LIFT_PRESET_STOW
      self.current_lift_preset_val = self.lift_stow_position
      self.state_timer.reset()
      self.state_timer.start()

  def iterate(self, robot_mode, simulation, pilot_stick, copilot_stick):
    self.robot_mode = robot_mode
    lift_position = self.lift_talon.getAnalogInRaw()

    if lift_position > self.lift_stow_position + 5:
      SmartDashboard.putBoolean("Creep", True)
    else:
      SmartDashboard.putBoolean("Creep", False)

    if robot_mode == RobotMode.TEST:

      if self.test_lift_pneumatic.getSelected() == 1:
        self.lift_pneumatic_extend.set(False)
        self.lift_pneumatic_retract.set(True)
      else:
        self.lift_pneumatic_extend.set(True)
        self.lift_pneumatic_retract.set(False)


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
      self.iterate_state_machine(pilot_stick, copilot_stick)

    SmartDashboard.putString("Lift State", self.current_state.name)
    SmartDashboard.putString("Lift Preset", self.current_lift_preset.name)
    SmartDashboard.putNumber("Lift Setpoint", self.lift_setpoint)
    SmartDashboard.putNumber("Lift Position", lift_position)

  def iterate_state_machine(self, pilot_stick, copilot_stick):
    #****************DEPLOY SEQUENCE**************************
    if self.current_state == LiftState.LIFT_DEPLOY_EXTEND_PNEUMATIC:
      self.lift_pneumatic_extend.set(True) 
      self.lift_pneumatic_retract.set(False)
      self.state_timer.reset()
      self.state_timer.start()
      self.current_state = LiftState.LIFT_DEPLOY_WAIT1

    elif self.current_state == LiftState.LIFT_DEPLOY_WAIT1:
      if self.state_timer.hasPeriodPassed(0.5):
        self.current_state = LiftState.LIFT_DEPLOY_MOVE_TO_STOW
    
    elif self.current_state == LiftState.LIFT_DEPLOY_MOVE_TO_STOW:
      self.go_to_preset(LiftPreset.LIFT_PRESET_STOW)
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
        self.current_state = LiftState.LIFT_DEPLOYED
    
    #****************DEPLOY SEQUENCE**************************

    #****************DEPLOYED*********************************
    elif self.current_state == LiftState.LIFT_DEPLOYED:
      if self.robot_mode == RobotMode.TELE:
        if copilot_stick.LeftBumper().get() and copilot_stick.X().get():
          if not self.current_lift_preset == LiftPreset.LIFT_PRESET_PORT_LOW:
            self.go_to_preset(LiftPreset.LIFT_PRESET_PORT_LOW)
        elif copilot_stick.LeftBumper().get() and copilot_stick.Y().get():
          if not self.current_lift_preset == LiftPreset.LIFT_PRESET_PORT_MIDDLE:
            self.go_to_preset(LiftPreset.LIFT_PRESET_PORT_MIDDLE)
        elif copilot_stick.LeftBumper().get() and copilot_stick.B().get():
          if not self.current_lift_preset == LiftPreset.LIFT_PRESET_PORT_HIGH:
            self.go_to_preset(LiftPreset.LIFT_PRESET_PORT_HIGH)
        elif copilot_stick.RightBumper().get() and copilot_stick.X().get():
          if not self.current_lift_preset == LiftPreset.LIFT_PRESET_HATCH_LOW:
            self.go_to_preset(LiftPreset.LIFT_PRESET_HATCH_LOW)
        elif copilot_stick.RightBumper().get() and copilot_stick.Y().get():
          if not self.current_lift_preset == LiftPreset.LIFT_PRESET_HATCH_MIDDLE:
            self.go_to_preset(LiftPreset.LIFT_PRESET_HATCH_MIDDLE)
        elif copilot_stick.RightBumper().get() and copilot_stick.B().get():
          if not self.current_lift_preset == LiftPreset.LIFT_PRESET_HATCH_HIGH:
            self.go_to_preset(LiftPreset.LIFT_PRESET_HATCH_HIGH)
        else:
          if not self.current_lift_preset == LiftPreset.LIFT_PRESET_STOW:
            self.go_to_preset(LiftPreset.LIFT_PRESET_STOW)

      current_lift_adjust_time = self.lift_adjust_timer.get()
      dt = current_lift_adjust_time - self.last_lift_adjust_time
      self.last_lift_adjust_time = current_lift_adjust_time

      if self.bang_bang_to_setpoint():
        max_down_adjust = float(abs(self.current_lift_preset_val - self.lift_stow_position))
        max_up_adjust = float(abs(self.current_lift_preset_val - self.max_lift_position))
        self.lift_adjust_val += dt* self.max_lift_adjust_rate * pilot_stick.RightStickY()
        if self.lift_adjust_val > 0:
          self.lift_adjust_val = min(self.lift_adjust_val, self.max_lift_adjust_value)
        else:
          self.lift_adjust_val = max(self.lift_adjust_val, -self.max_lift_adjust_value)
        self.lift_adjust_val = max(min(self.lift_adjust_val, max_up_adjust), -max_down_adjust)

    #****************DEPLOYED*********************************

  def bang_bang_to_setpoint(self):
    if self.current_lift_preset == LiftPreset.LIFT_PRESET_STOW and (self.state_timer.get() > 1.0 or self.robot_mode == RobotMode.AUTO):
        self.lift_pneumatic_extend.set(False) 
        self.lift_pneumatic_retract.set(True)
        self.set_lift_setpoint(self.current_lift_preset_val + int(self.lift_adjust_val))
    
    if not self.current_lift_preset == LiftPreset.LIFT_PRESET_STOW:
      self.set_lift_setpoint(self.current_lift_preset_val + int(self.lift_adjust_val))

    lift_position = self.lift_talon.getSelectedSensorPosition(0)
    err = abs(lift_position - self.lift_setpoint)
    if  err > 1:
      self.on_target = False
      if lift_position < self.lift_setpoint:
        self.lift_talon.set(ControlMode.PercentOutput, 1.0)
      elif lift_position > self.lift_setpoint:
        self.lift_talon.set(ControlMode.PercentOutput, -1.0)
    else:
      self.lift_talon.set(ControlMode.PercentOutput, 0.0)
      self.on_target = True

    return self.on_target

  def disable(self):
    self.logger.info("DeepSpaceLift::disable()")
    self.lift_talon.set(ControlMode.PercentOutput, 0)

  def set_lift_setpoint(self, ticks):
    self.lift_setpoint = max(min(ticks, self.max_lift_position), self.min_lift_position)


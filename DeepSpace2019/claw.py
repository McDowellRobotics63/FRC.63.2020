
import wpilib
from wpilib import SmartDashboard

import math
import ctre
import robotmap

from robotenums import ClawState

class DeepSpaceClaw():
  def __init__(self, logger):
    self.logger = logger

  def init(self):
    self.logger.info("DeepSpaceClaw::init()")
    self.timer = wpilib.Timer()
    self.timer.start()

    self.state_timer = wpilib.Timer()
    self.current_state = ClawState.CLAW_STOW_HOLD

    self.ball_infrared = wpilib.DigitalInput(robotmap.BALL_IR_SENSOR)
    
    self.left_grab = ctre.TalonSRX(robotmap.CLAW_LEFT_WHEELS_CAN_ID)
    self.right_grab = ctre.TalonSRX(robotmap.CLAW_RIGHT_WHEELS_CAN_ID)

    self.talons = [self.left_grab, self.right_grab]

    self.claw_open = wpilib.Solenoid(robotmap.PCM2_CANID, robotmap.CLAW_OPEN_SOLENOID)
    self.claw_close = wpilib.Solenoid(robotmap.PCM2_CANID, robotmap.CLAW_CLOSE_SOLENOID)

    self.wrist_down = wpilib.Solenoid(robotmap.PCM2_CANID, robotmap.WRIST_EXTEND_SOLENOID)
    self.wrist_up = wpilib.Solenoid(robotmap.PCM2_CANID, robotmap.WRIST_RETRACT_SOLENOID)

    self.claw_close.set(True)
    self.claw_open.set(False)

    self.wrist_down.set(False)
    self.wrist_up.set(True)

  def config(self, simulation):
    self.logger.info("DeepSpaceClaw::config()")

    '''Configuration items common for all talons'''
    for talon in self.talons:
      talon.configNominalOutputForward(0.0, robotmap.CAN_TIMEOUT_MS)
      talon.configNominalOutputReverse(0.0, robotmap.CAN_TIMEOUT_MS)
      talon.configPeakOutputForward(1.0, robotmap.CAN_TIMEOUT_MS)
      talon.configPeakOutputReverse(-1.0, robotmap.CAN_TIMEOUT_MS)
      talon.enableVoltageCompensation(True)
      talon.configVoltageCompSaturation(11.5, robotmap.CAN_TIMEOUT_MS)
      talon.configOpenLoopRamp(0.125, robotmap.CAN_TIMEOUT_MS)
  
  def deploy_claw(self):
    self.current_state = ClawState.CLAW_DEPLOY_BEGIN

  def stow_claw(self):
    self.current_state = ClawState.CLAW_STOW_BEGIN

  def shoot_ball(self):
    self.current_state = ClawState.CLAW_SHOOT_BALL

  def iterate(self, robot_mode, pilot_stick, copilot_stick):
    if pilot_stick.LeftBumper().get():
      self.claw_close.set(True)
      self.claw_open.set(False)
    elif pilot_stick.RightBumper().get():
      self.claw_close.set(False)
      self.claw_open.set(True)

    if pilot_stick.A().get():
      self.shoot_ball()

    #Do we need a boolean to look for pressed edge?
    if pilot_stick.DpadUp().get():
      self.stow_claw()

    #Do we need a boolean to look for pressed edge?
    if pilot_stick.DpadDown().get():
      self.deploy_claw()

    self.iterate_state_machine()

    SmartDashboard.putString("Claw State", self.current_state.name)

  def iterate_state_machine(self):
    #****************STOW SEQUENCE****************************
    if self.current_state == ClawState.CLAW_STOW_MOVE_TO_STOW:
      self.left_grab.set(ctre.ControlMode.PercentOutput, 0.0)
      self.right_grab.set(ctre.ControlMode.PercentOutput, 0.0)
      self.wrist_down.set(False)
      self.wrist_up.set(True)
      self.state_timer.reset()
      self.state_timer.start()
      self.current_state = ClawState.CLAW_STOW_WAIT2

    elif self.current_state == ClawState.CLAW_STOW_WAIT2:
      if self.state_timer.hasPeriodPassed(0.25):
        self.current_state = ClawState.CLAW_STOW_HOLD
    
    elif self.current_state == ClawState.CLAW_STOW_HOLD:
      self.left_grab.set(ctre.ControlMode.PercentOutput, 0.0)
      self.right_grab.set(ctre.ControlMode.PercentOutput, 0.0)
    #****************STOW SEQUENCE****************************
    
    #****************DEPLOY SEQUENCE****************************
    elif self.current_state == ClawState.CLAW_DEPLOY:
      self.wrist_down.set(True)
      self.wrist_up.set(False)
      self.state_timer.reset()
      self.state_timer.start()
      self.current_state = ClawState.CLAW_DEPLOY_WAIT1

    elif self.current_state == ClawState.CLAW_DEPLOY_WAIT1:
      if self.state_timer.hasPeriodPassed(0.25):
        self.current_state = ClawState.CLAW_DEPLOY_ACTIVE
    
    elif self.current_state == ClawState.CLAW_DEPLOY_ACTIVE:
      if not self.ball_infrared.get():
        self.left_grab.set(ctre.ControlMode.PercentOutput, 0.0)
        self.right_grab.set(ctre.ControlMode.PercentOutput, 0.0)
      else:
        self.left_grab.set(ctre.ControlMode.PercentOutput, 0.5)
        self.right_grab.set(ctre.ControlMode.PercentOutput, -0.5)
    #****************DEPLOY SEQUENCE****************************

    #****************SHOOT SEQUENCE****************************
    elif self.current_state == ClawState.CLAW_SHOOT_BALL:
      self.left_grab.set(ctre.ControlMode.PercentOutput, -0.5)
      self.right_grab.set(ctre.ControlMode.PercentOutput, 0.5)
      self.current_state = ClawState.CLAW_SHOOT_BALL_WAIT1
      self.state_timer.reset()
      self.state_timer.start()

    elif self.current_state == ClawState.CLAW_SHOOT_BALL_WAIT1:
      if self.state_timer.hasPeriodPassed(0.25):
        self.current_state = ClawState.CLAW_DEPLOY
    #****************SHOOT SEQUENCE****************************

  def disable(self):
    self.logger.info("DeepSpaceClaw::disable()")
    self.left_grab.set(ctre.ControlMode.PercentOutput, 0.0)
    self.right_grab.set(ctre.ControlMode.PercentOutput, 0.0)


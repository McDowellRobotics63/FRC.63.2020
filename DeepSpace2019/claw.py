
import wpilib
from wpilib import SmartDashboard
from wpilib import sendablechooser

import math
import ctre
import robotmap

from robotenums import ClawState
from robotenums import RobotMode

class DeepSpaceClaw():
  def __init__(self, logger):
    self.logger = logger

  def init(self):
    self.logger.info("DeepSpaceClaw::init()")
    self.timer = wpilib.Timer()
    self.timer.start()

    self.state_timer = wpilib.Timer()
    self.current_state = ClawState.CLAW_STOWED

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

    self.test_wrist = sendablechooser.SendableChooser()
    self.test_wrist.setDefaultOption("Retract", 1)
    self.test_wrist.addOption("Extend", 2)

    self.test_claw = sendablechooser.SendableChooser()
    self.test_claw.setDefaultOption("Retract", 1)
    self.test_claw.addOption("Extend", 2)

    SmartDashboard.putData("TestWrist", self.test_wrist)
    SmartDashboard.putData("TestClaw", self.test_claw)
    SmartDashboard.putNumber("TestClawMotors", 0)

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
    if robot_mode == RobotMode.TEST:
      self.test_mode()
      return

    if pilot_stick.DpadLeft().get():
      self.claw_close.set(False)
      self.claw_open.set(True)
    elif pilot_stick.DpadRight().get():
      self.claw_close.set(True)
      self.claw_open.set(False)

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
        self.current_state = ClawState.CLAW_STOWED
    
    elif self.current_state == ClawState.CLAW_STOWED:
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
        self.current_state = ClawState.CLAW_DEPLOYED
    
    elif self.current_state == ClawState.CLAW_DEPLOYED:
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

  def test_mode(self):
    if self.test_wrist.getSelected() == 1:
      self.wrist_up.set(True)
      self.wrist_down.set(False)
    else:
      self.wrist_up.set(False)
      self.wrist_down.set(True)

    if self.test_claw.getSelected() == 1:
      self.claw_close.set(False)
      self.claw_open.set(True)
    else:
      self.claw_close.set(True)
      self.claw_open.set(False)

    self.left_grab.set(ctre.ControlMode.PercentOutput, SmartDashboard.getNumber("TestClawMotors", 0))
    self.right_grab.set(ctre.ControlMode.PercentOutput, -SmartDashboard.getNumber("TestClawMotors", 0))

  def disable(self):
    self.logger.info("DeepSpaceClaw::disable()")
    self.left_grab.set(ctre.ControlMode.PercentOutput, 0.0)
    self.right_grab.set(ctre.ControlMode.PercentOutput, 0.0)



import wpilib
from wpilib import SmartDashboard

import math
import robotmap

from robotenums import HarpoonState

class DeepSpaceHarpoon():
  HARPOON_PNUEMATIC_WAIT_TIME = 0.25

  def __init__(self, logger):
    self.logger = logger

  def init(self):
    self.logger.info("DeepSpaceHarpoon::init()")
    self.timer = wpilib.Timer()
    self.timer.start()
    
    self.state_timer = wpilib.Timer()
    self.current_state = HarpoonState.HARPOON_STOWED

    self.harpoon_outside_extend = wpilib.Solenoid(robotmap.PCM2_CANID, robotmap.HARPOON_OUTSIDE_EXTEND_SOLENOID)
    self.harpoon_outside_retract = wpilib.Solenoid(robotmap.PCM2_CANID, robotmap.HARPOON_OUTSIDE_RETRACT_SOLENOID)

    self.harpoon_center_extend = wpilib.Solenoid(robotmap.PCM2_CANID, robotmap.HARPOON_CENTER_EXTEND_SOLENOID)
    self.harpoon_center_retract = wpilib.Solenoid(robotmap.PCM2_CANID, robotmap.HARPOON_CENTER_RETRACT_SOLENOID)

    self.harpoon_center_extend.set(False)
    self.harpoon_center_retract.set(True)

    self.harpoon_outside_extend.set(False)
    self.harpoon_outside_retract.set(True)

  def config(self, simulation):
    self.logger.info("DeepSpaceHarpoon::config()")

  def deploy_harpoon(self):
    self.current_state = HarpoonState.HARPOON_DEPLOY_BEGIN

  def stow_harpoon(self):
    self.current_state = HarpoonState.HARPOON_STOW_BEGIN

  def iterate(self, robot_mode, pilot_stick, copilot_stick):
    if pilot_stick.Back().get():
      self.stow_harpoon()

    if pilot_stick.Start().get():
      self.deploy_harpoon()

    self.iterate_state_machine()

    SmartDashboard.putString("Harpoon State", self.current_state.name)

  def iterate_state_machine(self):
    #****************DEPLOY SEQUENCE****************************
    if self.current_state == HarpoonState.HARPOON_DEPLOY_EXTEND_OUTSIDE:
      self.harpoon_outside_extend.set(True)
      self.harpoon_outside_retract.set(False)
      self.current_state = HarpoonState.HARPOON_DEPLOY_WAIT1
      self.state_timer.reset()
      self.state_timer.start()

    elif self.current_state == HarpoonState.HARPOON_DEPLOY_WAIT1:
      if self.state_timer.hasPeriodPassed(self.HARPOON_PNUEMATIC_WAIT_TIME):
        self.current_state = HarpoonState.HARPOON_DEPLOY_EXTEND_CENTER

    elif self.current_state == HarpoonState.HARPOON_DEPLOY_EXTEND_CENTER:
      self.harpoon_center_extend.set(True)
      self.harpoon_center_retract.set(False)
      self.current_state = HarpoonState.HARPOON_DEPLOY_WAIT2
      self.state_timer.reset()
      self.state_timer.start()

    elif self.current_state == HarpoonState.HARPOON_DEPLOY_WAIT2:
      if self.state_timer.hasPeriodPassed(self.HARPOON_PNUEMATIC_WAIT_TIME):
        self.current_state = HarpoonState.HARPOON_DEPLOYED
    #****************DEPLOY SEQUENCE****************************
    
    #*****************STOW SEQUENCE*****************************
    elif self.current_state == HarpoonState.HARPOON_STOW_RETRACT_CENTER:
      self.harpoon_center_extend.set(False)
      self.harpoon_center_retract.set(True)
      self.current_state = HarpoonState.HARPOON_STOW_WAIT1
      self.state_timer.reset()
      self.state_timer.start()

    elif self.current_state == HarpoonState.HARPOON_STOW_WAIT1:
      if self.state_timer.hasPeriodPassed(self.HARPOON_PNUEMATIC_WAIT_TIME):
        self.current_state = HarpoonState.HARPOON_STOW_RETRACT_OUTSIDE

    elif self.current_state == HarpoonState.HARPOON_STOW_RETRACT_OUTSIDE:
      self.harpoon_outside_extend.set(False)
      self.harpoon_outside_retract.set(True)
      self.current_state = HarpoonState.HARPOON_STOW_WAIT2
      self.state_timer.reset()
      self.state_timer.start()

    elif self.current_state == HarpoonState.HARPOON_STOW_WAIT2:
      if self.state_timer.hasPeriodPassed(self.HARPOON_PNUEMATIC_WAIT_TIME):
        self.current_state = HarpoonState.HARPOON_STOWED
    #*****************STOW SEQUENCE*****************************

  def disable(self):
    self.logger.info("DeepSpaceHarpoon::disable()")


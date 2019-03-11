
import wpilib
import math
import robotmap

class DeepSpaceHarpoon():

  HARPOON_STOW_RETRACT_CENTER = 3
  HARPOON_STOW_WAIT1 = 4
  HARPOON_STOW_RETRACT_OUTSIDE = 5
  HARPOON_STOW_WAIT2 = 6

  '''
  7, 8, 9 and 10 were if we need to extend center piston at end of stow
  and retract center piston at beginning of deploy
  '''

  HARPOON_DEPLOY_EXTEND_OUTSIDE = 11
  HARPOON_DEPLOY_WAIT1 = 12
  HARPOON_DEPLOY_EXTEND_CENTER = 13
  HARPOON_DEPLOY_WAIT2 = 14

  HARPOON_DEPLOYED = 1
  HARPOON_STOWED = 2
  HARPOON_DEPLOY_BEGIN = HARPOON_DEPLOY_EXTEND_OUTSIDE
  HARPOON_STOW_BEGIN = HARPOON_STOW_RETRACT_CENTER

  HARPOON_PNUEMATIC_WAIT_TIME = 0.25

  def __init__(self, logger):
    self.logger = logger

  def init(self):
    self.logger.info("DeepSpaceHarpoon::init()")
    self.timer = wpilib.Timer()
    self.timer.start()
    
    self.state_timer = wpilib.Timer()
    self.current_state = self.HARPOON_STOWED

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
    self.current_state = self.HARPOON_DEPLOY_BEGIN

  def stow_harpoon(self):
    self.current_state = self.HARPOON_STOW_BEGIN

  def iterate(self, robot_mode, pilot_stick, copilot_stick):
    if pilot_stick.getRawButtonPressed(robotmap.XBOX_BACK):
      self.stow_harpoon()

    if pilot_stick.getRawButtonPressed(robotmap.XBOX_START):
      self.deploy_harpoon()

    #****************DEPLOY SEQUENCE****************************
    if self.current_state == self.HARPOON_DEPLOY_EXTEND_OUTSIDE:
      self.harpoon_outside_extend.set(True)
      self.harpoon_outside_retract.set(False)
      self.current_state = self.HARPOON_DEPLOY_WAIT1
      self.state_timer.reset()
      self.state_timer.start()

    elif self.current_state == self.HARPOON_DEPLOY_WAIT1:
      if self.state_timer.hasPeriodPassed(self.HARPOON_PNUEMATIC_WAIT_TIME):
        self.current_state = self.HARPOON_DEPLOY_EXTEND_CENTER

    elif self.current_state == self.HARPOON_DEPLOY_EXTEND_CENTER:
      self.harpoon_center_extend.set(True)
      self.harpoon_center_retract.set(False)
      self.current_state = self.HARPOON_DEPLOY_WAIT2
      self.state_timer.reset()
      self.state_timer.start()

    elif self.current_state == self.HARPOON_DEPLOY_WAIT2:
      if self.state_timer.hasPeriodPassed(self.HARPOON_PNUEMATIC_WAIT_TIME):
        self.current_state = self.HARPOON_DEPLOYED
    #****************DEPLOY SEQUENCE****************************
    
    #*****************STOW SEQUENCE*****************************
    elif self.current_state == self.HARPOON_STOW_RETRACT_CENTER:
      self.harpoon_center_extend.set(False)
      self.harpoon_center_retract.set(True)
      self.current_state = self.HARPOON_STOW_WAIT1
      self.state_timer.reset()
      self.state_timer.start()

    elif self.current_state == self.HARPOON_STOW_WAIT1:
      if self.state_timer.hasPeriodPassed(self.HARPOON_PNUEMATIC_WAIT_TIME):
        self.current_state = self.HARPOON_STOW_RETRACT_OUTSIDE

    elif self.current_state == self.HARPOON_STOW_RETRACT_OUTSIDE:
      self.harpoon_outside_extend.set(False)
      self.harpoon_outside_retract.set(True)
      self.current_state = self.HARPOON_STOW_WAIT2
      self.state_timer.reset()
      self.state_timer.start()

    elif self.current_state == self.HARPOON_STOW_WAIT2:
      if self.state_timer.hasPeriodPassed(self.HARPOON_PNUEMATIC_WAIT_TIME):
        self.current_state = self.HARPOON_STOWED
    #*****************STOW SEQUENCE*****************************

  def disable(self):
    self.logger.info("DeepSpaceHarpoon::disable()")


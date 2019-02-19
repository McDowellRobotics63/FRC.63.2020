
import wpilib
import math
import robotmap

class DeepSpaceHarpoon():

  def __init__(self, logger):
    self.logger = logger

  def init(self):
    self.logger.info("DeepSpaceHarpoon::init()")
    self.timer = wpilib.Timer()
    self.timer.start()

    self.harpoon_outside_extend = wpilib.Solenoid(robotmap.PCM2_CANID, robotmap.HARPOON_OUTSIDE_EXTEND_SOLENOID)
    self.harpoon_outside_retract = wpilib.Solenoid(robotmap.PCM2_CANID, robotmap.HARPOON_OUTSIDE_RETRACT_SOLENOID)

    self.harpoon_center_extend = wpilib.Solenoid(robotmap.PCM2_CANID, robotmap.HARPOON_CENTER_EXTEND_SOLENOID)
    self.harpoon_center_retract = wpilib.Solenoid(robotmap.PCM2_CANID, robotmap.HARPOON_CENTER_RETRACT_SOLENOID)

    self.harpoon_center_extend.set(False)
    self.harpoon_center_retract.set(True)

    self.harpoon_outside_extend.set(False)
    self.harpoon_outside_retract.set(True)

  def config(self, simulation):
    self.logger.info("DeepSpaceHarpoon::config(): ")

  def iterate(self, test_mode, pilot_stick, copilot_stick):
    if self.timer.hasPeriodPassed(0.5):
      self.logger.info("DeepSpaceHarpoon::iterate()")

    if pilot_stick.getRawButton(robotmap.XBOX_X):  #X
      self.harpoon_center_extend.set(False)
      self.harpoon_center_retract.set(True)
    elif pilot_stick.getRawButton(robotmap.XBOX_Y): #Y
      self.harpoon_center_extend.set(True)
      self.harpoon_center_retract.set(False)

    if pilot_stick.getRawButton(robotmap.XBOX_A):  #A
      self.harpoon_outside_extend.set(False)
      self.harpoon_outside_retract.set(True)
    elif pilot_stick.getRawButton(robotmap.XBOX_B):  #B
      self.harpoon_outside_extend.set(True)
      self.harpoon_outside_retract.set(False)

  def disable(self):
    self.logger.info("DeepSpaceHarpoon::disable()")


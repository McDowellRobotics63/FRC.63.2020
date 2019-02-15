
import wpilib

class DeepSpaceDrive():

  def __init__(self, logger):
    self.logger = logger

  def init(self):
    self.logger.info("DeepSpaceDrive::init()")
    self.timer = wpilib.Timer()
    self.timer.start()

  def config(self):
    self.logger.info("DeepSpaceDrive::config()")

  def iterate(self, pilot_stick, copilot_stick):
    self.logger.info("DeepSpaceDrive::iterate()")

  def disable(self):
    self.logger.info("DeepSpaceDrive::disable()")


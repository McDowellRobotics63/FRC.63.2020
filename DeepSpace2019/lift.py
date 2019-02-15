
import wpilib

class DeepSpaceLift():

  def __init__(self, logger):
    self.logger = logger

  def init(self):
    self.logger.info("DeepSpaceLift::init()")
    self.timer = wpilib.Timer()
    self.timer.start()

  def config(self):
    self.logger.info("DeepSpaceLift::config()")

  def iterate(self, pilot_stick, copilot_stick):
    self.logger.info("DeepSpaceLift::iterate()")

  def disable(self):
    self.logger.info("DeepSpaceLift::disable()")


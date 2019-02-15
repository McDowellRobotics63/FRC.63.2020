
import wpilib

class DeepSpaceClaw():

  def __init__(self, logger):
    self.logger = logger

  def init(self):
    self.logger.info("DeepSpaceClaw::init()")
    self.timer = wpilib.Timer()
    self.timer.start()

  def config(self):
    self.logger.info("DeepSpaceClaw::config()")

  def iterate(self, pilot_stick, copilot_stick):
    self.logger.info("DeepSpaceClaw::iterate()")

  def disable(self):
    self.logger.info("DeepSpaceClaw::disable()")



import wpilib

class MyRobot(wpilib.TimedRobot):

  def robotInit(self):
    self.timer = wpilib.Timer()
    self.timer.start()

    self.pilot_stick = wpilib.Joystick(0)
    self.copilot_stick = wpilib.Joystick(1)

  def autonomousInit(self):
    self.logger.info("MODE: autonomousInit")

  def autonomousPeriodic(self):
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: autonomousPeriodic")
  
  def teleopInit(self):
    self.logger.info("MODE: teleopInit")

  def teleopPeriodic(self):
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: teleopPeriodic")

  def disabledInit(self):
    self.logger.info("MODE: disabledInit")

  def disabledPeriodic(self):
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: disabledPeriodic")

  def testInit(self):
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: testInit")

  def testPeriodic(self):
    if self.timer.hasPeriodPassed(1.0):
      self.logger.info("MODE: testPeriodic")

if __name__ == "__main__":
    wpilib.run(MyRobot, physics_enabled=True)

import wpilib

from xboxcontroller import XboxController

class MyRobot(wpilib.TimedRobot):

  def robotInit(self):
    self.timer = wpilib.Timer()
    self.timer.start()

    self.stick = XboxController(0)
    
    
  def teleopInit(self):
      print("MODE: teleopInit")
 
  def teleopPeriodic(self):
    if self.timer.hasPeriodPassed(0.25):
      print(str(self.stick.LeftStickY()))

  def disabledInit(self):
    print("MODE: disabledInit")

  def disabledPeriodic(self):
    if self.timer.hasPeriodPassed(1.0):
      print("MODE: disabledPeriodic")

if __name__ == "__main__":
    wpilib.run(MyRobot, physics_enabled=True)

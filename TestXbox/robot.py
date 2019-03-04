import wpilib

from wpilib import SmartDashboard
from xboxcontroller import XboxController

class MyRobot(wpilib.TimedRobot):

  def robotInit(self):
    self.timer = wpilib.Timer()
    self.timer.start()

    self.stick = XboxController(0)

    SmartDashboard.putString("LEFT_Y_VALUES", "LEFT_Y_VALUES")
    SmartDashboard.putNumber("left_y_rate", 0.6)
    SmartDashboard.putNumber("left_y_expo", 1.0)
    SmartDashboard.putNumber("left_y_deadband", 0.1)
    SmartDashboard.putNumber("left_y_power", 1.5)
    SmartDashboard.putNumber("left_y_min", -0.5)
    SmartDashboard.putNumber("left_y_max", 0.5)

    SmartDashboard.putString("LEFT_X_VALUES", "LEFT_X_VALUES")
    SmartDashboard.putNumber("left_x_rate", 0.5)
    SmartDashboard.putNumber("left_x_expo", 1.0)
    SmartDashboard.putNumber("left_x_deadband", 0.1)
    SmartDashboard.putNumber("left_x_power", 1.5)
    SmartDashboard.putNumber("left_x_min", -0.5)
    SmartDashboard.putNumber("left_x_max", 0.5)

    SmartDashboard.putString("RIGHT_Y_VALUES", "RIGHT_Y_VALUES")
    SmartDashboard.putNumber("right_y_rate", 1.0)
    SmartDashboard.putNumber("right_y_expo", 0.0)
    SmartDashboard.putNumber("right_y_deadband", 0.1)
    SmartDashboard.putNumber("right_y_power", 1.0)
    SmartDashboard.putNumber("right_y_min", -1.0)
    SmartDashboard.putNumber("right_y_max", 1.0)
		
    SmartDashboard.putString("RIGHT_X_VALUES", "RIGHT_X_VALUES")
    SmartDashboard.putNumber("right_x_rate", 0.5)
    SmartDashboard.putNumber("right_x_expo", 1.0)
    SmartDashboard.putNumber("right_x_deadband", 0.1)
    SmartDashboard.putNumber("right_x_power", 1.5)
    SmartDashboard.putNumber("right_x_min", -0.5)
    SmartDashboard.putNumber("right_x_max", 0.5)
    
    
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

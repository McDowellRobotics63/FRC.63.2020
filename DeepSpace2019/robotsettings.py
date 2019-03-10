
from wpilib.shuffleboard import Shuffleboard
from networktables import NetworkTables

class DeepSpaceSettings():

  def __init__(self):

    #Left Y
    self.left_y_rate = Shuffleboard.getTab("DriveSettings").addPersistent("left_y_rate", 0.85)
    self.left_y_expo = Shuffleboard.getTab("DriveSettings").addPersistent("left_y_expo", 0.6)
    self.left_y_deadband = Shuffleboard.getTab("DriveSettings").addPersistent("left_y_deadband", 0.02)
    self.left_y_power = Shuffleboard.getTab("DriveSettings").addPersistent("left_y_power", 1.5)
    self.left_y_min = Shuffleboard.getTab("DriveSettings").addPersistent("left_y_min", -1.0)
    self.left_y_max = Shuffleboard.getTab("DriveSettings").addPersistent("left_y_max", 1.0)

    #Left X
    self.left_x_rate = Shuffleboard.getTab("DriveSettings").addPersistent("left_x_rate", 0.85)
    self.left_x_expo = Shuffleboard.getTab("DriveSettings").addPersistent("left_x_expo", 0.6)
    self.left_x_deadband = Shuffleboard.getTab("DriveSettings").addPersistent("left_x_deadband", 0.02)
    self.left_x_power = Shuffleboard.getTab("DriveSettings").addPersistent("left_x_power", 1.5)
    self.left_x_min = Shuffleboard.getTab("DriveSettings").addPersistent("left_x_min", -1.0)
    self.left_x_max = Shuffleboard.getTab("DriveSettings").addPersistent("left_x_max", 1.0)
    
    #Right Y
    self.right_y_rate = Shuffleboard.getTab("DriveSettings").addPersistent("right_y_rate", 1.0)
    self.right_y_expo = Shuffleboard.getTab("DriveSettings").addPersistent("right_y_expo", 0.0)
    self.right_y_deadband = Shuffleboard.getTab("DriveSettings").addPersistent("right_y_deadband", 0.1)
    self.right_y_power = Shuffleboard.getTab("DriveSettings").addPersistent("right_y_power", 1.0)
    self.right_y_min = Shuffleboard.getTab("DriveSettings").addPersistent("right_y_min", -1.0)
    self.right_y_max = Shuffleboard.getTab("DriveSettings").addPersistent("right_y_max", 1.0)

    #Right X
    self.right_x_rate = Shuffleboard.getTab("DriveSettings").addPersistent("right_x_rate", 1.0)
    self.right_x_expo = Shuffleboard.getTab("DriveSettings").addPersistent("right_x_expo", 0.0)
    self.right_x_deadband = Shuffleboard.getTab("DriveSettings").addPersistent("right_x_deadband", 0.1)
    self.right_x_power = Shuffleboard.getTab("DriveSettings").addPersistent("right_x_power", 1.0)
    self.right_x_min = Shuffleboard.getTab("DriveSettings").addPersistent("right_x_min", -1.0)
    self.right_x_max = Shuffleboard.getTab("DriveSettings").addPersistent("right_x_max", 1.0)


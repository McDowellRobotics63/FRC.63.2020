
from wpilib.shuffleboard import Shuffleboard
from networktables import NetworkTables

class DeepSpaceSettings():

  def __init__(self):

    self.lift_settings_table = NetworkTables.getTable('LiftSettings')
    self.drive_settings_table = NetworkTables.getTable('DriveSettings')

    self.lift_settings_table.setDefaultNumber("MinLiftPosition", 75)
    self.min_lift_position = self.lift_settings_table.getEntry("MinLiftPosition")
    self.min_lift_position.setPersistent()

    self.lift_settings_table.setDefaultNumber("MaxLiftPosition", 225)
    self.max_lift_position = self.lift_settings_table.getEntry("MaxLiftPosition")
    self.max_lift_position.setPersistent()

    self.lift_settings_table.setDefaultNumber("MaxLiftAdjustRate", 10)
    self.max_lift_adjust_rate = self.lift_settings_table.getEntry("MaxLiftAdjustRate")
    self.max_lift_adjust_rate.setPersistent()

    self.lift_settings_table.setDefaultNumber("MaxLiftAdjustValue", 15)
    self.max_lift_adjust_value = self.lift_settings_table.getEntry("MaxLiftAdjustValue")
    self.max_lift_adjust_value.setPersistent()

    self.lift_settings_table.setDefaultNumber("LiftStowPosition", 90)
    self.lift_stow_position = self.lift_settings_table.getEntry("LiftStowPosition")
    self.lift_stow_position.setPersistent()

    self.lift_settings_table.setDefaultNumber("LiftFrontPortLow", 150)
    self.lift_front_port_low = self.lift_settings_table.getEntry("LiftFrontPortLow")
    self.lift_front_port_low.setPersistent()

    self.lift_settings_table.setDefaultNumber("LiftFrontPortMiddle", 175)
    self.lift_front_port_middle = self.lift_settings_table.getEntry("LiftFrontPortMiddle")
    self.lift_front_port_middle.setPersistent()

    self.lift_settings_table.setDefaultNumber("LiftFrontPortHigh", 200)
    self.lift_front_port_high = self.lift_settings_table.getEntry("LiftFrontPortHigh")
    self.lift_front_port_high.setPersistent()

    self.lift_settings_table.setDefaultNumber("LiftSideHatchLow", 135)
    self.lift_side_hatch_low = self.lift_settings_table.getEntry("LiftSideHatchLow")
    self.lift_side_hatch_low.setPersistent()

    self.lift_settings_table.setDefaultNumber("LiftSideHatchMiddle", 160)
    self.lift_side_hatch_middle = self.lift_settings_table.getEntry("LiftSideHatchMiddle")
    self.lift_side_hatch_middle.setPersistent()

    self.lift_settings_table.setDefaultNumber("LiftSideHatchHigh", 185)
    self.lift_side_hatch_high = self.lift_settings_table.getEntry("LiftSideHatchHigh")
    self.lift_side_hatch_high.setPersistent()

    #Left Y
    self.drive_settings_table.setDefaultNumber("left_y_rate", 0.85)
    self.left_y_rate = self.drive_settings_table.getEntry("left_y_rate")
    self.left_y_rate.setPersistent()

    self.drive_settings_table.setDefaultNumber("left_y_expo", 0.6)
    self.left_y_expo = self.drive_settings_table.getEntry("left_y_expo")
    self.left_y_expo.setPersistent()

    self.drive_settings_table.setDefaultNumber("left_y_deadband", 0.02)
    self.left_y_deadband = self.drive_settings_table.getEntry("left_y_deadband")
    self.left_y_deadband.setPersistent()

    self.drive_settings_table.setDefaultNumber("left_y_power", 1.5)
    self.left_y_power = self.drive_settings_table.getEntry("left_y_power")
    self.left_y_power.setPersistent()

    self.drive_settings_table.setDefaultNumber("left_y_min", -1.0)
    self.left_y_min = self.drive_settings_table.getEntry("left_y_min")
    self.left_y_min.setPersistent()

    self.drive_settings_table.setDefaultNumber("left_y_max", 1.0)
    self.left_y_max = self.drive_settings_table.getEntry("left_y_max")
    self.left_y_max.setPersistent()

    #Left X
    self.drive_settings_table.setDefaultNumber("left_x_rate", 0.85)
    self.left_x_rate = self.drive_settings_table.getEntry("left_x_rate")
    self.left_x_rate.setPersistent()

    self.drive_settings_table.setDefaultNumber("left_x_expo", 0.6)
    self.left_x_expo = self.drive_settings_table.getEntry("left_x_expo")
    self.left_x_expo.setPersistent()

    self.drive_settings_table.setDefaultNumber("left_x_deadband", 0.02)
    self.left_x_deadband = self.drive_settings_table.getEntry("left_x_deadband")
    self.left_x_deadband.setPersistent()

    self.drive_settings_table.setDefaultNumber("left_x_power", 1.5)
    self.left_x_power = self.drive_settings_table.getEntry("left_x_power")
    self.left_x_power.setPersistent()

    self.drive_settings_table.setDefaultNumber("left_x_min", -1.0)
    self.left_x_min = self.drive_settings_table.getEntry("left_x_min")
    self.left_x_min.setPersistent()

    self.drive_settings_table.setDefaultNumber("left_x_max", 1.0)
    self.left_x_max = self.drive_settings_table.getEntry("left_x_max")
    self.left_x_max.setPersistent()
    
    #Right Y
    self.drive_settings_table.setDefaultNumber("right_y_rate", 1.0)
    self.right_y_rate = self.drive_settings_table.getEntry("right_y_rate")
    self.right_y_rate.setPersistent()

    self.drive_settings_table.setDefaultNumber("right_y_expo", 0.0)
    self.right_y_expo = self.drive_settings_table.getEntry("right_y_expo")
    self.right_y_expo.setPersistent()

    self.drive_settings_table.setDefaultNumber("right_y_deadband", 0.1)
    self.right_y_deadband = self.drive_settings_table.getEntry("right_y_deadband")
    self.right_y_deadband.setPersistent()

    self.drive_settings_table.setDefaultNumber("right_y_power", 1.0)
    self.right_y_power = self.drive_settings_table.getEntry("right_y_power")
    self.right_y_power.setPersistent()

    self.drive_settings_table.setDefaultNumber("right_y_min", -1.0)
    self.right_y_min = self.drive_settings_table.getEntry("right_y_min")
    self.right_y_min.setPersistent()

    self.drive_settings_table.setDefaultNumber("right_y_max", 1.0)
    self.right_y_max = self.drive_settings_table.getEntry("right_y_max")
    self.right_y_max.setPersistent()

    #Right X
    self.drive_settings_table.setDefaultNumber("right_x_rate", 1.0)
    self.right_x_rate = self.drive_settings_table.getEntry("right_x_rate")
    self.right_x_rate.setPersistent()

    self.drive_settings_table.setDefaultNumber("right_x_expo", 0.0)
    self.right_x_expo = self.drive_settings_table.getEntry("right_x_expo")
    self.right_x_expo.setPersistent()

    self.drive_settings_table.setDefaultNumber("right_x_deadband", 0.1)
    self.right_x_deadband = self.drive_settings_table.getEntry("right_x_deadband")
    self.right_x_deadband.setPersistent()

    self.drive_settings_table.setDefaultNumber("right_x_power", 1.0)
    self.right_x_power = self.drive_settings_table.getEntry("right_x_power")
    self.right_x_power.setPersistent()

    self.drive_settings_table.setDefaultNumber("right_x_min", -1.0)
    self.right_x_min = self.drive_settings_table.getEntry("right_x_min")
    self.right_x_min.setPersistent()

    self.drive_settings_table.setDefaultNumber("right_x_max", 1.0)
    self.right_x_max = self.drive_settings_table.getEntry("right_x_max")
    self.right_x_max.setPersistent()



import wpilib

from wpilib import Solenoid
from wpilib import SmartDashboard
from networktables.util import ntproperty
from wpilib import sendablechooser

import robotmap

from ctre import TalonSRX
from ctre import ControlMode
from ctre import FeedbackDevice
from ctre._impl import StatusFrame

from robotenums import RobotMode
from robotenums import LiftState
from robotenums import LiftPreset

class DeepSpaceLift():
  min_lift_position = ntproperty("/LiftSettings/MinLiftPosition", 75, persistent = True)
  max_lift_position = ntproperty("/LiftSettings/MaxLiftPosition", 225, persistent = True)
  max_lift_adjust_rate = ntproperty("/LiftSettings/MaxLiftAdjustRate", 10, persistent = True)
  max_lift_adjust_value = ntproperty("/LiftSettings/MaxLiftAdjustValue", 15, persistent = True)

  lift_stow_position = ntproperty("/LiftSettings/LiftStowPosition", 90, persistent = True)

  lift_front_port_low = ntproperty("/LiftSettings/LiftFrontPortLow", 150, persistent = True)
  lift_front_port_middle = ntproperty("/LiftSettings/LiftFrontPortMiddle", 175, persistent = True)
  lift_front_port_high = ntproperty("/LiftSettings/LiftFrontPortHigh", 200, persistent = True)
  
  lift_side_hatch_low = ntproperty("/LiftSettings/LiftSideHatchLow", 135, persistent = True)
  lift_side_hatch_middle = ntproperty("/LiftSettings/LiftSideHatchMiddle", 160, persistent = True)
  lift_side_hatch_high = ntproperty("/LiftSettings/LiftSideHatchHigh", 185, persistent = True)

  on_target = False

  def __init__(self, logger):
    self.logger = logger

  def init(self):
    self.logger.info("DeepSpaceLift::init()")
    self.timer = wpilib.Timer()
    self.timer.start()

    self.robot_mode = RobotMode.TEST

    self.state_timer = wpilib.Timer()

    self.lift_talon = TalonSRX(robotmap.LIFT_CAN_ID)

    '''Select and zero sensor in init() function.  That way the zero position doesn't get reset every time we enable/disable robot'''
    self.lift_talon.configSelectedFeedbackSensor(FeedbackDevice.Analog, 0, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.setSelectedSensorPosition(0, 0, robotmap.CAN_TIMEOUT_MS)

    self.lift_pneumatic_extend = Solenoid(robotmap.PCM1_CANID, robotmap.LIFT_RAISE_SOLENOID)
    self.lift_pneumatic_retract = Solenoid(robotmap.PCM1_CANID, robotmap.LIFT_LOWER_SOLENOID)

    self.lift_pneumatic_extend.set(False)
    self.lift_pneumatic_retract.set(True)

    self.test_lift_pneumatic = sendablechooser.SendableChooser()
    self.test_lift_pneumatic.setDefaultOption("Retract", 1)
    self.test_lift_pneumatic.addOption("Extend", 2)

    SmartDashboard.putData("TestLiftPneumatic", self.test_lift_pneumatic)

  def config(self, simulation):
    self.logger.info("DeepSpaceLift::config()")

    '''Generic config'''
    self.lift_talon.configNominalOutputForward(0.0, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.configNominalOutputReverse(0.0, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.configPeakOutputForward(1.0, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.configPeakOutputReverse(-1.0, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.enableVoltageCompensation(True)
    self.lift_talon.configVoltageCompSaturation(11.5, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.configOpenLoopRamp(0.125, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.setInverted(True)

    '''sensor config'''
    self.lift_talon.configSelectedFeedbackCoefficient(1.0, 0, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.setSensorPhase(False)
    self.lift_talon.setStatusFramePeriod(StatusFrame.Status_2_Feedback0, 10, robotmap.CAN_TIMEOUT_MS)

  def iterate(self, robot_mode, simulation, pilot_stick, copilot_stick):
    self.robot_mode = robot_mode
    lift_position = self.lift_talon.getAnalogInRaw()

    if lift_position > self.lift_stow_position + 30:
      SmartDashboard.putBoolean("Creep", True)
    else:
      SmartDashboard.putBoolean("Creep", False)

    if self.robot_mode == RobotMode.TEST:
      if self.test_lift_pneumatic.getSelected() == 1:
        self.lift_pneumatic_extend.set(False)
        self.lift_pneumatic_retract.set(True)
      else:
        self.lift_pneumatic_extend.set(True)
        self.lift_pneumatic_retract.set(False)
    else:
      if copilot_stick.LeftBumper().get():
        self.lift_pneumatic_extend.set(False)
        self.lift_pneumatic_retract.set(True)
      elif copilot_stick.RightBumper().get():
        self.lift_pneumatic_extend.set(True)
        self.lift_pneumatic_retract.set(False)

    #need to check these separately so we don't disable the mechanism completely if we end up one tick outside our allowable range
    if lift_position > self.min_lift_position or lift_position < self.max_lift_position:
      self.lift_talon.set(ControlMode.PercentOutput, -1.0 * pilot_stick.getRawAxis(robotmap.XBOX_RIGHT_Y_AXIS))
    elif lift_position < self.min_lift_position:
      #allow upward motion
      self.lift_talon.set(ControlMode.PercentOutput, max(-1.0 * pilot_stick.getRawAxis(robotmap.XBOX_RIGHT_Y_AXIS), 0))
    elif lift_position > self.max_lift_position:
      #allow downward motion
      self.lift_talon.set(ControlMode.PercentOutput, min(-1.0 * pilot_stick.getRawAxis(robotmap.XBOX_RIGHT_Y_AXIS), 0))
    else:
      self.lift_talon.set(ControlMode.PercentOutput, 0.0)

    SmartDashboard.putNumber("Lift Position", lift_position)

  def disable(self):
    self.logger.info("DeepSpaceLift::disable()")
    self.lift_talon.set(ControlMode.PercentOutput, 0)

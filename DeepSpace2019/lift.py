
import wpilib

from wpilib import Solenoid
from wpilib import SmartDashboard
from wpilib import sendablechooser

import robotmap

from ctre import TalonSRX
from ctre import ControlMode
from ctre import FeedbackDevice
from ctre._impl import StatusFrame

class DeepSpaceLift():

  def __init__(self, logger):
    self.logger = logger

  def init(self):
    self.logger.info("DeepSpaceLift::init()")
    self.timer = wpilib.Timer()
    self.timer.start()

    self.lift_talon = TalonSRX(robotmap.LIFT_CAN_ID)

    self.lift_talon.configSelectedFeedbackSensor(FeedbackDevice.Analog, 0, robotmap.CAN_TIMEOUT_MS)    

    self.lift_pneumatic_extend = Solenoid(robotmap.PCM1_CANID, robotmap.LIFT_RAISE_SOLENOID)
    self.lift_pneumatic_retract = Solenoid(robotmap.PCM1_CANID, robotmap.LIFT_LOWER_SOLENOID)

    self.lift_pneumatic_extend.set(False)
    self.lift_pneumatic_retract.set(True)

    SmartDashboard.putNumber("min_position", robotmap.MIN_POSITION_LIFT)
    SmartDashboard.putNumber("max_position", robotmap.MAX_POSITION_LIFT)
    SmartDashboard.putBoolean("motor_inverted", False)
    SmartDashboard.putBoolean("sensor_phase", False)
    SmartDashboard.putNumber("lift_setpoint", robotmap.MIN_POSITION_LIFT)
    SmartDashboard.putNumber("gain_f", robotmap.GAIN_F_LIFT)
    SmartDashboard.putNumber("gain_p", robotmap.GAIN_P_LIFT)
    SmartDashboard.putNumber("gain_i", robotmap.GAIN_I_LIFT)
    SmartDashboard.putNumber("gain_d", robotmap.GAIN_D_LIFT)
    SmartDashboard.putNumber("gain_izone", robotmap.GAIN_IZONE_LIFT)
    SmartDashboard.putNumber("cruise", robotmap.CRUISE_VELOCITY_LIFT)
    SmartDashboard.putNumber("accel", robotmap.ACCELERATION_LIFT)

    SmartDashboard.putNumber("lift_raw", self.lift_talon.getAnalogInRaw())
    SmartDashboard.putNumber("lift_position", self.lift_talon.getSelectedSensorPosition(0))
    SmartDashboard.putNumber("lift_velocity", self.lift_talon.getSelectedSensorVelocity(0))
    SmartDashboard.putNumber("percent_output", self.lift_talon.getMotorOutputPercent())

    self.lift_mode = sendablechooser.SendableChooser()
    self.lift_mode.setDefaultOption("OpenLoop", 1)
    self.lift_mode.addOption("MotionMagic", 2)
    SmartDashboard.putData("LiftMode", self.lift_mode)

    self.test_lift_pneumatic = sendablechooser.SendableChooser()
    self.test_lift_pneumatic.setDefaultOption("Retract", 1)
    self.test_lift_pneumatic.addOption("Extend", 2)
    SmartDashboard.putData("LiftPneumatic", self.test_lift_pneumatic)

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
    self.lift_talon.setInverted(SmartDashboard.getBoolean("motor_inverted", False))

    '''Closed-loop feedback config'''
    self.lift_talon.configFeedbackNotContinuous(True)
    self.lift_talon.configSelectedFeedbackCoefficient(1.0, 0, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.setSensorPhase(SmartDashboard.getBoolean("sensor_phase", False))
    self.lift_talon.setStatusFramePeriod(StatusFrame.Status_2_Feedback0, 10, robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.setStatusFramePeriod(StatusFrame.Status_10_MotionMagic, 10, robotmap.CAN_TIMEOUT_MS)

    '''Closed-loop gains config'''
    self.lift_talon.selectProfileSlot(0, 0)
    self.lift_talon.config_kF(0, SmartDashboard.getNumber("gain_f", robotmap.GAIN_F_LIFT), robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.config_kP(0, SmartDashboard.getNumber("gain_p", robotmap.GAIN_P_LIFT), robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.config_kI(0, SmartDashboard.getNumber("gain_i", robotmap.GAIN_I_LIFT), robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.config_kD(0, SmartDashboard.getNumber("gain_d", robotmap.GAIN_D_LIFT), robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.config_IntegralZone(0, SmartDashboard.getNumber("gain_izone", robotmap.GAIN_IZONE_LIFT), robotmap.CAN_TIMEOUT_MS)

    self.lift_talon.configMotionCruiseVelocity(int(SmartDashboard.getNumber("cruise", robotmap.CRUISE_VELOCITY_LIFT)), robotmap.CAN_TIMEOUT_MS)
    self.lift_talon.configMotionAcceleration(int(SmartDashboard.putNumber("accel", robotmap.ACCELERATION_LIFT)), robotmap.CAN_TIMEOUT_MS)

    '''Stuff we might want to use
    ConfigContinuousCurrentLimit
    ConfigPeakCurrentLimit(0)
    configForwardSoftLimitThreshold
    configReverseSoftLimitThreshold
    
    configClearPositionOnLimitF(False)
    configClearPositionOnLimitR(False)
    getLimitSwitchState()
    configForwardLimitSwitchSource(Deactivated)
    configReverseLimitSwitchSource(Deactivated)
    '''

  def iterate(self, test_mode, pilot_stick, copilot_stick):
    if self.timer.hasPeriodPassed(0.5):
      self.logger.info("DeepSpaceLift::iterate()")

    if self.test_lift_pneumatic.getSelected() == 1:
      self.lift_pneumatic_extend.set(False)
      self.lift_pneumatic_retract.set(True)
    else:
      self.lift_pneumatic_extend.set(True)
      self.lift_pneumatic_retract.set(False)

    if self.lift_mode.getSelected() == 1:
      self.lift_talon.set(ControlMode.PercentOutput, -pilot_stick.getRawAxis(robotmap.XBOX_LEFT_Y_AXIS))
    else:
      self.setLiftSetpoint(int(SmartDashboard.getNumber("lift_setpoint", robotmap.MIN_POSITION_LIFT)))

  def disable(self):
    self.logger.info("DeepSpaceLift::disable()")
    self.lift_talon.set(ControlMode.PercentOutput, 0)

  def setLiftSetpoint(self, ticks):
    ticks = max(min(ticks, robotmap.MAX_POSITION_LIFT), robotmap.MIN_POSITION_LIFT)
    self.lift_talon.set(ControlMode.MotionMagic, ticks)


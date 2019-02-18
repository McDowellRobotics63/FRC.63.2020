
import wpilib
import math

import robotmap

from wpilib import Solenoid

from ctre import TalonSRX
from ctre import FeedbackDevice
from ctre._impl import StatusFrame
from ctre import ControlMode

class DeepSpaceClaw():

  def __init__(self, logger):
    self.logger = logger

  def init(self):
    self.logger.info("DeepSpaceClaw::init()")
    self.timer = wpilib.Timer()
    self.timer.start()

    self.wrist_setpoint = 0

    self.left_grab = TalonSRX(robotmap.CLAW_LEFT_WHEELS_CAN_ID)
    self.right_grab = TalonSRX(robotmap.CLAW_RIGHT_WHEELS_CAN_ID)
    self.wrist_talon = TalonSRX(robotmap.CLAW_WRIST_CAN_ID)

    self.harpoon_outside_extend = Solenoid(robotmap.PCM2_CANID, robotmap.HARPOON_OUTSIDE_EXTEND_SOLENOID)
    self.harpoon_outside_retract = Solenoid(robotmap.PCM2_CANID, robotmap.HARPOON_OUTSIDE_RETRACT_SOLENOID)

    self.harpoon_center_extend = Solenoid(robotmap.PCM2_CANID, robotmap.HARPOON_CENTER_EXTEND_SOLENOID)
    self.harpoon_center_retract = Solenoid(robotmap.PCM2_CANID, robotmap.HARPOON_CENTER_RETRACT_SOLENOID)

    self.claw_open = Solenoid(robotmap.PCM2_CANID, robotmap.CLAW_OPEN_SOLENOID)
    self.claw_close = Solenoid(robotmap.PCM2_CANID, robotmap.CLAW_CLOSE_SOLENOID)

    self.harpoon_center_extend.set(False)
    self.harpoon_center_retract.set(True)

    self.harpoon_outside_extend.set(False)
    self.harpoon_outside_retract.set(True)

    self.claw_close.set(True)
    self.claw_open.set(False)

  def config(self):
    self.logger.info("DeepSpaceClaw::config(): ")

    self.wrist_talon.configSelectedFeedbackSensor(FeedbackDevice.Analog, 0, 10)
    self.wrist_talon.configSelectedFeedbackCoefficient(1.0, 0, 10)

    self.wrist_talon.selectProfileSlot(0, 0)
    self.wrist_talon.config_kF(0, 120, 10)
    self.wrist_talon.config_kP(0, 30, 10)
    self.wrist_talon.config_kI(0, 0, 10)
    self.wrist_talon.config_kD(0, 0, 10)
    self.wrist_talon.setSelectedSensorPosition(0, 0, 10)
    self.wrist_talon.configMotionCruiseVelocity(3, 10)
    self.wrist_talon.configMotionAcceleration(3, 10)

    self.wrist_talon.setSensorPhase(False)
    self.wrist_talon.setStatusFramePeriod(StatusFrame.Status_2_Feedback0, 10, 10)
    self.wrist_talon.setStatusFramePeriod(StatusFrame.Status_10_MotionMagic, 10, 10)    
    self.wrist_talon.configNominalOutputForward(0.0, 10)
    self.wrist_talon.configNominalOutputReverse(0.0, 10)
    self.wrist_talon.configPeakOutputForward(1.0, 10)
    self.wrist_talon.configPeakOutputReverse(-1.0, 10)
    self.wrist_talon.enableVoltageCompensation(True)
    self.wrist_talon.configVoltageCompSaturation(11.5, 10)
    self.wrist_talon.configOpenLoopRamp(0.125, 10)

    self.left_grab.configNominalOutputForward(0.0, 10)
    self.left_grab.configNominalOutputReverse(0.0, 10)
    self.left_grab.configPeakOutputForward(1.0, 10)
    self.left_grab.configPeakOutputReverse(-1.0, 10)
    self.left_grab.enableVoltageCompensation(True)
    self.left_grab.configVoltageCompSaturation(11.5, 10)
    self.left_grab.configOpenLoopRamp(0.125, 10)

    self.right_grab.configNominalOutputForward(0.0, 10)
    self.right_grab.configNominalOutputReverse(0.0, 10)
    self.right_grab.configPeakOutputForward(1.0, 10)
    self.right_grab.configPeakOutputReverse(-1.0, 10)
    self.right_grab.enableVoltageCompensation(True)
    self.right_grab.configVoltageCompSaturation(11.5, 10)
    self.right_grab.configOpenLoopRamp(0.125, 10)

  def iterate(self, pilot_stick, copilot_stick):
    if self.timer.hasPeriodPassed(0.5):
      self.logger.info("DeepSpaceClaw::iterate()")
      self.logger.info("Claw current: " + str(self.wrist_talon.getOutputCurrent()))
      self.logger.info("Claw position: " + str(self.wrist_talon.getSelectedSensorPosition(0)))
      self.logger.info("Claw analog in: " + str(self.wrist_talon.getAnalogInRaw()))

    if pilot_stick.getRawButton(robotmap.XBOX_LEFT_BUMPER): #left bumper
      self.left_grab.set(ControlMode.PercentOutput, 0.5)
      self.right_grab.set(ControlMode.PercentOutput, -0.5)
    elif pilot_stick.getRawButton(robotmap.XBOX_RIGHT_BUMPER): #right bumper
      self.left_grab.set(ControlMode.PercentOutput, -0.5)
      self.right_grab.set(ControlMode.PercentOutput, 0.5)
    else:
      self.left_grab.set(ControlMode.PercentOutput, 0.0)
      self.right_grab.set(ControlMode.PercentOutput, 0.0)

    if pilot_stick.getRawButton(robotmap.XBOX_BACK):  #Back
      self.claw_close.set(True)
      self.claw_open.set(False)
    elif pilot_stick.getRawButton(robotmap.XBOX_START): #Start
      self.claw_close.set(False)
      self.claw_open.set(True)

    if pilot_stick.getRawButton(robotmap.XBOX_X):  #X
      self.harpoon_center_extend.set(False)
      self.harpoon_center_retract.set(True)
    elif pilot_stick.getRawButton(robotmap.XBOX_Y): #Y
      self.harpoon_center_extend.set(True)
      self.harpoon_center_retract.set(False)

    if pilot_stick.getRawButton(robotmap.XBOX_A):  #A
      self.harpoon_outside_extend.set(False)
      self.harpoon_outside_retract.set(True)
    elif pilot_stick.getRawButton(robotmap.XBOX_B):  #B
      self.harpoon_outside_extend.set(True)
      self.harpoon_outside_retract.set(False)

    if copilot_stick.getRawButtonPressed(robotmap.XBOX_A): #A
      self.wrist_setpoint = min(self.wrist_setpoint + 5, 30)
      print("wrist_setpoint: " + str(self.wrist_setpoint))
    elif copilot_stick.getRawButtonPressed(robotmap.XBOX_B): #B
      self.wrist_setpoint = max(self.wrist_setpoint - 5, 0)
      print("wrist_setpoint: " + str(self.wrist_setpoint))

    #self.wrist_talon.set(ControlMode.MotionMagic, self.wrist_setpoint)
    self.wrist_talon.set(ControlMode.PercentOutput, copilot_stick.getRawAxis(robotmap.XBOX_RIGHT_Y_AXIS))

  def disable(self):
    self.logger.info("DeepSpaceClaw::disable()")
    self.left_grab.set(ControlMode.PercentOutput, 0.0)
    self.right_grab.set(ControlMode.PercentOutput, 0.0)



import wpilib
import math

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

    self.left_grab = TalonSRX(5)
    self.right_grab = TalonSRX(6)
    self.wrist_talon = TalonSRX(8)

    self.harpoon_center_extend = Solenoid(10, 0)
    self.harpoon_center_retract = Solenoid(10, 1)

    self.claw_open = Solenoid(10, 2)
    self.claw_close = Solenoid(10, 3)

    self.harpoon_outside_extend = Solenoid(10, 5)
    self.harpoon_outside_retract = Solenoid(10, 4)

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

    if pilot_stick.getRawButton(5): #left bumper
      self.left_grab.set(ControlMode.PercentOutput, 0.5)
      self.right_grab.set(ControlMode.PercentOutput, -0.5)
    elif pilot_stick.getRawButton(6): #right bumper
      self.left_grab.set(ControlMode.PercentOutput, -0.5)
      self.right_grab.set(ControlMode.PercentOutput, 0.5)
    else:
      self.left_grab.set(ControlMode.PercentOutput, 0.0)
      self.right_grab.set(ControlMode.PercentOutput, 0.0)

    if pilot_stick.getRawButton(7):  #Back
      self.claw_close.set(True)
      self.claw_open.set(False)
    elif pilot_stick.getRawButton(8): #Start
      self.claw_close.set(False)
      self.claw_open.set(True)

    if pilot_stick.getRawButton(3):  #X
      self.harpoon_center_extend.set(False)
      self.harpoon_center_retract.set(True)
    elif pilot_stick.getRawButton(4): #Y
      self.harpoon_center_extend.set(True)
      self.harpoon_center_retract.set(False)

    if pilot_stick.getRawButton(1):  #A
      self.harpoon_outside_extend.set(False)
      self.harpoon_outside_retract.set(True)
    elif pilot_stick.getRawButton(2):  #B
      self.harpoon_outside_extend.set(True)
      self.harpoon_outside_retract.set(False)

    if copilot_stick.getRawButtonPressed(1):
      self.wrist_setpoint = min(self.wrist_setpoint + 5, 30)
      print("wrist_setpoint: " + str(self.wrist_setpoint))
    elif copilot_stick.getRawButtonPressed(2):
      self.wrist_setpoint = max(self.wrist_setpoint - 5, 0)
      print("wrist_setpoint: " + str(self.wrist_setpoint))

    #self.wrist_talon.set(ControlMode.MotionMagic, self.wrist_setpoint)
    self.wrist_talon.set(ControlMode.PercentOutput, copilot_stick.getRawAxis(5))

  def disable(self):
    self.logger.info("DeepSpaceClaw::disable()")
    self.left_grab.set(ControlMode.PercentOutput, 0.0)
    self.right_grab.set(ControlMode.PercentOutput, 0.0)


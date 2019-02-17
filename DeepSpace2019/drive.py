
import wpilib

from wpilib import Solenoid
from ctre import TalonSRX
from ctre import ControlMode
from ctre import FeedbackDevice
from ctre._impl import StatusFrame

class DeepSpaceDrive():

  def __init__(self, logger):
    self.logger = logger

  def init(self):
    self.logger.info("DeepSpaceDrive::init()")
    self.timer = wpilib.Timer()
    self.timer.start()

    self.leftTalonMaster = TalonSRX(3)
    self.leftTalonSlave = TalonSRX(4)

    self.rightTalonMaster = TalonSRX(2)
    self.rightTalonSlave = TalonSRX(1)

    self.lift_talon = TalonSRX(7)

    self.drive_front_extend = Solenoid(9, 3)
    self.drive_front_retract = Solenoid(9, 2)
    self.drive_back_extend = Solenoid(9, 4)
    self.drive_back_retract = Solenoid(9, 5)
    self.lift_pneumatic_extend = Solenoid(9, 0)
    self.lift_pneumatic_retract = Solenoid(9, 1)
    self.harpoon_center_extend = Solenoid(10, 0)
    self.harpoon_center_retract = Solenoid(10, 1)
    self.harpoon_outside_extend = Solenoid(10, 4)
    self.harpoon_outside_retract = Solenoid(10, 5)


  def config(self):
    self.logger.info("DeepSpaceDrive::config()")
    
    self.leftTalonMaster.configNominalOutputForward(0.0, 10)
    self.leftTalonMaster.configNominalOutputReverse(0.0, 10)
    self.leftTalonMaster.configPeakOutputForward(1.0, 10)
    self.leftTalonMaster.configPeakOutputReverse(-1.0, 10)
    self.leftTalonMaster.enableVoltageCompensation(True)
    self.leftTalonMaster.configVoltageCompSaturation(11.5, 10)
    self.leftTalonMaster.configOpenLoopRamp(0.125, 10)
    self.leftTalonMaster.setInverted(False)

    self.rightTalonMaster.configNominalOutputForward(0.0, 10)
    self.rightTalonMaster.configNominalOutputReverse(0.0, 10)
    self.rightTalonMaster.configPeakOutputForward(1.0, 10)
    self.rightTalonMaster.configPeakOutputReverse(-1.0, 10)
    self.rightTalonMaster.enableVoltageCompensation(True)
    self.rightTalonMaster.configVoltageCompSaturation(11.5, 10)
    self.rightTalonMaster.configOpenLoopRamp(0.125, 10)
    self.rightTalonMaster.setInverted(True)

    self.leftTalonSlave.configSelectedFeedbackSensor(FeedbackDevice.QuadEncoder, 0, 10)
    self.leftTalonSlave.configSelectedFeedbackCoefficient(1.0, 0, 10)
    self.leftTalonSlave.setSensorPhase(True)
    self.leftTalonSlave.setStatusFramePeriod(StatusFrame.Status_2_Feedback0, 10, 10)
    self.leftTalonSlave.set(ControlMode.Follower, 3)
    self.leftTalonSlave.setInverted(False)

    self.rightTalonSlave.configSelectedFeedbackSensor(FeedbackDevice.QuadEncoder, 0, 10)
    self.rightTalonSlave.configSelectedFeedbackCoefficient(1.0, 0, 10)
    self.rightTalonSlave.setSensorPhase(True)
    self.rightTalonSlave.setStatusFramePeriod(StatusFrame.Status_2_Feedback0, 10, 10)
    self.rightTalonSlave.set(ControlMode.Follower, 2)
    self.rightTalonSlave.setInverted(True)

    self.lift_talon.configNominalOutputForward(0.0, 10)
    self.lift_talon.configNominalOutputReverse(0.0, 10)
    self.lift_talon.configPeakOutputForward(1.0, 10)
    self.lift_talon.configPeakOutputReverse(-1.0, 10)
    self.lift_talon.enableVoltageCompensation(True)
    self.lift_talon.configVoltageCompSaturation(11.5, 10)
    self.lift_talon.configOpenLoopRamp(0.125, 10)
    self.lift_talon.setInverted(False)

    self.drive_front_extend.set(False)
    self.drive_front_retract.set(True)
    self.drive_back_extend.set(False)
    self.drive_back_retract.set(True)
    self.lift_pneumatic_extend.set(False)
    self.lift_pneumatic_retract.set(True)
    self.harpoon_center_extend.set(False)
    self.harpoon_center_retract.set(True)
    self.harpoon_outside_extend.set(False)
    self.harpoon_outside_retract.set(True)

  def iterate(self, pilot_stick, copilot_stick):
    if self.timer.hasPeriodPassed(0.5):
      self.logger.info("DeepSpaceDrive::iterate()")
      self.logger.info("vleft: " + str(self.leftTalonSlave.getSelectedSensorVelocity(0)) + ", vright: " + str(self.rightTalonSlave.getSelectedSensorVelocity(0)))
      self.logger.info("amps_left: " + str(self.leftTalonMaster.getOutputCurrent()) + ", amps_right: " + str(self.rightTalonMaster.getOutputCurrent()))
      self.logger.info("output_left: " + str(self.leftTalonMaster.getMotorOutputPercent()) + ", output_right: " + str(self.rightTalonMaster.getMotorOutputPercent()))
    self.leftTalonMaster.set(ControlMode.PercentOutput, -1.0 * pilot_stick.getRawAxis(1))
    self.rightTalonMaster.set(ControlMode.PercentOutput, -1.0 * pilot_stick.getRawAxis(5))
    self.lift_talon.set(ControlMode.PercentOutput, copilot_stick.getRawAxis(1))

    if copilot_stick.getRawButton(3): #X
      self.drive_front_extend.set(False)
      self.drive_front_retract.set(True)
    elif copilot_stick.getRawButton(4): #Y
      self.drive_front_extend.set(True)
      self.drive_front_retract.set(False)

    if copilot_stick.getRawButton(1):  #A
      self.drive_back_extend.set(False)
      self.drive_back_retract.set(True)
    elif copilot_stick.getRawButton(2): #B
      self.drive_back_extend.set(True)
      self.drive_back_retract.set(False)

    if copilot_stick.getRawButton(5): #l-bumper
      self.lift_pneumatic_extend.set(True) 
      self.lift_pneumatic_retract.set(False)
    elif copilot_stick.getRawButton(6): #r-bumper
      self.lift_pneumatic_extend.set(False)
      self.lift_pneumatic_retract.set(True)

    if pilot_stick.getRawButton(1): #A
      self.harpoon_center_extend.set(False)
      self.harpoon_center_retract.set(True)
    elif pilot_stick.getRawButton(2): #B
      self.harpoon_center_extend.set(True)
      self.harpoon_center_retract.set(False)

    if pilot_stick.getRawButton(3):  #X
      self.harpoon_outside_extend.set(False)
      self.harpoon_outside_retract.set(True)
    elif pilot_stick.getRawButton(4): #Y
      self.harpoon_outside_extend.set(True)
      self.harpoon_outside_retract.set(False)



  def disable(self):
    self.logger.info("DeepSpaceDrive::disable()")



import wpilib
import ctre
import robotmap

class DeepSpaceDrive():

  def __init__(self, logger):
    self.logger = logger

  def init(self):
    self.logger.info("DeepSpaceDrive::init()")
    self.timer = wpilib.Timer()
    self.timer.start()

    self.leftTalonMaster = ctre.WPI_TalonSRX(robotmap.DRIVE_LEFT_MASTER_CAN_ID)
    self.leftTalonSlave = ctre.WPI_TalonSRX(robotmap.DRIVE_LEFT_SLAVE_CAN_ID)

    self.rightTalonMaster = ctre.WPI_TalonSRX(robotmap.DRIVE_RIGHT_MASTER_CAN_ID)
    self.rightTalonSlave = ctre.WPI_TalonSRX(robotmap.DRIVE_RIGHT_SLAVE_CAN_ID)

    self.talons = [self.leftTalonMaster, self.leftTalonSlave, self.rightTalonMaster, self.rightTalonSlave]

    self.drive = wpilib.RobotDrive(self.leftTalonMaster, self.rightTalonMaster)

    self.drive_front_extend = wpilib.Solenoid(robotmap.PCM1_CANID, robotmap.DRIVE_FRONT_EXTEND_SOLENOID)
    self.drive_front_retract = wpilib.Solenoid(robotmap.PCM1_CANID, robotmap.DRIVE_FRONT_RETRACT_SOLENOID)
    self.drive_back_extend = wpilib.Solenoid(robotmap.PCM1_CANID, robotmap.DRIVE_REAR_EXTEND_SOLENOID)
    self.drive_back_retract = wpilib.Solenoid(robotmap.PCM1_CANID, robotmap.DRIVE_REAR_RETRACT_SOLENOID)

  def config(self, simulation):
    self.logger.info("DeepSpaceDrive::config()")

    '''Configuration items common for all talons'''
    for talon in self.talons:
      talon.configNominalOutputForward(0.0, robotmap.CAN_TIMEOUT_MS)
      talon.configNominalOutputReverse(0.0, robotmap.CAN_TIMEOUT_MS)
      talon.configPeakOutputForward(1.0, robotmap.CAN_TIMEOUT_MS)
      talon.configPeakOutputReverse(-1.0, robotmap.CAN_TIMEOUT_MS)
      talon.enableVoltageCompensation(True)
      talon.configVoltageCompSaturation(11.5, robotmap.CAN_TIMEOUT_MS)
      talon.configOpenLoopRamp(0.125, robotmap.CAN_TIMEOUT_MS)

    self.leftTalonMaster.setInverted(False)
    self.leftTalonSlave.setInverted(False)
    self.rightTalonMaster.setInverted(True)
    self.rightTalonSlave.setInverted(True)

    self.leftTalonSlave.configSelectedFeedbackSensor(ctre.FeedbackDevice.QuadEncoder, 0, robotmap.CAN_TIMEOUT_MS)
    self.leftTalonSlave.configSelectedFeedbackCoefficient(1.0, 0, robotmap.CAN_TIMEOUT_MS)
    self.leftTalonSlave.setSensorPhase(True)
    self.leftTalonSlave.setStatusFramePeriod(ctre._impl.StatusFrame.Status_2_Feedback0, 10, robotmap.CAN_TIMEOUT_MS)
    self.leftTalonSlave.set(ctre.ControlMode.Follower, robotmap.DRIVE_LEFT_MASTER_CAN_ID)    

    self.rightTalonSlave.configSelectedFeedbackSensor(ctre.FeedbackDevice.QuadEncoder, 0, robotmap.CAN_TIMEOUT_MS)
    self.rightTalonSlave.configSelectedFeedbackCoefficient(1.0, 0, robotmap.CAN_TIMEOUT_MS)
    self.rightTalonSlave.setSensorPhase(True)
    self.rightTalonSlave.setStatusFramePeriod(ctre._impl.StatusFrame.Status_2_Feedback0, 10, robotmap.CAN_TIMEOUT_MS)
    self.rightTalonSlave.set(ctre.ControlMode.Follower, robotmap.DRIVE_RIGHT_MASTER_CAN_ID)

    self.drive_front_extend.set(False)
    self.drive_front_retract.set(True)
    self.drive_back_extend.set(False)
    self.drive_back_retract.set(True)

  def iterate(self, test_mode, pilot_stick, copilot_stick):
    if self.timer.hasPeriodPassed(0.5):
      self.logger.info("DeepSpaceDrive::iterate()")
      self.logger.info("vleft: " + str(self.leftTalonSlave.getSelectedSensorVelocity(0)) + ", vright: " + str(self.rightTalonSlave.getSelectedSensorVelocity(0)))
      self.logger.info("amps_left: " + str(self.leftTalonMaster.getOutputCurrent()) + ", amps_right: " + str(self.rightTalonMaster.getOutputCurrent()))
      self.logger.info("output_left: " + str(self.leftTalonMaster.getMotorOutputPercent()) + ", output_right: " + str(self.rightTalonMaster.getMotorOutputPercent()))
    
    self.drive.arcadeDrive(-1.0 * pilot_stick.getRawAxis(robotmap.XBOX_LEFT_Y_AXIS), pilot_stick.getRawAxis(robotmap.XBOX_LEFT_X_AXIS))

    if copilot_stick.getRawButton(robotmap.XBOX_X): #X
      self.drive_front_extend.set(False)
      self.drive_front_retract.set(True)
    elif copilot_stick.getRawButton(robotmap.XBOX_Y): #Y
      self.drive_front_extend.set(True)
      self.drive_front_retract.set(False)

    if copilot_stick.getRawButton(robotmap.XBOX_A):  #A
      self.drive_back_extend.set(False)
      self.drive_back_retract.set(True)
    elif copilot_stick.getRawButton(robotmap.XBOX_B): #B
      self.drive_back_extend.set(True)
      self.drive_back_retract.set(False)

  def disable(self):
    self.logger.info("DeepSpaceDrive::disable()")


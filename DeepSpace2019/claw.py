
import wpilib
import math
import ctre
import robotmap

class DeepSpaceClaw():

  def __init__(self, logger):
    self.logger = logger

  def init(self):
    self.logger.info("DeepSpaceClaw::init()")
    self.timer = wpilib.Timer()
    self.timer.start()

    self.stow = True

    self.ball_infrared = wpilib.DigitalInput(robotmap.BALL_IR_SENSOR)
    
    self.left_grab = ctre.TalonSRX(robotmap.CLAW_LEFT_WHEELS_CAN_ID)
    self.right_grab = ctre.TalonSRX(robotmap.CLAW_RIGHT_WHEELS_CAN_ID)
    self.wrist_talon = ctre.TalonSRX(robotmap.CLAW_WRIST_CAN_ID)

    self.talons = [self.left_grab, self.right_grab, self.wrist_talon]

    '''Select and zero sensor in init() function.  That way the zero position doesn't get reset every time we enable/disable robot'''
    self.wrist_talon.configSelectedFeedbackSensor(ctre.FeedbackDevice.Analog, 0, robotmap.CAN_TIMEOUT_MS)
    self.wrist_talon.setSelectedSensorPosition(0, 0, robotmap.CAN_TIMEOUT_MS)

    self.claw_open = wpilib.Solenoid(robotmap.PCM2_CANID, robotmap.CLAW_OPEN_SOLENOID)
    self.claw_close = wpilib.Solenoid(robotmap.PCM2_CANID, robotmap.CLAW_CLOSE_SOLENOID)

    self.claw_close.set(True)
    self.claw_open.set(False)

  def config(self, simulation):
    self.logger.info("DeepSpaceClaw::config(): ")

    '''Configuration items common for all talons'''
    for talon in self.talons:
      talon.configNominalOutputForward(0.0, robotmap.CAN_TIMEOUT_MS)
      talon.configNominalOutputReverse(0.0, robotmap.CAN_TIMEOUT_MS)
      talon.configPeakOutputForward(1.0, robotmap.CAN_TIMEOUT_MS)
      talon.configPeakOutputReverse(-1.0, robotmap.CAN_TIMEOUT_MS)
      talon.enableVoltageCompensation(True)
      talon.configVoltageCompSaturation(11.5, robotmap.CAN_TIMEOUT_MS)
      talon.configOpenLoopRamp(0.125, robotmap.CAN_TIMEOUT_MS)

    '''sensor config'''
    self.wrist_talon.configSelectedFeedbackCoefficient(1.0, 0, robotmap.CAN_TIMEOUT_MS)
    self.wrist_talon.setSensorPhase(True)
    self.wrist_talon.setStatusFramePeriod(ctre._impl.StatusFrame.Status_2_Feedback0, 10, robotmap.CAN_TIMEOUT_MS)

  def iterate(self, test_mode, pilot_stick, copilot_stick):
    if self.timer.hasPeriodPassed(0.5):
      self.logger.info("DeepSpaceClaw::iterate()")

    if pilot_stick.getRawButton(robotmap.XBOX_LEFT_BUMPER): #left bumper
      self.left_grab.set(ctre.ControlMode.PercentOutput, 0.5)
      self.right_grab.set(ctre.ControlMode.PercentOutput, -0.5)
    elif pilot_stick.getRawButton(robotmap.XBOX_RIGHT_BUMPER): #right bumper
      self.left_grab.set(ctre.ControlMode.PercentOutput, -0.5)
      self.right_grab.set(ctre.ControlMode.PercentOutput, 0.5)
    else:
      self.left_grab.set(ctre.ControlMode.PercentOutput, 0.0)
      self.right_grab.set(ctre.ControlMode.PercentOutput, 0.0)

    if pilot_stick.getRawButton(robotmap.XBOX_BACK):  #Back
      self.claw_close.set(True)
      self.claw_open.set(False)
    elif pilot_stick.getRawButton(robotmap.XBOX_START): #Start
      self.claw_close.set(False)
      self.claw_open.set(True)

    if copilot_stick.getRawButtonPressed(robotmap.XBOX_BACK): #Back
      self.stow = True
    elif copilot_stick.getRawButtonPressed(robotmap.XBOX_START): #Start
      self.stow = False

    wrist_position = self.wrist_talon.getSelectedSensorPosition(0)
    if self.stow and wrist_position > 5:
      self.wrist_talon.set(ctre.ControlMode.PercentOutput, 0.3)
    elif self.stow and wrist_position < 5:
      self.wrist_talon.set(ctre.ControlMode.PercentOutput, 0.1)
    elif not self.stow and wrist_position < 25:
      self.wrist_talon.set(ctre.ControlMode.PercentOutput, -0.1)
    else:
      self.wrist_talon.set(ctre.ControlMode.PercentOutput, 0.0)
    
    if test_mode == True:
      self.wrist_talon.set(ctre.ControlMode.PercentOutput, copilot_stick.getRawAxis(robotmap.XBOX_RIGHT_Y_AXIS))

  def disable(self):
    self.logger.info("DeepSpaceClaw::disable()")
    self.wrist_talon.set(ctre.ControlMode.PercentOutput, 0.0)
    self.left_grab.set(ctre.ControlMode.PercentOutput, 0.0)
    self.right_grab.set(ctre.ControlMode.PercentOutput, 0.0)


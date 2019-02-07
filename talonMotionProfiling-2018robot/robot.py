import math
import wpilib

import pathfinder as pf
import navx
import ctre

class MyRobot(wpilib.TimedRobot):
  
  WHEEL_DIAMETER = 0.5  # 6 inches
  ENCODER_COUNTS_PER_REV = 4096

  # Pathfinder constants
  MAX_VELOCITY = 48  # in/s
  MAX_ACCELERATION = 24 #in/s/s

  TIMEOUT_MS = 10 #milliseconds

  PIGEON_UNITS_PER_ROTATION = 8192

  def robotInit(self):
    self.timer = wpilib.Timer()
    self.timer.start()

    self.leftTalonMaster = ctre.TalonSRX(3)
    self.leftTalonSlave = ctre.TalonSRX(4)

    self.rightTalonMaster = ctre.TalonSRX(1)
    self.rightTalonSlave = ctre.TalonSRX(2)
    
    self.leftTalonSlave.set(ControlMode.Follower, 3)
    self.rightTalonSlave.set(ControlMode.Follower, 1)

    self.masterTalons = [self.leftTalonMaster, self.rightTalonMaster]
    self.slaveTalons = [self.leftTalonSlave, self.rightTalonSlave]

    self.leftTalons = [self.leftTalonMaster, self.leftTalonSlave]
    self.rightTalons = [self.rightTalonMaster, self.rightTalonSlave]

    self.talons = [self.leftTalonMaster, self.leftTalonSlave, self.rightTalonMaster, self.rightTalonSlave]

    for talon in self.talons:
      talon.configureNominalOutputForward(0.0, TIMEOUT_MS)
      talon.configNominalOutputReverse(0.0, TIMEOUT_MS)
      talon.configPeakOutputForward(1.0, TIMEOUT_MS)
      talon.configPeakOutputReverse(-1.0, TIMEOUT_MS)

      talon.enableVoltageCompensation(True)
      talon.configVoltageCompSaturation(11.5, TIMEOUT_MS) #Need nominal output voltage
      talon.configOpenloopRamp(0.125, TIMEOUT_MS) #Need ramp rate

    for talon in self.leftTalons:
      talon.setInverted(True)

    for talon in self.masterTalons:
      talon.configRemoteFeedbackFilter(5, RemoteSensorSource.GadgeteerPigeon_Yaw, 1, TIMEOUT_MS)

      talon.configSelectedFeedbackSensor(FeedbackDevice.RemoteSensor0, 0, TIMEOUT_MS)
      talon.configSelectedFeedbackSensor(FeedbackDevice.RemoteSensor1, 1, TIMEOUT_MS)
      talon.configSelectedFeedbackCoefficient(1.0, 0, TIMEOUT_MS)
      talon.configSelectedFeedbackCoefficient(3600 / PIGEON_UNITS_PER_ROTATION, 1, TIMEOUT_MS)

      talon.configMotionAcceleration(((MAX_ACCELERATION * ENCODER_COUNTS_PER_REV) / (math.pi * WHEEL_DIAMETER)) / 10, 10)
      talon.configMotionCruiseVelocity(((MAX_VELOCITY * ENCODER_COUNTS_PER_REV) / (math.pi * WHEEL_DIAMETER)) / 10, 10)
      talon.configMotionProfileTrajectoryPeriod(20, TIMEOUT_MS)

      if talon is self.rightTalonMaster:
        talon.setSensorPhase(True)
        talon.configAuxPIDPolarity(False, TIMEOUT_MS)

      if talon is self.leftTalonMaster:
        talon.setSensorPhase(False)
        talon.configAuxPIDPolarity(True, TIMEOUT_MS)
  
    self.pigeon = ctre.PigeonIMU(3)
    self.pigeon.setStatusFramePeriod(Pigeon_IMU_StatusFrame.CondStatus_9_SixDeg_YPR, 5, TIMEOUT_MS)
      
import math
import wpilib

import pathfinder as pf
import navx
from ctre import *

class MyRobot(wpilib.TimedRobot):
  
  WHEEL_DIAMETER = 0.5  # 6 inches
  ENCODER_COUNTS_PER_REV = 4096

  # Pathfinder constants
  MAX_VELOCITY = 48  # in/s
  MAX_ACCELERATION = 24 #in/s/s
  MAX_JERK = 120 #in/s/s/s

  TIMEOUT_MS = 10 #milliseconds

  PIGEON_UNITS_PER_ROTATION = 8192

  TALON_MOTIONPROFILE_SLOT = 2
  TALON_GYRO_SLOT = 1

  VELOCITY_MULTIPLIER = 1

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
      talon.configureNominalOutputForward(0.0, self.TIMEOUT_MS)
      talon.configNominalOutputReverse(0.0, self.TIMEOUT_MS)
      talon.configPeakOutputForward(1.0, self.TIMEOUT_MS)
      talon.configPeakOutputReverse(-1.0, self.TIMEOUT_MS)

      talon.enableVoltageCompensation(True)
      talon.configVoltageCompSaturation(11.5, self.TIMEOUT_MS) #Need nominal output voltage
      talon.configOpenloopRamp(0.125, self.TIMEOUT_MS) #Need ramp rate

    for talon in self.leftTalons:
      talon.setInverted(True)
    
    for talon in self.masterTalons:
      talon.configRemoteFeedbackFilter(5, RemoteSensorSource.GadgeteerPigeon_Yaw, 1, self.TIMEOUT_MS)

      talon.configSelectedFeedbackSensor(FeedbackDevice.RemoteSensor0, 0, self.TIMEOUT_MS)
      talon.configSelectedFeedbackSensor(FeedbackDevice.RemoteSensor1, 1, self.TIMEOUT_MS)
      talon.configSelectedFeedbackCoefficient(1.0, 0, self.TIMEOUT_MS)
      talon.configSelectedFeedbackCoefficient(3600 / self.PIGEON_UNITS_PER_ROTATION, 1, self.TIMEOUT_MS)

      talon.configMotionAcceleration(((MAX_ACCELERATION * self.ENCODER_COUNTS_PER_REV) / (math.pi * self.WHEEL_DIAMETER)) / 10, 10)
      talon.configMotionCruiseVelocity(((MAX_VELOCITY * self.ENCODER_COUNTS_PER_REV) / (math.pi * self.WHEEL_DIAMETER)) / 10, 10)
      talon.configMotionProfileTrajectoryPeriod(20, self.TIMEOUT_MS)

      if talon is self.rightTalonMaster:
        talon.setSensorPhase(True)
        talon.configAuxPIDPolarity(False, self.TIMEOUT_MS)

      if talon is self.leftTalonMaster:
        talon.setSensorPhase(False)
        talon.configAuxPIDPolarity(True, self.TIMEOUT_MS)

    self.pigeon = PigeonIMU(3)
    self.pigeon.setStatusFramePeriod(Pigeon_IMU_StatusFrame.CondStatus_9_SixDeg_YPR, 5, self.TIMEOUT_MS)

  def autonomousInit(self):
    self.robot_drive.setSafetyEnabled(False)

    self.pigeon.setYaw(0, self.TIMEOUT_MS)
    self.pigeon.setFusedHeading(0, self.TIMEOUT_MS)
    #self.pigeon.setCompassAngle(0, self.TIMEOUT_MS)

    self.leftTalonMaster.setSelectedSensorPosition(0, 0, self.TIMEOUT_MS)
    self.leftTalonMaster.getSensorCollection().setQuadraturePosition(0, self.TIMEOUT_MS)
    self.leftTalonMaster.clearMotionProfileTrajectories()
    self.leftTalonMaster.clearMotionProfileHasUnderrun(0)
    self.leftTalonMaster.set(ControlMode.MotionProfileArc, SetValueMotionProfile.Disable.value)

    self.rightTalonMaster.setSelectedSensorPosition(0, 0, self.TIMEOUT_MS)
    self.rightTalonMaster.getSensorCollection().setQuadraturePosition(0, self.TIMEOUT_MS)
    self.rightTalonMaster.clearMotionProfileTrajectories()
    self.rightTalonMaster.clearMotionProfileHasUnderrun(0)
    self.rightTalonMaster.set(ControlMode.MotionProfileArc, SetValueMotionProfile.Disable.value)

    self.leftMPStatus = MotionProfileStatus()
    self.rightMPStatus = MotionProfileStatus()

    points = [pf.Waypoint(0, 0, 0), pf.Waypoint(9, 5, 0)]

    info, trajectory = pf.generate(
      points,
      pf.FIT_HERMITE_CUBIC,
      pf.SAMPLES_HIGH,
      dt=self.getPeriod(),
      max_velocity=self.MAX_VELOCITY / 12, #converting from inches to feet
      max_acceleration=self.MAX_ACCELERATION / 12,
      max_jerk=self.MAX_JERK / 12
    )

    modifier = pf.modifiers.TankModifier(trajectory).modify(2.1) #Wheelbase in feet

    self.leftTrajectory = modifier.getLeftTrajectory()
    self.rightTrajectory = modifier.getRightTrajectory()

    for i in range(len(trajectory.segments)):
      leftSeg = self.leftTrajectory.segments[i]
      rightSeg = self.rightTrajectory.segments[i]

      velCorrection = (rightSeg.velocity - leftSeg.velocity) * self.VELOCITY_MULTIPLIER

      self.leftTrajectory[i] = TrajectoryPoint()
      self.rightTrajectory[i] = TrajectoryPoint()

      self.leftTrajectory[i].position = self.rightTrajectory[i].position = (((leftSeg.position + rightSeg.position) * 12) * self.ENCODER_COUNTS_PER_REV) / (math.pi * self.WHEEL_DIAMETER)
      self.leftTrajectory[i].auxiliaryPos = self.rightTrajectory[i].auxiliaryPos = 10 * math.degrees(leftSeg.heading)
      self.leftTrajectory[i].profileSlotSelect0 = self.rightTrajectory[i].profileSelect0 = self.TALON_MOTIONPROFILE_SLOT
      self.leftTrajectory[i].profileSlotSelect1 = self.rightTrajectory[i].profileSelect1 = self.TALON_GYRO_SLOT
      self.leftTrajectory[i].timeDur = self.rightTrajectory[i].timeDur = TrajectoryPoint.TrajectoryDuration.Trajectory_Duration_0ms
      self.leftTrajectory[i].zeroPos = rightTrajectory[i].zeroPos = i == 0
      self.leftTrajectory[i].isLastPoint = rightTrajectory[i].isLastPoint = i == len(trajectory.segments) - 1

      self.leftTrajectory[i].velocity = (((leftSeg.velocity - velCorrection) * 12) * self.ENCODER_COUNTS_PER_REV) / (math.pi * self.WHEEL_DIAMETER) / 10
      self.rightTrajectory[i].velocity = (((rightSeg.velocity + velCorrection) * 12) * self.ENCODER_COUNTS_PER_REV) / (math.pi * self.WHEEL_DIAMETER) / 10

    for point in self.leftTrajectory:
      self.leftTalons.pushMotionProfileTrajectory(point)

    for point in self.rightTrajectory:
      self.rightTalons.pushMotionProfileTrajectory(point)

    self.leftDone = False
    self.rightDone = False

  def autonomousPeriodic(self):
    self.leftTalonMaster.getMotionProfileStatus(self.leftMPStatus)
    self.rightTalonMaster.getMotionProfileStatus(self.rightMPStatus)

    self.leftTalonMaster.set(ControlMode.MotionProfileArc, SetValueMotionProfile.Enable.value)
    self.rightTalonMaster.set(ControlMode.MotionProfileArc, SetValueMotionProfile.Enable.value)

    if self.leftMPStatus.isLast and self.leftMPStatus.outPutEnable == SetValueMotionProfile.Enable and not self.leftDone:
      self.leftTalonMaster.neutralOutput()
      self.leftTalonMaster.set(ControlMode.PercentOutput, 0)
      self.leftDone = True

    if self.rightMPStatus.isLast and self.rightMPStatus.outPutEnable == SetValueMotionProfile.Enable and not self.rightDone:
      self.rightTalonMaster.neutralOutput()
      self.rightTalonMaster.set(ControlMode.PercentOutput, 0)
      self.rightDone = True

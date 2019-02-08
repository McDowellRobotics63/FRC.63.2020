import math
import wpilib

import pathfinder as pf
import navx

#from ctre import TalonSRX
#from ctre import TrajectoryPoint
#from ctre import PigeonIMU
#from ctre.pigeonimu import PigeonIMU_StatusFrame
from ctre.pigeonimu import *
from ctre import *
from ctre import TrajectoryPoint
from ctre._impl import *

class MyRobot(wpilib.TimedRobot):
  
  WHEEL_DIAMETER = 0.5  # 6 inches
  WHEEL_CIRCUMFERENCE = math.pi * WHEEL_DIAMETER
  
  # Pathfinder constants
  MAX_VELOCITY = 48  # in/s
  MAX_ACCELERATION = 24 #in/s/s
  MAX_JERK = 120 #in/s/s/s

  CAN_BUS_TIMEOUT_MS = 10

  ENCODER_COUNTS_PER_REV = 4096
  PIGEON_UNITS_PER_ROTATION = 8192

  TALON_MOTIONPROFILE_SLOT = 2
  TALON_GYRO_SLOT = 1

  LEFT_MASTER_CAN_ID = 3
  RIGHT_MASTER_CAN_ID = 1
  LEFT_SLAVE_CAN_ID = 4
  RIGHT_SLAVE_CAN_ID = 2
  PIGEON_IMU_CAN_ID = 5

  PRIMARY_PID_LOOP = 0
  AUX_PID_LOOP = 1

  BASE_TRAJECTORY_PERIOD_MS = 20

  VELOCITY_MULTIPLIER = 1

  def robotInit(self):
    self.timer = wpilib.Timer()
    self.timer.start()

    self.stick = wpilib.Joystick(0)

    self.leftTalonMaster = TalonSRX(self.LEFT_MASTER_CAN_ID)
    self.leftTalonSlave = TalonSRX(self.LEFT_SLAVE_CAN_ID)

    self.rightTalonMaster = TalonSRX(self.RIGHT_MASTER_CAN_ID)
    self.rightTalonSlave = TalonSRX(self.RIGHT_SLAVE_CAN_ID)
    
    self.leftTalonSlave.set(ControlMode.Follower, self.LEFT_MASTER_CAN_ID)
    self.rightTalonSlave.set(ControlMode.Follower, self.RIGHT_MASTER_CAN_ID)

    self.masterTalons = [self.leftTalonMaster, self.rightTalonMaster]
    self.slaveTalons = [self.leftTalonSlave, self.rightTalonSlave]

    self.leftTalons = [self.leftTalonMaster, self.leftTalonSlave]
    self.rightTalons = [self.rightTalonMaster, self.rightTalonSlave]

    self.talons = [self.leftTalonMaster, self.leftTalonSlave, self.rightTalonMaster, self.rightTalonSlave]

    for talon in self.talons:
      talon.configureNominalOutputForward(0.0, self.CAN_BUS_TIMEOUT_MS)
      talon.configNominalOutputReverse(0.0, self.CAN_BUS_TIMEOUT_MS)
      talon.configPeakOutputForward(1.0, self.CAN_BUS_TIMEOUT_MS)
      talon.configPeakOutputReverse(-1.0, self.CAN_BUS_TIMEOUT_MS)

      talon.enableVoltageCompensation(True)
      talon.configVoltageCompSaturation(11.5, self.CAN_BUS_TIMEOUT_MS) #Need nominal output voltage
      talon.configOpenloopRamp(0.125, self.CAN_BUS_TIMEOUT_MS) #Need ramp rate

    for talon in self.leftTalons:
      talon.setInverted(True)
    
    for talon in self.masterTalons:
      talon.configRemoteFeedbackFilter(5, RemoteSensorSource.GadgeteerPigeon_Yaw, 1, self.CAN_BUS_TIMEOUT_MS)

      talon.configSelectedFeedbackSensor(FeedbackDevice.RemoteSensor0, 0, self.CAN_BUS_TIMEOUT_MS)
      talon.configSelectedFeedbackSensor(FeedbackDevice.RemoteSensor1, 1, self.CAN_BUS_TIMEOUT_MS)
      talon.configSelectedFeedbackCoefficient(1.0, 0, self.CAN_BUS_TIMEOUT_MS)
      talon.configSelectedFeedbackCoefficient(3600 / self.PIGEON_UNITS_PER_ROTATION, 1, self.CAN_BUS_TIMEOUT_MS)

      talon.configMotionAcceleration(((self.MAX_ACCELERATION * self.ENCODER_COUNTS_PER_REV) / (math.pi * self.WHEEL_DIAMETER)) / 10, 10)
      talon.configMotionCruiseVelocity(((self.MAX_VELOCITY * self.ENCODER_COUNTS_PER_REV) / (math.pi * self.WHEEL_DIAMETER)) / 10, 10)
      talon.configMotionProfileTrajectoryPeriod(self.BASE_TRAJECTORY_PERIOD_MS, self.CAN_BUS_TIMEOUT_MS)

      if talon is self.rightTalonMaster:
        talon.setSensorPhase(True)
        talon.configAuxPIDPolarity(False, self.CAN_BUS_TIMEOUT_MS)

      if talon is self.leftTalonMaster:
        talon.setSensorPhase(False)
        talon.configAuxPIDPolarity(True, self.CAN_BUS_TIMEOUT_MS)

    self.pigeon = PigeonIMU(self.PIGEON_IMU_CAN_ID)
    self.pigeon.setStatusFramePeriod(PigeonIMU_StatusFrame.CondStatus_9_SixDeg_YPR, 5, self.CAN_BUS_TIMEOUT_MS)

  def autonomousInit(self):
    #self.robot_drive.setSafetyEnabled(False)

    self.pigeon.setYaw(0, self.CAN_BUS_TIMEOUT_MS)
    self.pigeon.setFusedHeading(0, self.CAN_BUS_TIMEOUT_MS)
    #self.pigeon.setCompassAngle(0, self.TIMEOUT_MS)

    self.leftTalonMaster.setSelectedSensorPosition(0, 0, self.CAN_BUS_TIMEOUT_MS)
    self.leftTalonMaster.getSensorCollection().setQuadraturePosition(0, self.CAN_BUS_TIMEOUT_MS)
    self.leftTalonMaster.clearMotionProfileTrajectories()
    self.leftTalonMaster.clearMotionProfileHasUnderrun(0)
    self.leftTalonMaster.set(ControlMode.MotionProfileArc, SetValueMotionProfile.Disable.value)

    self.rightTalonMaster.setSelectedSensorPosition(0, 0, self.CAN_BUS_TIMEOUT_MS)
    self.rightTalonMaster.getSensorCollection().setQuadraturePosition(0, self.CAN_BUS_TIMEOUT_MS)
    self.rightTalonMaster.clearMotionProfileTrajectories()
    self.rightTalonMaster.clearMotionProfileHasUnderrun(0)
    self.rightTalonMaster.set(ControlMode.MotionProfileArc, SetValueMotionProfile.Disable.value)

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
      self.leftTrajectory[i].timeDur = self.rightTrajectory[i].timeDur = 0
      self.leftTrajectory[i].zeroPos = self.rightTrajectory[i].zeroPos = i == 0
      self.leftTrajectory[i].isLastPoint = self.rightTrajectory[i].isLastPoint = i == len(trajectory.segments) - 1

      self.leftTrajectory[i].velocity = (((leftSeg.velocity - velCorrection) * 12) * self.ENCODER_COUNTS_PER_REV) / (math.pi * self.WHEEL_DIAMETER) / 10
      self.rightTrajectory[i].velocity = (((rightSeg.velocity + velCorrection) * 12) * self.ENCODER_COUNTS_PER_REV) / (math.pi * self.WHEEL_DIAMETER) / 10

    for point in self.leftTrajectory:
      self.leftTalonMaster.pushMotionProfileTrajectory(point)

    for point in self.rightTrajectory:
      self.rightTalonMaster.pushMotionProfileTrajectory(point)

    self.leftDone = False
    self.rightDone = False
    self.motionProfileEnabled = False
    self.bufferProcessingStartTime = 0
    self.executionStartTime = 0
    self.executionFinishTime = 0

  def autonomousPeriodic(self):
    self.leftMPStatus = self.leftTalonMaster.getMotionProfileStatus()
    self.rightMPStatus = self.rightTalonMaster.getMotionProfileStatus()

    '''
    The processMotionProfileBuffer() moves trajectory points from the
    "Top" level buffer into the "Bottom" level buffer.  This just means
    they are moved from a buffer inside the roboRIO into a buffer inside
    the Talon firmware itself.  The more sophisticated method is to call
    this function on a seperate background thread which is running at a rate which
    is twice as fast as the duration of the trajectory points.  Then in the main thread
    check that the bottom buffer count is high enough to trigger the motion
    profile execution to begin.  That allows the motion profile execution to
    begin sooner.  For this test we can just wait until the top buffer has
    been completely emptied into the bottom buffer.
    '''

    '''Let's time this to see if it's really worth doing it the more sophisticated way'''
    if self.leftMPStatus.btmBufferCnt == 0 and self.rightMPStatus.btmBufferCnt == 0:
      print("Beginning to funnel trajectory points into the Talons")
      self.bufferProcessingStartTime = self.timer.getFPGATimestamp()

    '''
    Don't print anything while funneling points into the Talons.
    Printing will slow down execution and we want to measure time
    that it took to do this operation.
    '''
    if self.leftMPStatus.topBufferCnt > 0:
      self.leftTalonMaster.processMotionProfileBuffer()

    if self.rightMPStatus.topBufferCnt > 0:
      self.rightTalonMaster.processMotionProfileBuffer()

    if not self.motionProfileEnabled and \
       self.leftMPStatus.btmBufferCnt > 0 and self.leftMPStatus.topBufferCnt == 0 and \
       self.rightMPStatus.btmBufferCnt > 0 and self.rightMPStatus.topBufferCnt == 0:
      self.leftTalonMaster.set(ControlMode.MotionProfileArc, SetValueMotionProfile.Enable.value)
      self.rightTalonMaster.set(ControlMode.MotionProfileArc, SetValueMotionProfile.Enable.value)
      self.motionProfileEnabled = True
      self.executionStartTime = self.timer.getFPGATimestamp()
      print("Beginning motion profile execution")

    if self.leftMPStatus.isLast and self.leftMPStatus.outputEnable == SetValueMotionProfile.Enable and not self.leftDone:
      self.leftTalonMaster.neutralOutput()
      self.leftTalonMaster.set(ControlMode.PercentOutput, 0)
      self.leftDone = True
      print("Left motion profile is finished executing")

    if self.rightMPStatus.isLast and self.rightMPStatus.outputEnable == SetValueMotionProfile.Enable and not self.rightDone:
      self.rightTalonMaster.neutralOutput()
      self.rightTalonMaster.set(ControlMode.PercentOutput, 0)
      self.rightDone = True
      print("Right motion profile is finished executing")


    '''
    It's ok to print debug info on every loop here because the execution
    is all happening inside the Talon firmware. However... continuosly
    calling into the Talons to get profile status, output percent, closed loop error etc
    may cause too much loading on the Talon firware or too much traffic on the
    CAN bus network... so maybe need to be careful with that.
    '''
    if not self.leftDone or not self.rightDone:
      print(f'\
        ****************************************\n\
         Points Remaining <{self.leftMPStatus.btmBufferCnt}, {self.rightMPStatus.btmBufferCnt}>\n\
         Motor Output <{self.leftTalonMaster.getMotorOutputPercent()}, {self.rightTalonMaster.getMotorOutputPercent()}>\n\
         Underrun <{self.leftMPStatus.hasUnderrun}, {self.rightMPStatus.hasUnderrun}>\n\
         Closed Loop Error <\
{self.leftTalonMaster.getClosedLoopError(self.PRIMARY_PID_LOOP)}, \
{self.rightTalonMaster.getClosedLoopError(self.PRIMARY_PID_LOOP)}, \
{self.rightTalonMaster.getClosedLoopError(self.AUX_PID_LOOP)}>\n\
        ****************************************\n\
        ')
    else:
      self.executionFinishTime = self.timer.getFPGATimestamp()
      print("Both Left and Right motion profiles are finished executing")
      print(f'Buffer fill time: {self.executionStartTime - self.bufferProcessingStartTime}')
      print(f'Profile exec time: {self.executionFinishTime - self.executionStartTime}')

  def teleopInit(self):
      print("MODE: teleopInit")

  def teleopPeriodic(self):
    if self.timer.hasPeriodPassed(0.25):
      ypr = self.pigeon.getYawPitchRoll()

      print(f'\
        *************teleopPeriodic*************\n\
         Sticks <{self.stick.getRawAxis(1)}, {self.stick.getRawAxis(5)}>\n\
         Motor Output % <{self.leftTalonMaster.getMotorOutputPercent()}, {self.rightTalonMaster.getMotorOutputPercent()}>\n\
         Ticks per 100ms <{self.leftTalonMaster.getQuadratureVelocity()}, {self.rightTalonMaster.getQuadratureVelocity()}>\n\
         Left/Right Speed (in/sec) <\
{self.unitsToInches(self.leftTalonMaster.getQuadratureVelocity()) * 10}, \
{self.unitsToInches(self.rightTalonMaster.getQuadratureVelocity()) * 10}>\n\
         Primary/Aux Feedback<\
{self.unitsToInches(self.rightTalonMaster.getSelectedSensorVelocity(self.PRIMARY_PID_LOOP))}, \
{self.unitsToInches(self.rightTalonMaster.getSelectedSensorVelocity(self.AUX_PID_LOOP))}>\n\
         Yaw/Pitch/Roll <{ypr[0]}, {ypr[1]}, {ypr[2]}>\n\
        ****************************************\n\
        ')

    self.leftTalonMaster.set(ControlMode.PercentOutput, -1.0 * self.stick.getRawAxis(1))
    self.rightTalonMaster.set(ControlMode.PercentOutput, -1.0 * self.stick.getRawAxis(5))

  def disabledInit(self):
    print("MODE: teleopInit")

  def disabledPeriodic(self):
    if self.timer.hasPeriodPassed(1.0):
      print("MODE: disabledPeriodic")

  def unitsToInches(self, units):
    return units * self.WHEEL_CIRCUMFERENCE / self.ENCODER_COUNTS_PER_REV

  def inchesToUnits(self, inches):
    return inches * self.ENCODER_COUNTS_PER_REV / self.WHEEL_CIRCUMFERENCE

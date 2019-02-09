import math
import wpilib

import pathfinder as pf

import pickle

from ctre.pigeonimu import PigeonIMU
from ctre.pigeonimu import PigeonIMU_StatusFrame

from ctre import TalonSRX
from ctre import ControlMode
from ctre import TrajectoryPoint
from ctre import FeedbackDevice
from ctre import RemoteSensorSource
from ctre import SetValueMotionProfile
from ctre._impl import StatusFrame # why ctre._impl??

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
  PIGEON_IMU_CAN_ID = 6

  PRIMARY_PID_LOOP_GAINS_SLOT = 0
  AUX_PID_LOOP_GAINS_SLOT = 1

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

    self.pigeon = PigeonIMU(self.PIGEON_IMU_CAN_ID)

    if not self.isSimulation():
      self.pigeon.setStatusFramePeriod(PigeonIMU_StatusFrame.CondStatus_9_SixDeg_YPR, 5, self.CAN_BUS_TIMEOUT_MS)
    else:
      print("setStatusFramePeriod() is not implmented in pyfrc simulator")

    self.masterTalons = [self.leftTalonMaster, self.rightTalonMaster]
    self.slaveTalons = [self.leftTalonSlave, self.rightTalonSlave]

    self.leftTalons = [self.leftTalonMaster, self.leftTalonSlave]
    self.rightTalons = [self.rightTalonMaster, self.rightTalonSlave]

    self.talons = [self.leftTalonMaster, self.leftTalonSlave, self.rightTalonMaster, self.rightTalonSlave]

    '''Common configuration items common for all talons'''
    for talon in self.talons:
      talon.configNominalOutputForward(0.0, self.CAN_BUS_TIMEOUT_MS)
      talon.configNominalOutputReverse(0.0, self.CAN_BUS_TIMEOUT_MS)

      talon.configPeakOutputForward(1.0, self.CAN_BUS_TIMEOUT_MS)
      talon.configPeakOutputReverse(-1.0, self.CAN_BUS_TIMEOUT_MS)

      talon.enableVoltageCompensation(True)
      talon.configVoltageCompSaturation(11.5, self.CAN_BUS_TIMEOUT_MS)
      
      talon.configOpenLoopRamp(0.125, self.CAN_BUS_TIMEOUT_MS)

    '''
    Left and right master talons must be setup for direct encoder input.
    Do left and right config separately instead of looping thru "master talons"
    in case we need to setSensorPhase differently for left and right.
    '''    
    self.leftTalonMaster.configSelectedFeedbackSensor(FeedbackDevice.CTRE_MagEncoder_Relative, self.PRIMARY_PID_LOOP, self.CAN_BUS_TIMEOUT_MS)
    '''This sets the scale factor on the feedback sensor.  For the encoders it is 1.0, this is really used for the gyro (pigeon) feedback'''
    self.leftTalonMaster.configSelectedFeedbackCoefficient(1.0, self.PRIMARY_PID_LOOP, self.CAN_BUS_TIMEOUT_MS)
    self.leftTalonMaster.setSensorPhase(True)
    '''This sets the rate at which this feedback gets updated to 10 ms'''
    self.leftTalonMaster.setStatusFramePeriod(StatusFrame.Status_2_Feedback0, 10, self.CAN_BUS_TIMEOUT_MS)

    self.rightTalonMaster.configSelectedFeedbackSensor(FeedbackDevice.CTRE_MagEncoder_Relative, self.PRIMARY_PID_LOOP, self.CAN_BUS_TIMEOUT_MS)
    '''This sets the scale factor on the feedback sensor.  For the encoders it is 1.0, this is really used for the gyro (pigeon) feedback'''
    self.rightTalonMaster.configSelectedFeedbackCoefficient(1.0, self.PRIMARY_PID_LOOP, self.CAN_BUS_TIMEOUT_MS)
    self.rightTalonMaster.setSensorPhase(False) #Based on pathfinder-2018robot project
    '''This sets the rate at which this feedback gets updated to 10 ms'''
    self.rightTalonMaster.setStatusFramePeriod(StatusFrame.Status_2_Feedback0, 10, self.CAN_BUS_TIMEOUT_MS)

    '''
    We are going to use the left slave talon to own the "sum" feedback sensor.
    (I think)This means it will use the left and right encoder sensor which are connected
    to the master talons as remote sensors and it will sum (average?) their output.
    '''
    if not self.isSimulation():
      '''Set encoder connected to left master as remote sensor 0'''
      self.leftTalonSlave.configRemoteFeedbackFilter(self.leftTalonMaster, RemoteSensorSource.TalonSRX_SelectedSensor, 0, self.CAN_BUS_TIMEOUT_MS)
      '''Set encoder connected to right master as remote sensor 1'''
      self.leftTalonSlave.configRemoteFeedbackFilter(self.rightTalonMaster, RemoteSensorSource.TalonSRX_SelectedSensor, 1, self.CAN_BUS_TIMEOUT_MS)
    else:
      print("configRemoteFeedbackFilter() is not implemented in pyfrc simulator")

    '''Set remote sensor 0 as first term in sensor sum'''
    self.leftTalonSlave.configSensorTerm(0, FeedbackDevice.RemoteSensor0, self.CAN_BUS_TIMEOUT_MS) #SensorTerm.Sum0 is not defined??
    '''Set remote sensor 1 as second term in sensor sum'''
    self.leftTalonSlave.configSensorTerm(1, FeedbackDevice.RemoteSensor1, self.CAN_BUS_TIMEOUT_MS) #SensorTerm.Sum1 is not defined??
    '''This sets the sum we just setup as the selected sensor for this device.  So we can use it remotely.'''
    self.leftTalonSlave.configSelectedFeedbackSensor(FeedbackDevice.SensorSum, self.PRIMARY_PID_LOOP, self.CAN_BUS_TIMEOUT_MS)   
    '''This sets the scale factor on the feedback sensor.  For the encoders it is 1.0, this is really used for the gyro (pigeon) feedback'''
    self.leftTalonSlave.configSelectedFeedbackCoefficient(1.0, self.PRIMARY_PID_LOOP, self.CAN_BUS_TIMEOUT_MS)
    '''This sets the rate at which this feedback gets updated to 10 ms'''
    self.leftTalonSlave.setStatusFramePeriod(StatusFrame.Status_2_Feedback0, 10, self.CAN_BUS_TIMEOUT_MS)

    '''Based on pathfinder-2018robot project I think none of the talon should be setInverted(True)'''
    #for talon in self.leftTalons:
      #talon.setInverted(True)

    '''
    Now that the sensor sum remote sensor is setup, we can setup the master talons close-loop configuration
    '''
    for talon in self.masterTalons:
      '''
      This just loads the constants into "slots".
      Later we will select the slots to use for the primary and aux PID loops.
      '''
      talon.config_kP(self.PRIMARY_PID_LOOP_GAINS_SLOT, 0.375, self.CAN_BUS_TIMEOUT_MS)
      talon.config_kI(self.PRIMARY_PID_LOOP_GAINS_SLOT, 0.0, self.CAN_BUS_TIMEOUT_MS)
      talon.config_kD(self.PRIMARY_PID_LOOP_GAINS_SLOT, 0.0, self.CAN_BUS_TIMEOUT_MS)
      talon.config_kF(self.PRIMARY_PID_LOOP_GAINS_SLOT, 0.35, self.CAN_BUS_TIMEOUT_MS)

      talon.config_kP(self.AUX_PID_LOOP_GAINS_SLOT, 7.0, self.CAN_BUS_TIMEOUT_MS)
      talon.config_kI(self.AUX_PID_LOOP_GAINS_SLOT, 0.0, self.CAN_BUS_TIMEOUT_MS)
      talon.config_kD(self.AUX_PID_LOOP_GAINS_SLOT, 8.0, self.CAN_BUS_TIMEOUT_MS)
      talon.config_kF(self.AUX_PID_LOOP_GAINS_SLOT, 0.0, self.CAN_BUS_TIMEOUT_MS)

      '''
      Select the gains to use for the position control loop.
      It probably doesn't matter what we select here since each individual trajectory point
      has a setting for the primary and aux PID fains to use.
      Selecting these gains here would be important if we were using motion magic control.
      '''
      talon.selectProfileSlot(self.PRIMARY_PID_LOOP_GAINS_SLOT, self.PRIMARY_PID_LOOP)
      '''This says the position control loop is allowed to command full motor output'''
      talon.configClosedLoopPeakOutput(self.PRIMARY_PID_LOOP, 1.0, self.CAN_BUS_TIMEOUT_MS)

      '''
      Select the gains to use for the heading control loop.
      It probably doesn't matter what we select here since each individual trajectory point
      has a setting for the primary and aux PID fains to use.
      Selecting these gains here would be important if we were using motion magic control.
      '''
      talon.selectProfileSlot(self.AUX_PID_LOOP_GAINS_SLOT, self.AUX_PID_LOOP)
      '''This says the heading control loop is allowed to command full motor output'''
      talon.configClosedLoopPeakOutput(self.AUX_PID_LOOP, 1.0, self.CAN_BUS_TIMEOUT_MS)

      if not self.isSimulation():
        '''Setup the "sum" sensor as remote sensor 0'''
        talon.configRemoteFeedbackFilter(self.leftTalonSlave.getDeviceID(), RemoteSensorSource.TalonSRX_SelectedSensor, 0, self.CAN_BUS_TIMEOUT_MS)
        '''Setup the pigeon as remote sensor 1'''
        talon.configRemoteFeedbackFilter(self.pigeon.getDeviceID(), RemoteSensorSource.GadgeteerPigeon_Yaw, 1, self.CAN_BUS_TIMEOUT_MS)
      else:
        print("configRemoteFeedbackFilter() is not implemented in pyfrc simulator")

      '''Select remote sensor 0 (the "sum" sensor) as the feedback for the primary PID loop (position control loop)'''
      talon.configSelectedFeedbackSensor(FeedbackDevice.RemoteSensor0, self.PRIMARY_PID_LOOP, self.CAN_BUS_TIMEOUT_MS)
      '''Select remote sensor 1 (the pigeon) as the feedback for the aux PID loop (heading control loop)'''
      talon.configSelectedFeedbackSensor(FeedbackDevice.RemoteSensor1, self.AUX_PID_LOOP, self.CAN_BUS_TIMEOUT_MS)
      '''This sets the scale factor on the feedback sensor.  For the encoders it is 1.0, this is really used for the gyro (pigeon) feedback'''
      talon.configSelectedFeedbackCoefficient(1.0, self.PRIMARY_PID_LOOP, self.CAN_BUS_TIMEOUT_MS)
      '''This sets the scale factor on the feedback sensor.  Finally we use something other than 1.0'''
      talon.configSelectedFeedbackCoefficient(3600 / self.PIGEON_UNITS_PER_ROTATION, self.AUX_PID_LOOP, self.CAN_BUS_TIMEOUT_MS)

    if not self.isSimulation():
      self.leftTalonMaster.configAuxPIDPolarity(True, self.CAN_BUS_TIMEOUT_MS)
      self.rightTalonMaster.configAuxPIDPolarity(False, self.CAN_BUS_TIMEOUT_MS)
    else:
      print("configAuxPIDPolarity() is not implemented in pyfrc simulator")

  def autonomousInit(self):
    if not self.isSimulation():
      self.pigeon.setYaw(0, self.CAN_BUS_TIMEOUT_MS)
      self.pigeon.setFusedHeading(0, self.CAN_BUS_TIMEOUT_MS)
    else:
      print("pigeon.setYaw() is not implemented in pyfrc simulator")
    
    if not self.isSimulation():
      self.leftTalonMaster.setSelectedSensorPosition(0, 0, self.CAN_BUS_TIMEOUT_MS)
    self.leftTalonMaster.getSensorCollection().setQuadraturePosition(0, self.CAN_BUS_TIMEOUT_MS)
    if not self.isSimulation():
      self.leftTalonMaster.clearMotionProfileTrajectories()
      self.leftTalonMaster.clearMotionProfileHasUnderrun(0)
    self.leftTalonMaster.set(ControlMode.MotionProfileArc, SetValueMotionProfile.Disable.value)

    if not self.isSimulation():
      self.rightTalonMaster.setSelectedSensorPosition(0, 0, self.CAN_BUS_TIMEOUT_MS)
    self.rightTalonMaster.getSensorCollection().setQuadraturePosition(0, self.CAN_BUS_TIMEOUT_MS)
    if not self.isSimulation():
      self.rightTalonMaster.clearMotionProfileTrajectories()
      self.rightTalonMaster.clearMotionProfileHasUnderrun(0)
    self.rightTalonMaster.set(ControlMode.MotionProfileArc, SetValueMotionProfile.Disable.value)

    if not self.isSimulation():
      with open("/home/lvuser/traj", "rb") as fp:
          trajectory = pickle.load(fp)
    else:
      with open("/home/ubuntu/traj", "rb") as fp:
          trajectory = pickle.load(fp)

    modifier = pf.modifiers.TankModifier(trajectory).modify(2.1) #Wheelbase in feet

    self.leftTrajectory = modifier.getLeftTrajectory()
    self.rightTrajectory = modifier.getRightTrajectory()

    for i in range(len(trajectory)):
      leftSeg = self.leftTrajectory[i]
      rightSeg = self.rightTrajectory[i]

      velCorrection = (rightSeg.velocity - leftSeg.velocity) * self.VELOCITY_MULTIPLIER

      position = (((leftSeg.position + rightSeg.position) * 12) * self.ENCODER_COUNTS_PER_REV) / (math.pi * self.WHEEL_DIAMETER)
      aux_position = 10 * math.degrees(leftSeg.heading)
      slot0 = self.TALON_MOTIONPROFILE_SLOT
      slot1 = self.TALON_GYRO_SLOT
      timeDur = 0
      zeroPos = i == 0
      isLastPoint = i == len(trajectory) - 1
      lvelocity = (((leftSeg.velocity - velCorrection) * 12) * self.ENCODER_COUNTS_PER_REV) / (math.pi * self.WHEEL_DIAMETER) / 10
      rvelocity = (((rightSeg.velocity + velCorrection) * 12) * self.ENCODER_COUNTS_PER_REV) / (math.pi * self.WHEEL_DIAMETER) / 10

      '''There was no empty constructor.'''
      self.leftTrajectory[i] = TrajectoryPoint(position, lvelocity, aux_position, slot0, slot1, isLastPoint, zeroPos, timeDur)
      self.rightTrajectory[i] = TrajectoryPoint(position, rvelocity, aux_position, slot0, slot1, isLastPoint, zeroPos, timeDur)

    if not self.isSimulation():
      for point in self.leftTrajectory:
        self.leftTalonMaster.pushMotionProfileTrajectory(point)

    if not self.isSimulation():
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
    if (not self.leftDone or not self.rightDone) and self.timer.hasPeriodPassed(0.25):
      if not self.isSimulation:
        lBufCount = self.leftMPStatus.btmBufferCnt
        rBufCount = self.rightMPStatus.btmBufferCnt
        lOutput = self.leftTalonMaster.getMotorOutputPercent()
        rOutput = self.rightTalonMaster.getMotorOutputPercent()
        lUnderrun = self.leftMPStatus.hasUnderrun
        rUnderrun = self.rightMPStatus.hasUnderrun
        lError = self.leftTalonMaster.getClosedLoopError(self.PRIMARY_PID_LOOP)
        rError = self.rightTalonMaster.getClosedLoopError(self.PRIMARY_PID_LOOP)
        hError = self.rightTalonMaster.getClosedLoopError(self.AUX_PID_LOOP)
      else:
        lBufCount = 0
        rBufCount = 0
        lOutput = 0
        rOutput = 0
        lUnderrun = 0
        rUnderrun = 0
        lError = 0
        rError = 0
        hError = 0

      print(f'\
        ****************************************\n\
         Points Remaining <{lBufCount}, {rBufCount}>\n\
         Motor Output <{lOutput}, {rOutput}>\n\
         Underrun <{lUnderrun}, {rUnderrun}>\n\
         Closed Loop Error <{lError}, {rError}, {hError}>\n\
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
      if not self.isSimulation():
        ypr = self.pigeon.getYawPitchRoll()
        primary_fdbk = self.unitsToInches(self.rightTalonMaster.getSelectedSensorVelocity(self.PRIMARY_PID_LOOP))
        aux_fdbk = self.unitsToInches(self.rightTalonMaster.getSelectedSensorVelocity(self.AUX_PID_LOOP))
        lOutput = self.leftTalonMaster.getMotorOutputPercent()
        rOutput = self.rightTalonMaster.getMotorOutputPercent()
        lTicks = self.leftTalonMaster.getQuadratureVelocity()
        rTicks = self.rightTalonMaster.getQuadratureVelocity()
        lSpeed = self.unitsToInches(self.leftTalonMaster.getQuadratureVelocity()) * 10
        rSpeed = self.unitsToInches(self.rightTalonMaster.getQuadratureVelocity()) * 10
      else:
        ypr = [0, 0, 0]
        primary_fdbk = 0
        aux_fdbk = 0
        lOutput = 0
        rOutput = 0
        lTicks = 0
        rTicks = 0
        lSpeed = 0
        rSpeed = 0

      print(f'\
        *************teleopPeriodic*************\n\
         Sticks <{self.stick.getRawAxis(1)}, {self.stick.getRawAxis(5)}>\n\
         Motor Output % <{lOutput}, {rOutput}>\n\
         Ticks per 100ms <{lTicks}, {rTicks}>\n\
         Left/Right Speed (in/sec) <{lSpeed},{rSpeed}>\n\
         Primary/Aux Feedback <{primary_fdbk}, {aux_fdbk}>\n\
         Yaw/Pitch/Roll <{ypr[0]}, {ypr[1]}, {ypr[2]}>\n\
        ****************************************\n\
        ')

    self.leftTalonMaster.set(ControlMode.PercentOutput, -1.0 * self.stick.getRawAxis(1))
    self.rightTalonMaster.set(ControlMode.PercentOutput, -1.0 * self.stick.getRawAxis(5))

  def disabledInit(self):
    print("MODE: disabledInit")

  def disabledPeriodic(self):
    if self.timer.hasPeriodPassed(1.0):
      print("MODE: disabledPeriodic")

  def unitsToInches(self, units):
    return units * self.WHEEL_CIRCUMFERENCE / self.ENCODER_COUNTS_PER_REV

  def inchesToUnits(self, inches):
    return inches * self.ENCODER_COUNTS_PER_REV / self.WHEEL_CIRCUMFERENCE

if __name__ == "__main__":
    wpilib.run(MyRobot, physics_enabled=True)

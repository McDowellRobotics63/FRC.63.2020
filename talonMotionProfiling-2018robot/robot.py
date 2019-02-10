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
  
  WHEEL_DIAMETER = 6  # 6 inches
  WHEEL_CIRCUMFERENCE = math.pi * WHEEL_DIAMETER

  CAN_BUS_TIMEOUT_MS = 10

  ENCODER_COUNTS_PER_REV = 4096
  PIGEON_UNITS_PER_ROTATION = 8192

  LEFT_MASTER_CAN_ID = 4
  RIGHT_MASTER_CAN_ID = 2
  LEFT_SLAVE_CAN_ID = 3
  RIGHT_SLAVE_CAN_ID = 1
  PIGEON_IMU_CAN_ID = 6
  ENCODER_SUM_CAN_ID = 5

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

    self.dummyTalon = TalonSRX(self.ENCODER_SUM_CAN_ID)

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

    self.leftTalonSlave.configSelectedFeedbackSensor(FeedbackDevice.CTRE_MagEncoder_Relative, self.PRIMARY_PID_LOOP, self.CAN_BUS_TIMEOUT_MS)
    self.leftTalonSlave.configSelectedFeedbackCoefficient(1.0, self.PRIMARY_PID_LOOP, self.CAN_BUS_TIMEOUT_MS)
    self.leftTalonSlave.setSensorPhase(False)
    self.leftTalonSlave.setStatusFramePeriod(StatusFrame.Status_2_Feedback0, 10, self.CAN_BUS_TIMEOUT_MS)

    self.rightTalonSlave.configSelectedFeedbackSensor(FeedbackDevice.CTRE_MagEncoder_Relative, self.PRIMARY_PID_LOOP, self.CAN_BUS_TIMEOUT_MS)
    self.rightTalonSlave.configSelectedFeedbackCoefficient(1.0, self.PRIMARY_PID_LOOP, self.CAN_BUS_TIMEOUT_MS)
    self.rightTalonSlave.setSensorPhase(False)
    self.rightTalonSlave.setStatusFramePeriod(StatusFrame.Status_2_Feedback0, 10, self.CAN_BUS_TIMEOUT_MS)

    self.dummyTalon.configRemoteFeedbackFilter(self.leftTalonSlave.getDeviceID(), RemoteSensorSource.TalonSRX_SelectedSensor, 0, self.CAN_BUS_TIMEOUT_MS)
    self.dummyTalon.configRemoteFeedbackFilter(self.rightTalonSlave.getDeviceID(), RemoteSensorSource.TalonSRX_SelectedSensor, 1, self.CAN_BUS_TIMEOUT_MS)
    self.dummyTalon.configSensorTerm(0, FeedbackDevice.RemoteSensor0, self.CAN_BUS_TIMEOUT_MS)
    self.dummyTalon.configSensorTerm(1, FeedbackDevice.RemoteSensor1, self.CAN_BUS_TIMEOUT_MS)
    self.dummyTalon.configSelectedFeedbackSensor(FeedbackDevice.SensorSum, self.PRIMARY_PID_LOOP, self.CAN_BUS_TIMEOUT_MS)   
    self.dummyTalon.configSelectedFeedbackCoefficient(1.0, self.PRIMARY_PID_LOOP, self.CAN_BUS_TIMEOUT_MS)
    self.dummyTalon.setStatusFramePeriod(StatusFrame.Status_2_Feedback0, 10, self.CAN_BUS_TIMEOUT_MS)

    for talon in self.leftTalons:
      talon.setInverted(True)

    for talon in self.rightTalons:
      talon.setInverted(False)

    self.leftTalonMaster.setSensorPhase(True)

    '''
    Now that the sensor sum remote sensor is setup, we can setup the master talons close-loop configuration
    '''
    for talon in self.masterTalons:
      talon.configMotionProfileTrajectoryPeriod(self.BASE_TRAJECTORY_PERIOD_MS)

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
      talon.configClosedLoopPeakOutput(self.PRIMARY_PID_LOOP_GAINS_SLOT, 1.0, self.CAN_BUS_TIMEOUT_MS)

      '''
      Select the gains to use for the heading control loop.
      It probably doesn't matter what we select here since each individual trajectory point
      has a setting for the primary and aux PID fains to use.
      Selecting these gains here would be important if we were using motion magic control.
      '''
      talon.selectProfileSlot(self.AUX_PID_LOOP_GAINS_SLOT, self.AUX_PID_LOOP)
      '''This says the heading control loop is allowed to command full motor output'''
      talon.configClosedLoopPeakOutput(self.AUX_PID_LOOP_GAINS_SLOT, 1.0, self.CAN_BUS_TIMEOUT_MS)

      if not self.isSimulation():
        '''Setup the "sum" sensor as remote sensor 0'''
        talon.configRemoteFeedbackFilter(self.dummyTalon.getDeviceID(), RemoteSensorSource.TalonSRX_SelectedSensor, 0, self.CAN_BUS_TIMEOUT_MS)
        '''Setup the pigeon as remote sensor 1'''
        talon.configRemoteFeedbackFilter(self.PIGEON_IMU_CAN_ID, RemoteSensorSource.GadgeteerPigeon_Yaw, 1, self.CAN_BUS_TIMEOUT_MS)
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
      self.leftTalonMaster.configAuxPIDPolarity(False, self.CAN_BUS_TIMEOUT_MS)
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
      self.leftTalonSlave.setSelectedSensorPosition(0, 0, self.CAN_BUS_TIMEOUT_MS)
    self.leftTalonSlave.getSensorCollection().setQuadraturePosition(0, self.CAN_BUS_TIMEOUT_MS)
    if not self.isSimulation():
      self.leftTalonMaster.clearMotionProfileTrajectories()
      self.leftTalonMaster.clearMotionProfileHasUnderrun(0)
    self.leftTalonMaster.set(ControlMode.MotionProfileArc, 0)

    if not self.isSimulation():
      self.rightTalonSlave.setSelectedSensorPosition(0, 0, self.CAN_BUS_TIMEOUT_MS)
    self.rightTalonSlave.getSensorCollection().setQuadraturePosition(0, self.CAN_BUS_TIMEOUT_MS)
    if not self.isSimulation():
      self.rightTalonMaster.clearMotionProfileTrajectories()
      self.rightTalonMaster.clearMotionProfileHasUnderrun(0)
    self.rightTalonMaster.set(ControlMode.MotionProfileArc, 0)

    if not self.isSimulation():
      with open("/home/lvuser/traj", "rb") as fp:
          trajectory = pickle.load(fp)
    else:
      with open("/home/ubuntu/traj", "rb") as fp:
          trajectory = pickle.load(fp)

    print("Length of trajectory: " + str(len(trajectory)))  
    modifier = pf.modifiers.TankModifier(trajectory).modify(2.1) #Wheelbase in feet

    self.leftTrajectory = modifier.getLeftTrajectory()
    self.rightTrajectory = modifier.getRightTrajectory()

    for i in range(len(trajectory)):
      leftSeg = self.leftTrajectory[i]
      rightSeg = self.rightTrajectory[i]

      velCorrection = (rightSeg.velocity - leftSeg.velocity) * self.VELOCITY_MULTIPLIER

      position = self.inchesToUnits((leftSeg.position + rightSeg.position) * 12)
      aux_position = 10 * math.degrees(leftSeg.heading)
      slot0 = self.PRIMARY_PID_LOOP_GAINS_SLOT
      slot1 = self.AUX_PID_LOOP_GAINS_SLOT
      timeDur = 0
      zeroPos = i == 0
      isLastPoint = i == len(trajectory) - 1
      lvelocity = self.inchesToUnits((leftSeg.velocity - velCorrection) * 12) / 10
      rvelocity = self.inchesToUnits((rightSeg.velocity + velCorrection) * 12) / 10

      '''There was no empty constructor.'''
      print(f'position: {position}, aux_position: {aux_position}, lvelcoity: {lvelocity}, rvelocity: {rvelocity}')
      self.leftTrajectory[i] = TrajectoryPoint(position, lvelocity, aux_position, slot0, slot1, isLastPoint, zeroPos, timeDur)
      self.rightTrajectory[i] = TrajectoryPoint(position, rvelocity, aux_position, slot0, slot1, isLastPoint, zeroPos, timeDur)

    if not self.isSimulation():
      for point in self.leftTrajectory:        
        self.leftTalonMaster.pushMotionProfileTrajectory(point)
        #print("Top buffer count left: " + str(self.leftTalonMaster.getMotionProfileStatus().topBufferCnt))

    if not self.isSimulation():
      for point in self.rightTrajectory:
        self.rightTalonMaster.pushMotionProfileTrajectory(point)
        #print("Top buffer count right: " + str(self.rightTalonMaster.getMotionProfileStatus().topBufferCnt))

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
    if not self.motionProfileEnabled and self.leftMPStatus.btmBufferCnt == 0 and self.rightMPStatus.btmBufferCnt == 0:
      print("Beginning to funnel trajectory points into the Talons")
      self.bufferProcessingStartTime = self.timer.getFPGATimestamp()

    '''
    Don't print anything while funneling points into the Talons.
    Printing will slow down execution and we want to measure time
    that it took to do this operation.
    '''
    if self.leftMPStatus.topBufferCnt > 0 and self.leftMPStatus.btmBufferCnt < 50:
      self.leftTalonMaster.processMotionProfileBuffer()

    if self.rightMPStatus.topBufferCnt > 0 and self.rightMPStatus.btmBufferCnt < 50:
      self.rightTalonMaster.processMotionProfileBuffer()

    if not self.motionProfileEnabled and \
       self.leftMPStatus.btmBufferCnt > 20 and \
       self.rightMPStatus.btmBufferCnt > 20:
      self.leftTalonMaster.set(ControlMode.MotionProfileArc, 1)
      self.rightTalonMaster.set(ControlMode.MotionProfileArc, 1)
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
      if not self.isSimulation():
        lTopCount = self.leftMPStatus.topBufferCnt
        rTopCount = self.rightMPStatus.topBufferCnt
        lBufCount = self.leftMPStatus.btmBufferCnt
        rBufCount = self.rightMPStatus.btmBufferCnt
        lOutput = self.leftTalonMaster.getMotorOutputPercent()
        rOutput = self.rightTalonMaster.getMotorOutputPercent()
        lUnderrun = self.leftMPStatus.hasUnderrun
        rUnderrun = self.rightMPStatus.hasUnderrun
        lTarget = self.leftTalonMaster.getClosedLoopTarget(self.PRIMARY_PID_LOOP)
        rTarget = self.rightTalonMaster.getClosedLoopTarget(self.PRIMARY_PID_LOOP)
        hTarget = self.rightTalonMaster.getClosedLoopTarget(self.AUX_PID_LOOP)
        lPosition = self.leftTalonMaster.getSelectedSensorPosition(self.PRIMARY_PID_LOOP)
        rPosition = self.rightTalonMaster.getSelectedSensorPosition(self.PRIMARY_PID_LOOP)
        lError = self.leftTalonMaster.getClosedLoopError(self.PRIMARY_PID_LOOP)
        rError = self.rightTalonMaster.getClosedLoopError(self.PRIMARY_PID_LOOP)
        hError = self.rightTalonMaster.getClosedLoopError(self.AUX_PID_LOOP)
      else:
        lTopCount = 0
        rTopCount = 0
        lBufCount = 0
        rBufCount = 0
        lOutput = 0
        rOutput = 0
        lUnderrun = 0
        rUnderrun = 0
        lTarget = 0
        rTarget = 0
        lPosition = 0
        rPosition = 0
        hTarget = 0
        lError = 0
        rError = 0
        hError = 0

      print(f'\
        ****************************************\n\
         Top Count <{lTopCount}, {rTopCount}>\n\
         Bottom Count <{lBufCount}, {rBufCount}>\n\
         Motor Output <{lOutput}, {rOutput}>\n\
         Underrun <{lUnderrun}, {rUnderrun}>\n\
         Closed Loop Target <{lTarget}, {rTarget}, {hTarget}>\n\
         Closed Loop Position <{lPosition}, {rPosition}>\n\
         Closed Loop Error <{lError}, {rError}, {hError}>\n\
        ****************************************\n\
        ')
    else:
      self.executionFinishTime = self.timer.getFPGATimestamp()
      #print("Both Left and Right motion profiles are finished executing")
      #print(f'Buffer fill time: {self.executionStartTime - self.bufferProcessingStartTime}')
      #print(f'Profile exec time: {self.executionFinishTime - self.executionStartTime}')
    
  def teleopInit(self):
      print("MODE: teleopInit")
      if not self.isSimulation():
        self.pigeon.setYaw(0, self.CAN_BUS_TIMEOUT_MS)
        self.pigeon.setFusedHeading(0, self.CAN_BUS_TIMEOUT_MS)
      else:
        print("pigeon.setYaw() is not implemented in pyfrc simulator")

  def teleopPeriodic(self):
    if self.timer.hasPeriodPassed(0.25):
      if not self.isSimulation():
        ypr = self.pigeon.getYawPitchRoll()
        primary_fdbk = self.rightTalonMaster.getSelectedSensorVelocity(self.PRIMARY_PID_LOOP)
        aux_fdbk = self.rightTalonMaster.getSelectedSensorVelocity(self.AUX_PID_LOOP)
        lOutput = self.leftTalonMaster.getMotorOutputPercent()
        rOutput = self.rightTalonMaster.getMotorOutputPercent()
        lTicks = self.leftTalonMaster.getQuadratureVelocity()
        rTicks = self.rightTalonMaster.getQuadratureVelocity()
        lSpeed = self.unitsToInches(self.leftTalonSlave.getSelectedSensorVelocity(self.PRIMARY_PID_LOOP)) * 10
        rSpeed = self.unitsToInches(self.rightTalonSlave.getSelectedSensorVelocity(self.PRIMARY_PID_LOOP)) * 10
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

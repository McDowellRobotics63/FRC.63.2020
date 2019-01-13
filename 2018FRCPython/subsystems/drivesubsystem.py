
from enum import Enum

from wpilib.command.subsystem import Subsystem
from wpilib.drive import DifferentialDrive
from wpilib import Solenoid
from wpilib import SmartDashboard

from ctre import WPI_TalonSRX
from ctre import FeedbackDevice
from ctre import ControlMode
from ctre import NeutralMode

import robotmap

class Shift(Enum):
    HIGH = 0
    LOW = 1

class DriveSubsystem(Subsystem):

    def __init__(self, robot):
        super().__init__("Drive")
        self.robot = robot

        self.left_master = WPI_TalonSRX(robotmap.DRIVELEFTMASTER)
        self.right_master = WPI_TalonSRX(robotmap.DRIVERIGHTMASTER)
        self.left_slave = WPI_TalonSRX(robotmap.DRIVELEFTSLAVE)
        self.right_slave = WPI_TalonSRX(robotmap.DRIVERIGHTSLAVE)
        self.shifter_high = Solenoid(robotmap.PCM1_CANID, robotmap.SHIFTER_HIGH)
        self.shifter_low = Solenoid(robotmap.PCM1_CANID, robotmap.SHIFTER_LOW)
        self.differential_drive = DifferentialDrive(self.left_master, self.right_master)

        self.TalonConfig()
        self.shiftLow()

    def teleDrive(self, xSpeed, zRotation):
        if self.robot.oi.getController1().B().get():
            scale = SmartDashboard.getNumber("creep_mult", 0.3)
            xSpeed = xSpeed * scale
            zRotation = zRotation * scale

        self.differential_drive.arcadeDrive(xSpeed, zRotation, False)

    def getLeftPosition(self):
        return self.left_master.getSelectedSensorPosition(0)

    def getRightPosition(self):
        return self.right_master.getSelectedSensorPosition(0)

    def getRightSpeed(self):
        return self.right_master.getSelectedSensorVelocity(0)

    def getLeftSpeed(self):
        return self.unitsToInches(self.left_master.getSelectedSensorVelocity(0))

    def getErrorLeft(self):
        return self.left_master.getClosedLoopError(0)

    def getErrorRight(self):
        return self.right_master.getClosedLoopError(0)

    def isLeftSensorConnected(self):
        return self.left_master.getSensorCollection().getPulseWidthRiseToRiseUs() != 0

    def isRightSensorConnected(self):
        return self.right_master.getSensorCollection().getPulseWidthRiseToRiseUs() != 0

    def resetEncoders(self):
        self.left_master.setSelectedSensorPosition(0, 0, robotmap.TIMEOUT_MS)
        self.right_master.setSelectedSensorPosition(0, 0, robotmap.TIMEOUT_MS)

        self.left_master.getSensorCollection().setQuadraturePosition(0, robotmap.TIMEOUT_MS)
        self.right_master.getSensorCollection().setQuadraturePosition(0, robotmap.TIMEOUT_MS)

    def setMotionMagicLeft(self, setpoint):
        SmartDashboard.putNumber("setpoint_left_units", self.inchesToUnits(setpoint))
        self.left_master.set(ControlMode.MotionMagic, self.inchesToUnits(setpoint))

    def setMotionMagicRight(self, setpoint):
        self.right_master.set(ControlMode.MotionMagic, self.inchesToUnits(-setpoint))

    def isMotionMagicNearTarget(self):
        retval = False

        if self.left_master.getActiveTrajectoryPosition() == self.left_master.getClosedLoopTarget(0):
            if self.right_master.getActiveTrajectoryPosition() == self.right_master.getClosedLoopTarget(0):
                if abs(self.left_master.getClosedLoopError(0)) < 300:
                    if abs(self.right_master.getClosedLoopError(0)) < 300:
                        retval = True
        return retval

    def shiftHigh(self):
        self.shifter_high.set(True)
        self.shifter_low.set(False)

    def shiftLow(self):
        self.shifter_high.set(False)
        self.shifter_low.set(True)

    def stop(self):
        self.left_master.set(ControlMode.PercentOutput, 0.0)
        self.right_master.set(ControlMode.PercentOutput, 0.0)

    def unitsToInches(self, units):
        return units * robotmap.DRIVE_WHEEL_CIRCUMFERENCE / robotmap.DRIVE_ENCODER_PPR

    def inchesToUnits(self, inches):
        return inches * robotmap.DRIVE_ENCODER_PPR / robotmap.DRIVE_WHEEL_CIRCUMFERENCE

    def autoInit(self):
        self.resetEncoders()
        self.left_master.setNeutralMode(NeutralMode.Brake)
        self.left_slave.setNeutralMode(NeutralMode.Brake)
        self.right_master.setNeutralMode(NeutralMode.Brake)
        self.right_slave.setNeutralMode(NeutralMode.Brake)
        self.differential_drive.setSafetyEnabled(False)
        self.shiftLow()

    def teleInit(self):
        self.left_master.setNeutralMode(NeutralMode.Coast)
        self.left_slave.setNeutralMode(NeutralMode.Coast)
        self.right_master.setNeutralMode(NeutralMode.Coast)
        self.right_slave.setNeutralMode(NeutralMode.Coast)
        self.differential_drive.setSafetyEnabled(True)
        self.shiftLow()

    def TalonConfig(self):
        self.left_master.configSelectedFeedbackSensor(
            FeedbackDevice.CTRE_MagEncoder_Relative,
            0,
            robotmap.TIMEOUT_MS)
        self.right_master.configSelectedFeedbackSensor(
            FeedbackDevice.CTRE_MagEncoder_Relative,
            0,
            robotmap.TIMEOUT_MS)

        self.left_master.setSelectedSensorPosition(0, 0, robotmap.TIMEOUT_MS)
        self.right_master.setSelectedSensorPosition(0, 0, robotmap.TIMEOUT_MS)

        self.left_master.setStatusFramePeriod(
            WPI_TalonSRX.StatusFrameEnhanced.Status_13_Base_PIDF0,
            10,
            robotmap.TIMEOUT_MS)
        self.left_master.setStatusFramePeriod(
            WPI_TalonSRX.StatusFrameEnhanced.Status_10_MotionMagic,
            10,
            robotmap.TIMEOUT_MS)

        self.right_master.setStatusFramePeriod(
            WPI_TalonSRX.StatusFrameEnhanced.Status_13_Base_PIDF0,
            10,
            robotmap.TIMEOUT_MS)
        self.right_master.setStatusFramePeriod(
            WPI_TalonSRX.StatusFrameEnhanced.Status_10_MotionMagic,
            10,
            robotmap.TIMEOUT_MS)

        self.left_master.setSensorPhase(False)
        self.right_master.setSensorPhase(False)

        self.left_master.setInverted(True)
        self.left_slave.setInverted(True)

        self.right_master.setInverted(True)
        self.right_slave.setInverted(True)

        #Makes talons force zero voltage across when zero output to resist motion
        self.left_master.setNeutralMode(NeutralMode.Brake)
        self.left_slave.setNeutralMode(NeutralMode.Brake)
        self.right_master.setNeutralMode(NeutralMode.Brake)
        self.right_slave.setNeutralMode(NeutralMode.Brake)

        self.left_slave.set(ControlMode.Follower, robotmap.DRIVELEFTMASTER)
        self.right_slave.set(ControlMode.Follower, robotmap.DRIVERIGHTMASTER)

        #Closed Loop Voltage Limits
        self.left_master.configNominalOutputForward(0.0, robotmap.TIMEOUT_MS)
        self.right_master.configNominalOutputForward(0.0, robotmap.TIMEOUT_MS)

        self.left_master.configNominalOutputReverse(-0.0, robotmap.TIMEOUT_MS)
        self.right_master.configNominalOutputReverse(-0.0, robotmap.TIMEOUT_MS)

        self.left_master.configPeakOutputForward(1.0, robotmap.TIMEOUT_MS)
        self.right_master.configPeakOutputForward(1.0, robotmap.TIMEOUT_MS)

        self.left_master.configPeakOutputReverse(-1.0, robotmap.TIMEOUT_MS)
        self.right_master.configPeakOutputReverse(-1.0, robotmap.TIMEOUT_MS)

    def configGains(self, f, p, i, d, izone, cruise, accel):
        self.left_master.selectProfileSlot(0, 0)
        self.left_master.config_kF(0, f, robotmap.TIMEOUT_MS)
        self.left_master.config_kP(0, p, robotmap.TIMEOUT_MS)
        self.left_master.config_kI(0, i, robotmap.TIMEOUT_MS)
        self.left_master.config_kD(0, d, robotmap.TIMEOUT_MS)
        self.left_master.config_IntegralZone(0, izone, robotmap.TIMEOUT_MS)

        self.right_master.selectProfileSlot(0, 0)
        self.right_master.config_kF(0, f, robotmap.TIMEOUT_MS)
        self.right_master.config_kP(0, p, robotmap.TIMEOUT_MS)
        self.right_master.config_kI(0, i, robotmap.TIMEOUT_MS)
        self.right_master.config_kD(0, d, robotmap.TIMEOUT_MS)
        self.right_master.config_IntegralZone(0, izone, robotmap.TIMEOUT_MS)

        self.left_master.configMotionCruiseVelocity(cruise, robotmap.TIMEOUT_MS)
        self.left_master.configMotionAcceleration(accel, robotmap.TIMEOUT_MS)

        self.right_master.configMotionCruiseVelocity(cruise, robotmap.TIMEOUT_MS)
        self.right_master.configMotionAcceleration(accel, robotmap.TIMEOUT_MS)

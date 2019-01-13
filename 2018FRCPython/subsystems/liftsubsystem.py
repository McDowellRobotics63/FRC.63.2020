
from enum import Enum

from wpilib.command.subsystem import Subsystem
from wpilib import DigitalInput
from wpilib import SmartDashboard

from ctre import WPI_TalonSRX
from ctre import FeedbackDevice
from ctre import NeutralMode
from ctre import ControlMode

import robotmap

class Direction(Enum):
    UP = 0
    DOWN = 1

class LiftSubsystem(Subsystem):

    def __init__(self, robot):
        super().__init__("Lift")
        self.robot = robot

        self.lift_motor = WPI_TalonSRX(robotmap.LIFT)
        self.applied_feed_forward = Direction.UP
        self.bottom_limit = DigitalInput(robotmap.LIMIT_SWITCH_LIFT)
        self.TalonConfig()

    def initSubsystemAuto(self):
        self.resetEncoder()
        self.setMotionMagicSetpoint(0)

    def TalonConfig(self):
        self.lift_motor.configSelectedFeedbackSensor(
            FeedbackDevice.CTRE_MagEncoder_Relative,
            0,
            robotmap.TIMEOUT_MS)
        self.lift_motor.setSelectedSensorPosition(0, 0, robotmap.TIMEOUT_MS)
        self.lift_motor.setStatusFramePeriod(
            WPI_TalonSRX.StatusFrameEnhanced.Status_13_Base_PIDF0,
            10,
            robotmap.TIMEOUT_MS)
        self.lift_motor.setStatusFramePeriod(
            WPI_TalonSRX.StatusFrameEnhanced.Status_10_MotionMagic,
            10,
            robotmap.TIMEOUT_MS)
        self.lift_motor.setSensorPhase(False)
        self.lift_motor.setInverted(True)
        self.lift_motor.setNeutralMode(NeutralMode.Brake)
        self.lift_motor.configNominalOutputForward(0, robotmap.TIMEOUT_MS)
        self.lift_motor.configNominalOutputReverse(0, robotmap.TIMEOUT_MS)
        self.lift_motor.configPeakOutputForward(1.0, robotmap.TIMEOUT_MS)
        self.lift_motor.configPeakOutputReverse(-1.0, robotmap.TIMEOUT_MS)
        self.lift_motor.setNeutralMode(NeutralMode.Brake)
        self.lift_motor.configContinuousCurrentLimit(20, robotmap.TIMEOUT_MS)
        self.lift_motor.configPeakCurrentLimit(0, robotmap.TIMEOUT_MS)
        self.lift_motor.configPeakCurrentDuration(0, robotmap.TIMEOUT_MS)
        self.lift_motor.enableCurrentLimit(False)

    def configGains(self, f, p, i, d, izone, accel, cruise):
        self.lift_motor.selectProfileSlot(0, 0)
        self.lift_motor.config_kF(0, f, robotmap.TIMEOUT_MS)
        self.lift_motor.config_kP(0, p, robotmap.TIMEOUT_MS)
        self.lift_motor.config_kI(0, i, robotmap.TIMEOUT_MS)
        self.lift_motor.config_kD(0, d, robotmap.TIMEOUT_MS)
        self.lift_motor.config_IntegralZone(0, izone, robotmap.TIMEOUT_MS)
        self.lift_motor.configMotionCruiseVelocity(cruise, robotmap.TIMEOUT_MS)
        self.lift_motor.configMotionAcceleration(accel, robotmap.TIMEOUT_MS)

    def resetIntegrator(self):
        self.lift_motor.setIntegralAccumulator(0, 0, robotmap.TIMEOUT_MS)

    def getCurrentSetpoint(self):
        return self.unitsToInches(self.lift_motor.getClosedLoopTarget(0))

    def getCurrentPosition(self):
        return self.unitsToInches(self.lift_motor.getSelectedSensorPosition(0))

    def getLiftSpeed(self):
        return self.unitsToInches(self.lift_motor.getSelectedSensorVelocity(0))

    def setMotionMagicSetpoint(self, setpoint):
        setpoint_units = self.inchesToUnits(setpoint)

        if (setpoint_units < self.lift_motor.getClosedLoopTarget(0) and
                self.applied_feed_forward == Direction.UP):

            self.lift_motor.config_kF(0,
                                      SmartDashboard.getNumber("kF_lift_down", 0.0),
                                      robotmap.TIMEOUT_MS)

            self.applied_feed_forward = Direction.DOWN
        elif (setpoint_units > self.lift_motor.getClosedLoopTarget(0) and
              self.applied_feed_forward == Direction.DOWN):

            self.lift_motor.config_kF(0,
                                      SmartDashboard.getNumber("kF_lift_up", 0.0),
                                      robotmap.TIMEOUT_MS)

            self.applied_feed_forward = Direction.UP

        max_lift = SmartDashboard.getNumber("max_lift_inches", 79) / robotmap.LIFT_INCHES_PER_UNIT
        setpoint_units = min(setpoint_units, max_lift)
        setpoint_units = max(0, setpoint_units)

        SmartDashboard.putNumber("setpoint_units", setpoint_units)
        SmartDashboard.putNumber("setpoint_inches", setpoint)

        if self.isSensorConnected():
            self.lift_motor.set(ControlMode.MotionMagic, setpoint_units)
        else:
            self.stop()

    def isMotionMagicNearTarget(self):
        retval = False

        if self.lift_motor.getActiveTrajectoryPosition() == self.lift_motor.getClosedLoopTarget(0):
            if abs(self.lift_motor.getClosedLoopError(0)) < 1000:
                retval = True

        return retval

    def hold(self):
        self.lift_motor.set(ControlMode.MotionMagic, self.lift_motor.getSelectedSensorPosition(0))

    def stop(self):
        self.setPercentOutput(0.0)

    def setPercentOutput (self, val):
        self.lift_motor.set(ControlMode.PercentOutput, val)

    def isSensorConnected(self):
        return self.lift_motor.getSensorCollection().getPulseWidthRiseToRiseUs() != 0

    def resetEncoder(self):
        self.lift_motor.setSelectedSensorPosition(0, 0, robotmap.TIMEOUT_MS)
        self.lift_motor.getSensorCollection().setQuadraturePosition(0, robotmap.TIMEOUT_MS)

    def unitsToInches(self, units):
        return units * robotmap.LIFT_INCHES_PER_UNIT

    def inchesToUnits(self, inches):
        return inches / robotmap.LIFT_INCHES_PER_UNIT

    def isBottomedOut(self):
        return self.bottom_limit.get() is False

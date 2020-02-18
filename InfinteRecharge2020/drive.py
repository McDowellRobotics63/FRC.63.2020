import wpilib
from wpilib import drive
from wpilib import SmartDashboard
from wpilib import Encoder

import ctre
import robotmap
from xboxcontroller import XBox

class InfiniteRechargeDrive():
    def __init__(self):
        #Initialize talon motors with talon speed controller
        self.frontLeftMotor = ctre.WPI_TalonSRX(robotmap.FRONT_LEFT_ID)
        self.rearLeftMotor = ctre.WPI_TalonSRX(robotmap.REAR_LEFT_ID)
        self.frontRightMotor = ctre.WPI_TalonSRX(robotmap.REAR_RIGHT_ID)
        self.rearRightMotor = ctre.WPI_TalonSRX(robotmap.FRONT_RIGHT_ID)

        # invert the left side motors
        self.frontLeftMotor.setInverted(True)
        self.frontRightMotor.setInverted(True)
        self.rearLeftMotor.setInverted(True)
        self.rearRightMotor.setInverted(True)
        
        self.talons = [self.frontLeftMotor, self.rearLeftMotor, self.frontRightMotor, self.rearRightMotor]

        #Initialize drivetrain with motors
        self.drive = drive.MecanumDrive(
            self.frontLeftMotor,
            self.rearLeftMotor,
            self.frontRightMotor,
            self.rearRightMotor,
        )

    def Config(self):
        #Configure PID gains for talons
        for talon in self.talons:
            talon.configNominalOutputForward(0.0, robotmap.CAN_TIMEOUT_MS)
            talon.configNominalOutputReverse(0.0, robotmap.CAN_TIMEOUT_MS)
            talon.configPeakOutputForward(1.0, robotmap.CAN_TIMEOUT_MS)
            talon.configPeakOutputReverse(-1.0, robotmap.CAN_TIMEOUT_MS)
            talon.enableVoltageCompensation(True)
            talon.configVoltageCompSaturation(11.5, robotmap.CAN_TIMEOUT_MS)
            
            talon.config_kP(0, 0.375, robotmap.CAN_TIMEOUT_MS)
            talon.config_kI(0, 0.0, robotmap.CAN_TIMEOUT_MS)
            talon.config_kD(0, 0.0, robotmap.CAN_TIMEOUT_MS)
            talon.config_kF(0, 0.35, robotmap.CAN_TIMEOUT_MS)

            talon.selectProfileSlot(0, 0)
            talon.configClosedLoopPeakOutput(0, 1.0, robotmap.CAN_TIMEOUT_MS)

            #Set sensor to mag encoder
            talon.configSelectedFeedbackSensor(ctre.FeedbackDevice.CTRE_MagEncoder_Relative, 0, robotmap.CAN_TIMEOUT_MS)
            talon.configSelectedFeedbackCoefficient(1.0, 0, robotmap.CAN_TIMEOUT_MS)

            talon.setSelectedSensorPosition(0)

    def Iterate(self, pilot: XBox):
        #Take in controller axis values for drive
        self.drive.driveCartesian(
                pilot.leftStickX(),
                pilot.leftStickY(),
                pilot.rightStickX()
            )
        

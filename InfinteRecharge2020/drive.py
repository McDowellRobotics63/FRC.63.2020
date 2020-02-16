import wpilib
from wpilib import drive
from wpilib import SmartDashboard

import ctre
import robotmap
from xboxcontroller import XBox

class InfiniteRechargeDrive():
    def __init__(self):
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

        for talon in self.talons:
            talon.configNominalOutputForward(0.0, 25)
            talon.configNominalOutputReverse(0.0, 25)
            talon.configPeakOutputForward(1.0, 25)
            talon.configPeakOutputReverse(-1.0, 25)
            talon.enableVoltageCompensation(True)
            talon.configVoltageCompSaturation(11.5, 25)
            #talon.configOpenLoopRamp(0.125, 25)

        for talon in self.talons:
            talon.config_kP(0, 0.375, 25)
            talon.config_kI(0, 0.0, 25)
            talon.config_kD(0, 0.0, 25)
            talon.config_kF(0, 0.35, 25)

            talon.selectProfileSlot(0, 0)
            talon.configClosedLoopPeakOutput(0, 1.0, 25)

            talon.configSelectedFeedbackSensor(ctre.FeedbackDevice.CTRE_MagEncoder_Absolute, 0, 25)
            talon.configSelectedFeedbackCoefficient(1.0, 0, 25)

        self.drive = drive.MecanumDrive(
            self.frontLeftMotor,
            self.rearLeftMotor,
            self.frontRightMotor,
            self.rearRightMotor,
        )

    def Iterate(self, pilot: XBox):
        self.drive.driveCartesian(
                pilot.leftStickX(),
                pilot.leftStickY(),
                pilot.rightStickX()
            )
        

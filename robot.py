#!/usr/bin/env python3
# this is the messiest coding ive ever seen
#adding a comment so i can commit the code

import wpilib
from wpilib.buttons import JoystickButton
from wpilib.drive import MecanumDrive
from wpilib import Spark
from wpilib import Victor
from wpilib import SPI
from wpilib import encoder

import math

import pickle

from navx import AHRS

import ctre
from ctre import RemoteSensorSource
from ctre import SetValueMotionProfile
from ctre import WPI_TalonSRX
from ctre import ControlMode
from ctre import TrajectoryPoint

class MyRobot(wpilib.TimedRobot):
    """Main robot class"""

    

    # Channels on the roboRIO that the motor controllers are plugged in to
    frontLeftChannel = 1
    rearLeftChannel = 2
    frontRightChannel = 4
    rearRightChannel = 3

    ballGrabMotor = 1
    ballTickler = 2

    # The channel on the driver station that the joystick is connected to
    lStickChannel = 0
    rStickChannel = 1

    # solenoids
    PCM_CANID = 6

    GEAR_ADJUST_RETRACT_SOLENOID = 0
    GEAR_ADJUST_EXTEND_SOLENOID = 1
    GEAR_DOOR_DROP_SOLENOID = 3
    GEAR_DOOR_RAISE_SOLENOID = 2
    GEAR_PUSHER_RETRACT_SOLENOID = 4
    GEAR_PUSHER_EXTEND_SOLENOID = 5
    BALL_DOOR_OPEN_SOLENOID = 6
    BALL_DOOR_CLOSE_SOLENOID = 7

    GRABBER_STATE = False
    TICKLER_STATE = False
    COMPRESSOR_STATE = False
    GEAR_DOOR_STATE = False
    GEAR_ADJUST_STATE = False
    GEAR_PUSHER_STATE = False

    AUTO_STATE = 0

    WHEEL_CIRCUMFERENCE = 19 #inches

    def robotInit(self):
        self.timer = wpilib.Timer()
        self.timer.start()

        self.auto_timer = wpilib.Timer()

        self.gyro = AHRS.create_spi()
        self.gyro.reset()

        self.compressor = wpilib.Compressor(self.PCM_CANID)
        self.compressor.setClosedLoopControl(False)
        #self.compressor.setClosedLoopControl(True)

        #Solenoids galore
        self.gearAdjustExtend = wpilib.Solenoid(self.PCM_CANID, self.GEAR_ADJUST_EXTEND_SOLENOID)
        self.gearAdjustRetract = wpilib.Solenoid(self.PCM_CANID, self.GEAR_ADJUST_RETRACT_SOLENOID)

        self.gearPusherExtend = wpilib.Solenoid(self.PCM_CANID, self.GEAR_PUSHER_EXTEND_SOLENOID)
        self.gearPusherRetract = wpilib.Solenoid(self.PCM_CANID, self.GEAR_PUSHER_RETRACT_SOLENOID)

        self.gearDoorDrop = wpilib.Solenoid(self.PCM_CANID, self.GEAR_DOOR_DROP_SOLENOID)
        self.gearDoorRaise = wpilib.Solenoid(self.PCM_CANID, self.GEAR_DOOR_RAISE_SOLENOID)

        self.ballDoorOpen = wpilib.Solenoid(self.PCM_CANID, self.BALL_DOOR_OPEN_SOLENOID)
        self.ballDoorClose = wpilib.Solenoid(self.PCM_CANID, self.BALL_DOOR_CLOSE_SOLENOID)
        

        """Robot initialization function"""
        self.frontLeftMotor = ctre.WPI_TalonSRX(self.frontLeftChannel)
        self.rearLeftMotor = ctre.WPI_TalonSRX(self.rearLeftChannel)
        self.frontRightMotor = ctre.WPI_TalonSRX(self.frontRightChannel)
        self.rearRightMotor = ctre.WPI_TalonSRX(self.rearRightChannel)

        self.tickler = Spark(self.ballTickler)
        self.grabber = Victor(self.ballGrabMotor)

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

            talon.configOpenLoopRamp(0.125, 25)

            talon.config_kP(0, 0.375, 25)
            talon.config_kI(0, 0.0, 25)
            talon.config_kD(0, 0.0, 25)
            talon.config_kF(0, 0.35, 25)

            talon.selectProfileSlot(0, 0)
            talon.configClosedLoopPeakOutput(0, 1.0, 25)

            talon.configSelectedFeedbackSensor(ctre.FeedbackDevice.QuadEncoder, 0, 25)
            talon.configSelectedFeedbackCoefficient(1.0, 0, 25)

            talon.set(ctre.ControlMode.PercentOutput, 0)

        self.drive = MecanumDrive(
            self.frontLeftMotor,
            self.rearLeftMotor,
            self.frontRightMotor,
            self.rearRightMotor,
        )

        self.drive.setExpiration(0.1)
        self.drive.setSafetyEnabled(False)

        self.lstick = wpilib.Joystick(self.lStickChannel)
        self.rstick = wpilib.Joystick(self.rStickChannel)

    def disabled(self):
        """Called when the robot is disabled"""
        while self.isDisabled():
            wpilib.Timer.delay(0.01)

    def DriveStraight(self, distance):

        pass

    def autonomousInit(self):
        self.auto_timer.start()

    def autonomousPeriodic(self):
        #self.auto_timer.delay(5)

        while self.AUTO_STATE != 4:
            """
            self.frontLeftMotor.set(ctre.ControlMode.PercentOutput, -0.4)
            self.frontRightMotor.set(ctre.ControlMode.PercentOutput, 0.4)
            self.rearLeftMotor.set(ctre.ControlMode.PercentOutput, -0.4)
            self.rearRightMotor.set(ctre.ControlMode.PercentOutput, 0.4)
            """
            if self.AUTO_STATE == 0:
                self.drive.driveCartesian(0, .5, -.025)

                if self.auto_timer.hasPeriodPassed(1.7):
                    self.AUTO_STATE = 1
                    #self.auto_timer.reset()

        
            if self.AUTO_STATE == 1:
                self.drive.driveCartesian(0, 0, 0)

                if self.auto_timer.hasPeriodPassed(1.5):
                    self.AUTO_STATE = 2

            if self.AUTO_STATE == 2:
                self.drive.driveCartesian(0, -.5, 0.025)

                if self.auto_timer.hasPeriodPassed(2):
                    self.AUTO_STATE = 3
                    

            if self.AUTO_STATE == 3:
                self.drive.driveCartesian(0, 0, 0)

                #for talon in self.talons:
                    #talon.stopMotor()
                #self.logger.info("STAWP")
                self.AUTO_STATE = 4

                 

        #self.drive.setExpiration(0.1)


        #pass

    def conditonAxis(self, axis, deadband, rate, expo, power, minimum, maximum):
        deadband = min(abs(deadband), 1)
        rate = max(0.1, min(abs(rate), 10))
        expo = max(0, min(abs(expo), 1))
        power = max(1, min(abs(power), 10))

        if axis > -deadband and axis < deadband:
            axis = 0
        else:
            axis = rate * (math.copysign(1, axis) * ((abs(axis) - deadband) / (1 - deadband)))

        if expo > 0.01:
            axis = ((axis * (abs(axis) ** power) * expo) + (axis * (1 - expo)))

        axis = max(min(axis, maximum), minimum)

        return axis

    def teleopInit(self):
        self.compressor.setClosedLoopControl(False)
        self.gyro.reset()

        self.solenoid_timer = wpilib.Timer()
        self.solenoid_timer.start()

        for talon in self.talons:
            talon.setQuadraturePosition(0)

        self.GearAdjustRetract()
        self.GearPusherRetract()
        self.GearDoorDrop()

    #Solenoid functions
    def BallDoorOpen(self):
        self.ballDoorOpen.set(True)
        self.ballDoorClose.set(False)

        self.tickler.set(-0.4)

    def BallDoorClose(self):
        self.ballDoorOpen.set(False)
        self.ballDoorClose.set(True)

        self.tickler.set(0.0)

    def GearAdjustExtend(self):
        self.gearAdjustExtend.set(True)
        self.gearAdjustRetract.set(False)

    def GearAdjustRetract(self):
        self.gearAdjustExtend.set(False)
        self.gearAdjustRetract.set(True)

    def GearPusherExtend(self):
        self.gearPusherExtend.set(True)
        self.gearPusherRetract.set(False)

    def GearPusherRetract(self):
        self.gearPusherExtend.set(False)
        self.gearPusherRetract.set(True)

    def GearDoorDrop(self):
        self.gearDoorDrop.set(True)
        self.gearDoorRaise.set(False)

    def GearDoorRaise(self):
        self.gearDoorDrop.set(False)
        self.gearDoorRaise.set(True)

    #Ball Grab
    def BallGrabStart(self):
        self.grabber.set(-0.2)

    def BallGrabStop(self):
        self.grabber.set(0.0)

    def activate(self, extend, retract, state):
        self.solenoid_timer.reset()
        self.logger.info(state)
        if state:
            extend()
        else:
            retract()

    def teleopPeriodic(self):
        """Called when operation control mode is enabled"""

        while self.isEnabled():
            '''
            self.logger.info("FrontLeft: " + str(self.frontLeftMotor.getMotorOutputVoltage()))
            self.logger.info("RearLeft: " + str(self.rearLeftMotor.getMotorOutputVoltage()))
            self.logger.info("FrontRight: " + str(self.frontRightMotor.getMotorOutputVoltage()))
            self.logger.info("RearRight: " + str(self.rearRightMotor.getMotorOutputVoltage()))
            '''

            self.drive.driveCartesian(
                -self.conditonAxis(self.lstick.getX(), 0.05, 0.85, 0.6, 1.5, -1, 1), 
                self.conditonAxis(self.lstick.getY(), 0.05, 0.85, 0.6, 1.5, -1, 1), 
                -self.conditonAxis(self.rstick.getX(), 0.25, 0.85, 0.6, 0.5, -1, 1) 
                #self.gyro.getYaw()
            )

            if self.solenoid_timer.hasPeriodPassed(0.5):
                if JoystickButton(self.lstick, 3).get():
                    self.COMPRESSOR_STATE = not self.COMPRESSOR_STATE
                    self.activate(
                        self.compressor.start,
                        self.compressor.stop,
                        self.COMPRESSOR_STATE
                    )

                if JoystickButton(self.lstick, 2).get():
                    self.TICKLER_STATE = not self.TICKLER_STATE
                    self.activate(
                        self.BallDoorOpen,
                        self.BallDoorClose,
                        self.TICKLER_STATE
                    )
                
                if JoystickButton(self.lstick, 1).get():
                    self.GRABBER_STATE = not self.GRABBER_STATE
                    self.activate(
                        self.BallGrabStart,
                        self.BallGrabStop,
                        self.GRABBER_STATE
                    )

                #pilotstick 2
                if JoystickButton(self.rstick, 3).get():
                    self.GEAR_DOOR_STATE = not self.GEAR_DOOR_STATE
                    self.activate(
                        self.GearDoorRaise,
                        self.GearDoorDrop,
                        self.GEAR_DOOR_STATE
                    )

                if JoystickButton(self.rstick, 5).get():
                    self.GEAR_ADJUST_STATE = not self.GEAR_ADJUST_STATE
                    self.activate(
                        self.GearAdjustExtend,
                        self.GearAdjustRetract,
                        self.GEAR_ADJUST_STATE
                    )

                if JoystickButton(self.rstick, 4).get():
                    self.GEAR_PUSHER_STATE = not self.GEAR_PUSHER_STATE
                    self.activate(
                        self.GearPusherExtend,
                        self.GearPusherRetract,
                        self.GEAR_PUSHER_STATE
                    )

            wpilib.Timer.delay(0.04)
"""
            if self.timer.get() > 1:
                if (JoystickButton(self.lstick, 3).get()):
                    self.timer.reset()
                    self.COMPRESSOR_STATE = not self.COMPRESSOR_STATE
                    if self.COMPRESSOR_STATE:
                        self.compressor.start()
                    else:
                        self.compressor.stop()
                
                #pilotstick 1
                if JoystickButton(self.lstick, 5).get():
                    self.BallDoorOpen()
                
                if JoystickButton(self.lstick, 4).get():
                    self.BallDoorClose()

                if JoystickButton(self.lstick, 6).get():
                    self.BallGrabStart()
                
                if JoystickButton(self.lstick, 7).get():
                    self.BallGrabStop()

                #pilotstick 2
                if JoystickButton(self.rstick, 3).get():
                    self.activate(
                        self.GearDoorRaise,
                        self.GearDoorDrop,
                        self.GEAR_DOOR_STATE
                    )

                if JoystickButton(self.rstick, 5).get():
                    self.activate(
                        self.GearAdjustExtend,
                        self.GearAdjustRetract,
                        self.GEAR_ADJUST_STATE
                    )

                if JoystickButton(self.rstick, 4).get():
                    self.activate(
                        self.GearPusherExtend,
                        self.GearPusherRetract,
                        self.GEAR_PUSHER_STATE
                    )

                #self.logger.info("Gyro: " + str(self.gyro.getYaw()))
            #self.logger.info("frontLeftMotor 1: " + str(self.frontLeftMotor.getSelectedSensorPosition()))
            #self.logger.info("frontLeftMotor 2: " + str(self.frontLeftMotor.getAnalogIn()))
            #self.logger.info("frontLeftMotor 3: " + str(self.frontLeftMotor.getQuadraturePosition()))
            #self.logger.info("frontLeftMotor 4: " + str(self.frontLeftMotor.getSelectedSensorPosition()))
"""



if __name__ == "__main__":
    wpilib.run(MyRobot)

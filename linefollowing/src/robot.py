#!/usr/bin/env python3

import wpilib


class MyRobot(wpilib.SampleRobot):
    """Main robot class"""

    def robotInit(self):
        """Robot-wide initialization code should go here"""

        self.lstick = wpilib.Joystick(0)
        self.rstick = wpilib.Joystick(1)

        self.l_motor = wpilib.Jaguar(1)
        self.r_motor = wpilib.Jaguar(2)

        # Position gets automatically updated as robot moves
        self.gyro = wpilib.AnalogGyro(1)

        self.robot_drive = wpilib.RobotDrive(self.l_motor, self.r_motor)

        self.motor = wpilib.Jaguar(4)

        self.light_sensor_left = wpilib.DigitalInput(1)
        self.light_sensor_middle = wpilib.DigitalInput(2)
        self.light_sensor_right = wpilib.DigitalInput(3)        

        self.position = wpilib.AnalogInput(2)

    def disabled(self):
        """Called when the robot is disabled"""
        while self.isDisabled():
            self.robot_drive.arcadeDrive(0.0, 0)
            wpilib.Timer.delay(0.01)

    def autonomous(self):
        """Called when autonomous mode is enabled"""

        timer = wpilib.Timer()
        timer.start()

        while self.isAutonomous() and self.isEnabled():

            # follow line
            if self.light_sensor_left.get():
                print("adjust left")
                self.robot_drive.arcadeDrive(-1.0, 0)
            elif self.light_sensor_right.get():
                print("adjust right")
                self.robot_drive.arcadeDrive(-1.0, 0.15)
            elif self.light_sensor_middle.get():
                print("drive straight")
                self.robot_drive.arcadeDrive(-1.0, 0)
            else:
                print("where is the line??")

            wpilib.Timer.delay(0.01)

    def operatorControl(self):
        """Called when operation control mode is enabled"""

        timer = wpilib.Timer()
        timer.start()

        while self.isOperatorControl() and self.isEnabled():

            self.robot_drive.arcadeDrive(self.lstick)

            # Move a motor with a Joystick
            y = self.rstick.getY()

            self.motor.set(y)

            wpilib.Timer.delay(0.04)


if __name__ == "__main__":

    wpilib.run(MyRobot, physics_enabled=True)

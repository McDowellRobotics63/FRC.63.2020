#!/usr/bin/env python3
#
# This example demonstrates using robotpy-pathfinder in the pyfrc simulator
# with a working physics modules such that you can see the path being traced
#
# Note that the pyfrc physics aren't particularly realistic (in particular,
# friction and momentum are ignored), so performance of these exact parameters
# on a real robot won't be so great.
#
import csv

import math
import wpilib

import pathfinder as pf
import navx
import ctre
from ctre import *
import csv
import pickle;

class MyRobot(wpilib.TimedRobot):
    """Main robot class"""

    # Robot attributes
    WHEEL_DIAMETER = 0.5  # 6 inches
    ENCODER_COUNTS_PER_REV = 4096

    # Pathfinder constants
    MAX_VELOCITY = 2  # ft/s
    MAX_ACCELERATION = 2 #ft/s/s

    def robotInit(self):
        """Robot-wide initialization code should go here"""

        self.timer = wpilib.Timer()
        self.timer.start()

        self.navx = navx.AHRS.create_spi()

        self.lstick = wpilib.Joystick(0)

        self.l_motor_master = ctre.WPI_TalonSRX(3)
        self.l_motor_slave = ctre.WPI_TalonSRX(4)

        self.r_motor_master = ctre.WPI_TalonSRX(1)        
        self.r_motor_slave = ctre.WPI_TalonSRX(2)

        self.l_motor_slave.set(ControlMode.Follower, 3)        
        self.r_motor_slave.set(ControlMode.Follower, 1)

        self.l_motor_master.setInverted(False)
        self.l_motor_slave.setInverted(False)
        self.r_motor_master.setInverted(False)
        self.r_motor_slave.setInverted(False)

        self.l_motor_master.setSensorPhase(True)
        self.r_motor_master.setSensorPhase(False)        
        
        self.robot_drive = wpilib.RobotDrive(self.l_motor_master, self.r_motor_master)

    def autonomousInit(self):

        self.robot_drive.setSafetyEnabled(False)
        self.navx.reset()
        self.l_motor_master.setSelectedSensorPosition(0, 0, 10)
        self.r_motor_master.setSelectedSensorPosition(0, 0, 10)
	
        self.l_motor_master.getSensorCollection().setQuadraturePosition(0, 10)
        self.r_motor_master.getSensorCollection().setQuadraturePosition(0, 10)        

        if self.isSimulation():
            # Set up the trajectory
            points = [pf.Waypoint(0, 0, 0), pf.Waypoint(9, 6, 0)]

            info, trajectory = pf.generate(
                points,
                pf.FIT_HERMITE_CUBIC,
                pf.SAMPLES_HIGH,
                dt=self.getPeriod(),
                max_velocity=self.MAX_VELOCITY,
                max_acceleration=self.MAX_ACCELERATION,
                max_jerk=120.0,
            )

            with open("/home/ubuntu/traj", "wb") as fp:
                pickle.dump(trajectory, fp)
        else:
            with open("/home/lvuser/traj", "rb") as fp:
                trajectory = pickle.load(fp)
            print("len of read trajectory: " + str(len(trajectory)))


        print("autonomousInit: " + str(len(trajectory)))

        if self.isSimulation():
            with open('/home/ubuntu/out.csv', 'w+') as points:
                points_writer = csv.writer(points, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

                points_writer.writerow(['dt', 'x', 'y', 'position', 'velocity', 'acceleration', 'jerk', 'heading'])
                for i in trajectory:
                    points_writer.writerow([i.dt, i.x, i.y, i.position, i.velocity, i.acceleration, i.jerk, i.heading])

        # Wheelbase Width = 2 ft
        modifier = pf.modifiers.TankModifier(trajectory).modify(2.1)

        # Do something with the new Trajectories...
        left = modifier.getLeftTrajectory()
        right = modifier.getRightTrajectory()

        leftFollower = pf.followers.EncoderFollower(left)
        leftFollower.configureEncoder(
            self.l_motor_master.getSelectedSensorPosition(0), self.ENCODER_COUNTS_PER_REV, self.WHEEL_DIAMETER
        )
        leftFollower.configurePIDVA(1.0, 0.0, 0.0, 1 / self.MAX_VELOCITY, 0)

        rightFollower = pf.followers.EncoderFollower(right)
        rightFollower.configureEncoder(
            self.r_motor_master.getSelectedSensorPosition(0), self.ENCODER_COUNTS_PER_REV, self.WHEEL_DIAMETER
        )
        rightFollower.configurePIDVA(1.0, 0.0, 0.0, 1 / self.MAX_VELOCITY, 0)

        self.leftFollower = leftFollower
        self.rightFollower = rightFollower

        # This code renders the followed path on the field in simulation (requires pyfrc 2018.2.0+)
        if wpilib.RobotBase.isSimulation():
            from pyfrc.sim import get_user_renderer

            renderer = get_user_renderer()
            if renderer:
                renderer.draw_pathfinder_trajectory(
                    left, color="#0000ff", offset=(-1, 0)
                )
                renderer.draw_pathfinder_trajectory(
                    modifier.source, color="#00ff00", show_dt=1.0, dt_offset=0.0
                )
                renderer.draw_pathfinder_trajectory(
                    right, color="#0000ff", offset=(1, 0)
                )

    def autonomousPeriodic(self):

        l = self.leftFollower.calculate(self.l_motor_master.getSelectedSensorPosition(0))
        r = self.rightFollower.calculate(self.r_motor_master.getSelectedSensorPosition(0))

        gyro_heading = (
            -self.navx.getAngle()
        )  # Assuming the gyro is giving a value in degrees
        desired_heading = pf.r2d(
            self.leftFollower.getHeading()
        )  # Should also be in degrees

        # This is a poor man's P controller
        angleDifference = pf.boundHalfDegrees(desired_heading - gyro_heading)
        turn = 5 * (-1.0 / 80.0) * angleDifference

        if self.timer.hasPeriodPassed(0.5):
            print("l: " + str(l) + ", r: " + str(r) + ", turn: " + str(turn))
            #print("current segment: " + str(self.leftFollower.getSegment().position))            

        l = l + turn
        r = r - turn

        if self.leftFollower.isFinished() or self.rightFollower.isFinished():
            self.robot_drive.tankDrive(0, 0)
        else:
            # -1 is forward, so invert both values
            self.robot_drive.tankDrive(-l, -r)

    def teleopPeriodic(self):
        self.robot_drive.setSafetyEnabled(False)
        #self.robot_drive.arcadeDrive(self.lstick.getRawAxis(1), self.lstick.getRawAxis(0), False)
        self.robot_drive.tankDrive(self.lstick.getRawAxis(1), self.lstick.getRawAxis(5))
        if self.timer.hasPeriodPassed(1.0):
            print("left-encoder: " + str(self.l_motor_master.getSelectedSensorPosition(0)))
            print("right-encoder: " + str(self.r_motor_master.getSelectedSensorPosition(0)))
            print("velocity: " + str(self.l_motor_master.getSelectedSensorVelocity(0)))  
            print("fps: " + str(self.l_motor_master.getSelectedSensorVelocity(0) * 31.4 * self.WHEEL_DIAMETER / 4096))  
            print("navx: " + str(self.navx.getAngle()))


if __name__ == "__main__":
    wpilib.run(MyRobot)

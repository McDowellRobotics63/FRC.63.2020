#!/usr/bin/env python3

import wpilib
from wpilib import SmartDashboard
from commandbased import CommandBasedRobot

from subsystems import clawsubsystem
from subsystems import climbsubsystem
from subsystems import liftsubsystem
from subsystems import drivesubsystem
from commands_drive.teleop_drive_low_command import TeleopDriveLowCommand

from oi import OI


class ExampleBot(CommandBasedRobot):
    """
    The CommandBasedRobot base class implements almost everything you need for
    a working robot program. All you need to do is set up the subsystems and
    commands. You do not need to override the "periodic" functions, as they
    will automatically call the scheduler. You may override the "init" functions
    if you want to do anything special when the mode changes.
    """

    def robotInit(self):
        """
        This is a good place to set up your subsystems and anything else that
        you will need to access later.
        """
        self.claw = clawsubsystem.ClawSubsystem(self)
        self.climb = climbsubsystem.ClimbSubsystem(self)
        self.lift = liftsubsystem.LiftSubsystem(self)
        self.drive = drivesubsystem.DriveSubsystem(self)

        # This MUST be here. If the OI creates Commands (which it very likely
        # will), constructing it during the construction of CommandBase (from
        # which commands extend), subsystems are not guaranteed to be
        # yet. Thus, their requires() statements may grab null pointers. Bad
        # news. Don't move it.
        self.oi = OI(self)

        self.teleDrive = TeleopDriveLowCommand(self)

        SmartDashboard.putNumber("creep_mult", 0.3)

        #self.autonomousProgram = AutonomousProgram()

    def teleopInit(self):
        self.teleDrive.start()

    def autonomousInit(self):
        """
        You should call start on your autonomous program here. You can
        instantiate the program here if you like, or in robotInit as in this
        example. You can also use a SendableChooser to have the autonomous
        program chosen from the SmartDashboard.
        """

        #self.autonomousProgram.start()

def disabledInit(self):
    self.teleDrive.cancel()
    self.drive.teleInit()

if __name__ == "__main__":
    wpilib.run(ExampleBot)


import wpilib
from wpilib import sendablechooser
from wpilib import Timer
from wpilib import SmartDashboard

from robotenums import *

import pickle

class Auto1():
    def __init__(self, robot, logger):
        self.logger = logger
        self.robot = robot
        self.timer = Timer()

        if not self.robot.isSimulation():
            with open("/home/lvuser/traj", "rb") as fp:
                self.trajectory = pickle.load(fp)
        else:
            with open("/home/ubuntu/traj", "rb") as fp:
                self.trajectory = pickle.load(fp)

        self.target_chooser = sendablechooser.SendableChooser()
        self.target_chooser.setDefaultOption(TargetHeight.LOW.name, TargetHeight.LOW)
        self.target_chooser.addOption(TargetHeight.MIDDLE.name, TargetHeight.MIDDLE)
        self.target_chooser.addOption(TargetHeight.HIGH.name, TargetHeight.HIGH)

        self.left_right_chooser = sendablechooser.SendableChooser()
        self.left_right_chooser.setDefaultOption(RightLeft.RIGHT.name, RightLeft.RIGHT)
        self.left_right_chooser.addOption(RightLeft.LEFT.name, RightLeft.LEFT)

        self.hab_level_chooser = sendablechooser.SendableChooser()
        self.hab_level_chooser.setDefaultOption(HabLevel.LEVEL1.name, HabLevel.LEVEL1)
        self.hab_level_chooser.addOption(HabLevel.LEVEL2.name, HabLevel.LEVEL2)

        SmartDashboard.putData("TargetChooser", self.target_chooser)
        SmartDashboard.putData("LeftRightChooser", self.left_right_chooser)
        SmartDashboard.putData("HabLevelChooser", self.hab_level_chooser)

        self.chosen_target = TargetHeight.LOW
        self.left_right = RightLeft.RIGHT
        self.hab_level = HabLevel.LEVEL1

    def init(self):
        self.logger.info("Initializing auto 1")

        self.chosen_target = self.target_chooser.getSelected()
        self.left_right = self.left_right_chooser.getSelected()
        self.hab_level = self.hab_level_chooser.getSelected()

        self.logger.info("<Auto1> " + self.hab_level.name + ", " + self.left_right.name + ", " + self.chosen_target.name)

        self.state = 0
        self.timer.start()

    def iterate(self):
        SmartDashboard.putNumber("Auto1 State", self.state)

        if self.state == 0:
            self.robot.harpoon.deploy_harpoon()
            self.timer.reset()
            if self.hab_level == HabLevel.LEVEL2:
                self.state = 1
            else:
                self.state = 2

        elif self.state == 1:
            self.robot.drive.drive_straight(0.4)
            if self.timer.get() > 1.0:
                self.state = 2

        elif self.state == 2:
            self.robot.drive.drive_straight(0.0)
            self.robot.lift.deploy_lift()
            self.state = 3

        elif self.state == 3:
            if self.robot.lift.current_state == LiftState.LIFT_DEPLOYED:
                self.state = 4

        elif self.state == 4:
            self.robot.drive.follow_a_path(self.trajectory)
            self.state = 5

        elif self.state == 5:
            if self.robot.drive.leftDone and self.robot.drive.rightDone:
                self.state = 6

        elif self.state == 6:
            if self.chosen_target == TargetHeight.LOW:
                self.robot.lift.go_to_preset(LiftPreset.LIFT_PRESET_HATCH_LOW)
            elif self.chosen_target == TargetHeight.MIDDLE:
                self.robot.lift.go_to_preset(LiftPreset.LIFT_PRESET_HATCH_MIDDLE)
            if self.chosen_target == TargetHeight.HIGH:
                self.robot.lift.go_to_preset(LiftPreset.LIFT_PRESET_HATCH_HIGH)
            self.state = 7

        elif self.state == 7:
            if self.robot.lift.bang_bang_to_setpoint():
                self.state = 8

        elif self.state == 8:
            self.robot.harpoon.stow_harpoon()
            self.state = 9

        elif self.state == 9:
            if self.robot.harpoon.current_state == HarpoonState.HARPOON_STOWED:
                self.timer.reset()
                self.state = 10

        elif self.state == 10:
            self.robot.drive.drive_straight(-0.4)
            if self.timer.get() > 1.0:
                self.state = 11

        elif self.state == 11:
            self.robot.drive.drive_straight(0.0)
            self.state = 12

        elif self.state == 12:
            self.robot.lift.go_to_preset(LiftPreset.LIFT_PRESET_STOW)
            self.state = 13

        elif self.state == 13:
            if self.robot.lift.bang_bang_to_setpoint():
                self.state = 14

        elif self.state == 14:
            pass
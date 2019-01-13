from wpilib.command import CommandGroup
from wpilib import SmartDashboard

from commands_lift.auto_set_lift_position import AutoSetLiftPosition
from commands_drive.auto_drive_fixed_distance import AutoDriveFixedDistance
from commands_drive.auto_rotate import AutoRotate
from commands_claw.obtain_box import ObtainBox
from commands_claw.auto_shoot_box import AutoShootBox

class AutoRoutine(CommandGroup):
    def __init__(self, field_setup, switches):
        super().__init__()

        #All inches
        self.DEFAULT_HEIGHT = 17 #lift height for moving
        self.SWITCH_HEIGHT = 30
        self.SCALE0 = 240
        self.SCALE1 = 6 #diagonal bit
        self.SCALE2 = 8 #creep forward
        self.SCALE_TURN = 30
        self.TWOCUBE0 = 48 #distance to come back for switch before turning
        self.TWOCUBE1 = 90.50966799187808 #slanted bit
        self.TWOCUBE2 = 32 #drive forward for cube
        self.SWITCH0 = 140 #distance from middle of robot to middle of switch
        self.SWITCH1 = 6 #left/right distance from switch
        self.MIDDLE0 = 24
        self.MIDDLE1 = 50 #half of switch width
        self.MIDDLE_FUDGE = 44 #amount to subtract from switch0 to go forward
        self.MIDDLE_OFFSET = 16 #offcenteredness to correct when in middle
        self.LINE = 120 #distance to auto line
        self.SHAKE = 6

        if switches == 1: 
            self.botPos = 'r'
        if switches == 2: 
            self.botPos = 'm'
        if switches == 4: 
            self.botPos = 'l'

        self.field_setup = field_setup

        self.drive(self.SHAKE)
        self.parallelLift(self.DEFAULT_HEIGHT)
        if self.botPos == 'm':
            self.middle()
        elif self.field_setup.charAt(0) == self.botPos: #only switch in on same side
            self.switches()
        elif field_setup.charAt(1) == self.botPos: #scale on our bot's side
            self.scale()
            if self.field_setup.charAt(0) == self.botPos: #switch is also on our bot's side
                self.twoCube()
        else:
            self.weRektBois()

        if self.botPos != 'm': 
            self.sequentialLift(0)

    def middle(self):
        self.drive(self.MIDDLE0 - self.SHAKE)
        if self.field_setup.charAt(0) == 'l':
            self.turn(-90)
            self.drive(self.MIDDLE1 + self.MIDDLE_OFFSET)
        else:
            self.turn(90)
            self.drive(self.MIDDLE1 - self.MIDDLE_OFFSET)
        if self.field_setup.charAt(0) == 'l':
            self.turn(90)
        else:
            self.turn(-90)

        self.parallelLift(self.SWITCH_HEIGHT)
        self.drive(self.SWITCH0 - self.MIDDLE0 - self.MIDDLE_FUDGE)
        self.shoot()

    def scale(self):
        self.drive(self.SCALE0 - self.SHAKE)
        self.turnCalc(self.SCALE_TURN)
        self.parallelLift(SmartDashboard.getNumber("max_lift_inches", 79)-2)
        self.drive(self.SCALE1)
        self.drive(self.SCALE2)
        self.shoot()
        self.drive(-self.SCALE2)

    def switches(self):
        self.drive(self.SWITCH0 - self.SHAKE)
        self.turnCalc(90)
        self.sequentialLift(self.SWITCH_HEIGHT)
        self.drive(self.SWITCH1)
        self.shoot()
        self.drive(-self.SWITCH1)

    #starts from end pos of scale
    def twoCube(self):
        self.turnCalc(90)
        self.drive(self.TWOCUBE0)
        self.turnCalc(-45)
        self.parallelLift(0)
        self.drive(self.TWOCUBE1)
        self.turnCalc(45)
        self.drive(self.TWOCUBE2)
        self.sequentialLift(0)
        self.addSequential(ObtainBox(self))
        self.parallelLift(self.SWITCH_HEIGHT)
        self.drive(26)
        self.shoot()

    #autoline
    def weRektBois(self):
        self.drive(self.LINE-self.SHAKE)

    #turns angle on left, -angle on right
    def turnCalc(self, angle):
        if self.botPos == 'l':
            self.addSequential(AutoRotate(self, angle))
        else:
            self.addSequential(AutoRotate(self, -angle))

    def drive(self, dist):
        self.addSequential(AutoDriveFixedDistance(self, dist))

    def turn(self, angle):
        self.addSequential(AutoRotate(self, angle))

    def shoot(self):
        self.addSequential(AutoShootBox(self))

    def parallelLift(self, height):
        self.addParallel(AutoSetLiftPosition(self, height))

    def sequentialLift(self, height):
        self.addSequential(AutoSetLiftPosition(self, height))

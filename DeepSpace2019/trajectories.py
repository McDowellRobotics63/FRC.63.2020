import pathfinder as pf
import math

class AutoTrajectories():
    RightRocketNear = [pf.Waypoint(0, 0, 0), pf.Waypoint(11, -7.5, -math.pi/6)]

    RightRocketFar = [pf.Waypoint(0, 0, 0),pf.Waypoint(3, 0, 0), pf.Waypoint(15.5, -2, -math.pi/6), pf.Waypoint(16.5, -7.5, math.pi/5.5)]

    LeftRocketNear = [pf.Waypoint(0, 0, 0), pf.Waypoint(11, 7.5, math.pi/6)]

    LeftRocketFar = [pf.Waypoint(0, 0, 0),pf.Waypoint(3, 0, 0), pf.Waypoint(15.5, 2, math.pi/6), pf.Waypoint(16.5, 7.5, -math.pi/5.5)]
    
#Right Start, Near hatch
#pf.Waypoint(0, 0, 0), pf.Waypoint(11, -7.5, -math.pi/6)

#Right Start, Far hatch
#pf.Waypoint(0, 0, 0),pf.Waypoint(3, 0, 0), pf.Waypoint(15.5, -2, -math.pi/6), pf.Waypoint(16.5, -7.5, math.pi/5.5)

#Left Start, Near hatch
#pf.Waypoint(0, 0, 0), pf.Waypoint(11, 7.5, math.pi/6)

#Left Start, Far hatch
#pf.Waypoint(0, 0, 0),pf.Waypoint(3, 0, 0), pf.Waypoint(15.5, 2, math.pi/6), pf.Waypoint(16.5, 7.5, -math.pi/5.5)
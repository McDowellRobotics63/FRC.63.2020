
import pathfinder as pf
import pickle
import math
import csv

# Pathfinder constants
MAX_VELOCITY = 4  # ft/s
MAX_ACCELERATION = 4 #ft/s/s
PERIOD = 0.02
MAX_JERK = 120.0

# Set up the trajectory
points = [pf.Waypoint(0, 0, 0), pf.Waypoint(6, 3, math.pi/2), pf.Waypoint(0, 6, 0)]

info, trajectory = pf.generate(
    points,
    pf.FIT_HERMITE_CUBIC,
    pf.SAMPLES_HIGH,
    dt=PERIOD,
    max_velocity=MAX_VELOCITY,
    max_acceleration=MAX_ACCELERATION,
    max_jerk=MAX_JERK,
)

'''
with open('/home/ubuntu/out.csv', 'w+') as points:
    points_writer = csv.writer(points, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)

    points_writer.writerow(['dt', 'x', 'y', 'position', 'velocity', 'acceleration', 'jerk', 'heading'])
    for i in trajectory:
        points_writer.writerow([i.dt, i.x, i.y, i.position, i.velocity, i.acceleration, i.jerk, i.heading])
'''

with open("/home/ubuntu/traj", "wb") as fp:
    pickle.dump(trajectory, fp)

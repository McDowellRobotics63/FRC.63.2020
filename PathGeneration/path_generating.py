import copy
import math
from Plot import Plot
from Vector2D import Vector2D

#Open the file
file = open("Coordinates.txt", "r+")
coords = []

#Put coordinates into a list of 2D vectors
for i in file:
    s = i.split()
    coords.append(Vector2D(float(s[0]), float(s[1])))
file.close()

#Generate Points and make a smooth path
#Adds more points given coordinates
def injectPoints(coords):
    #Controls spacing between each injectd point
    spacing  = 6
    newPoints = []
    for i in range(len(coords) - 1):
        vector = coords[i + 1].sub(coords[i])
        num_points_that_fit = math.ceil(vector.mag() / spacing)
        
        vector = vector.div(Vector2D(vector.mag(), vector.mag())).mult(Vector2D(spacing, spacing))
        for j in range(num_points_that_fit):
            newPoints.append(coords[i].add(vector.mult(Vector2D(j, j))))
    newPoints.append(coords[len(coords) - 1])
    return newPoints
   
#Smooths the injected points on the path
def smoothPath(path, a, b, tol):
    newPath = path.copy()

    change = tol
    while change >= tol:
        change = 0.0
        for i in range(1, len(path) - 1):
            aux = newPath[i]
            p1 = path[i].sub(newPath[i]).mult(Vector2D(a, a))
            p2 = Vector2D(b, b).mult(newPath[i - 1].add(newPath[i + 1]).sub(newPath[i].mult(Vector2D(2, 2))))
            newPath[i] = newPath[i].add(p1.add(p2))
            change += abs(aux.sub(newPath[i]).x)
            change += abs(aux.sub(newPath[i]).y)
    return newPath

#Calulate the curvature between points on the path
def getCurvature(path):
    points = path.copy()
    pCurve = []
    pCurve.append(0)

    for i in range(1, len(path) - 1):
        path[i] = path[i].add(Vector2D(0.001, 0))
        k1 = 0.5 * ((path[i].x ** 2) + (path[i].y ** 2) - (path[i - 1].x ** 2) - (path[i - 1].y ** 2)) / (path[i].x - path[i - 1].x)
        k2 = (path[i].y - path[i - 1].y) / (path[i].x - path[i - 1].x)
        b = 0.5 * ((path[i - 1].x ** 2) - 2 * path[i - 1].x * k1 + (path[i - 1].y ** 2) - (path[i + 1].x ** 2) + 2 * path[i + 1].x * k1 - (path[i + 1].y ** 2)) / (path[i + 1].x * k2 - path[i + 1].y + path[i - 1].y - path[i - 1].x * k2)
        a = k1 - k2 * b
        r = math.sqrt(((path[i].x - a) ** 2) + ((path[i].y - b) ** 2))
        pCurve.append(1 / r)
    pCurve.append(0)
    return pCurve

#Variables to control smoothing
#Lower b value = less smooth path
#Changing a or t breaks it so leave those at what they're at
b = 0.97
a = 1 - b
t = 0.001

straightPath = injectPoints(coords)
smoothedPath = smoothPath(straightPath, a, b, t)

Plot(straightPath, smoothedPath, 2)

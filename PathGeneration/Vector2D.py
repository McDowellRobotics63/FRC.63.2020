import math

class Vector2D(object):
    """Creates a 2D Vector"""
    def __init__(self, x, y):
        self.x = x
        self.y = y


    #Finds the magnitude of the vector
    def mag(self):
        return math.sqrt((self.x ** 2) + (self.y ** 2))

    #Add vectors
    def add(self, other):
        m = Vector2D(0, 0)
        m.x = self.x + other.x
        m.y = self.y + other.y
        return m

    #Subtract vectors
    def sub(self, other):
        m = Vector2D(0, 0)
        m.x = self.x - other.x
        m.y = self.y - other.y
        return m

    #Multiply vectors
    def mult(self, other):
        m = Vector2D(0, 0)
        m.x = self.x * other.x
        m.y = self.y * other.y
        return m

    #Divide vectors
    def div(self, other):
        m = Vector2D(0, 0)
        m.x = self.x / other.x
        m.y = self.y / other.y
        return m

    #Calculates dist between self and another vector
    def dist(self, other):
        return math.sqrt(((other.x - self.x) ** 2) + ((other.y - self.x) ** 2))

    #Calculates dot product of two vectors
    def dot(self, other):
        return (self.x * other.x) + (self.y * other.y)

    #Calculates the angle at which the vector points
    def heading(self):
        angle = math.atan2(-self.y, self.x)
        return -1 * angle



        





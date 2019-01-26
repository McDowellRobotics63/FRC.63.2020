from tkinter import *
from Vector2D import Vector2D

#Plots the points and draws lines for the path on a canvas

class Plot(object):
    def __init__(self, points, path, size):
        self.points = points
        self.path = path
        self.size = size

        self.root = Tk()
        self.c = Canvas(self.root, width=900, height=900)

        #Draw lines for the genereated path & the given coordinates
        for i in range(len(self.points) - 1):
            self.c.create_line(self.points[i].x, self.points[i].y, self.points[i + 1].x, self.points[i + 1].y, fill='red')
            self.c.create_line(self.path[i].x, self.path[i].y, self.path[i + 1].x, self.path[i + 1].y, width=2)
        
        #Draw points on the given path
        for i in range(len(self.path)):
            self.c.create_oval(self.path[i].x - (self.size), self.path[i].y - (self.size), self.path[i].x + self.size, self.path[i].y + self.size, fill='grey')

        self.c.pack()
        self.root.mainloop()
            




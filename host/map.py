"""
Mapper
Probabilistic map of the forest
"""

import numpy
import matplotlib.pyplot as mpl

X_MAX = 96 # inches
Y_MAX = 96 # inches
DIST_MIN = 2
DIST_MAX = 100 
ERROR = 0.2 # rad

class Map:

    ## initialize map
    def __init__(self):
        self.map = numpy.zeros([X_MAX,Y_MAX])
    
    ## Appends new snapshot to the map
    def append(self, trees, position, orientation, error):
        (x, y) = position
        t = orientation
        for offset in trees:
            for orientation in [-error, 0, error]: # more then 3
                x1 = x + numpy.cos(t + offset + error) * DIST_MIN
                y1 = y + numpy.sin(t + offset + error) * DIST_MIN
                for dist in range(DIST_MIN, DIST_MAX):
                    x2 = x1 + numpy.cos(t + offset + error) * dist
                    y2 = y1 + numpy.sin(t + offset + error) * dist
                    if (x2 >= X_MAX - 2) or (y2 >= Y_MAX - 2):
                        break
                    elif (x2 <= 0) or (y2 <= 0):
                        break
                    else:
                        continue
            x_vals = numpy.linspace(x1, x2, dist).astype(int)
            y_vals = numpy.linspace(y1, y2, dist).astype(int)
            self.map[x_vals, y_vals] += 1 ## add to field
    
    ## Returns the predicted x-y location of trees based on the current map
    ## - should filter for only high probability points
    ## - should cluster like-points into a consolidated estimate location
    ## - should only return significant intersections
    def predict(self):
        prob = self.map[numpy.nonzero(self.map)]
        (x, y) = numpy.nonzero((self.map > numpy.mean(prob)))
        mpl.scatter(x, y)
        mpl.show()
        return (x,y)
        
    def filtered(self):
        
    
    ## Displays the entire probabilistic map of tree locations
    def display(self):
        (x, y) = numpy.nonzero(self.map)
        prob = self.map[numpy.nonzero(self.map)]
        mpl.scatter(x, y, c=prob)
        mpl.show()
        return (x,y)
        
if __name__ == '__main__':
    f = Map()
    f.append([0, 1.25], (1,0), 1, ERROR)
    f.append([0.75, 1.25, 1.5], (90,0), 1, ERROR)
    f.append([0.25, 1.5, -0.25], (45,0), 1, ERROR)
    soft = f.display()
    hard = f.predict()

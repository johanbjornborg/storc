#Package imports
from numpy import array, cos, sin
from math import radians, pi

#Local imports
import sheer_layer as sl
import equations as eq
import create_kml as kml
from numpy.oldnumeric.arrayfns import reverse

'''
Created on Jul 3, 2012

@author: John Wells

WHAT IT DOES 7/13:
    Takes a position (Recorded in numpy array format [x,y,z]) and determines its path based on the wind speeds and directions from 
    NWS Salt Lake City.
    Essentially, it's just doing some vector addition. For each sheer lyr in the atmosphere, it adds in the vector components of the wind speed and direction.
    From there, it takes the ascent rate (Assumed as constant, might need to fix that) and calculates how long it will take to reach the top of the highest sheer lyr.
    
    Update 7/25:
    Updated the prediction algorithm to be piecewise. One part for ascent, the other for descent.
    
    Update 8/7:
    Added a function to calculate the projected descent path, given a list of points. The intent of this is to address a 
    miscalculation in the original prediction. The assumption is that the ascent vector should mirror the descent, with the exception
    of a faster descent velocity.
    Also tuned the kml output a little bit.
    
WHAT I WISH IT DID:
    Vector calculation hasn't been tested, but it seems correct.
    Used dictionaries instead of classes.
'''



class predict(object):
    '''
    Predicts where a balloon is going to go based on wind data pulled from various sources
    '''
    
    AscentPoints = []
    DescentPoints = []
    origin = array([])
    
    def __init__(self, data_source, max_height):
        self.data = []
        self.tick = 0
        self.peak = max_height
        if data_source == 1:
#            print "\n------Using GFS text file------\n"
            for d in sl.gfs_local():  
                self.data.append(d)
        elif data_source == 2:
#            print "\n------Using winds aloft data----\n"
            for d in sl.get_winds_aloft():
                self.data.append(d)
                
    def path_correction(self, origin, points, apex = 30000, pressure = None, temp = None):
        '''
        Given a list of real time GPS points, calculate the projected descent path.
        Initial implementation: 
        Take the given list of points, create a vector out of it, 
        reverse the Z coordinate, and add it to itself.
        
        Desired implementation:
        Create a vector from the list of points, and plot the descent using the descent rate calculation.
        This is desirable because the descent rate greatly differs from the ascent. 
        
        1) Get a unit vector from points.
        2) Starting at the apex, create a time step (t = 0), and calculate how long it takes to travel to the ground.
        3) For however many seconds it takes, add up the results.
        '''
        corrections = []
        n = apex # Set Height
        peak = points[len(points) - 1]
        if pressure is None:
            pressure = eq.pressure(n)
        if temp is None:
            temp = 1
        for p in reversed(points):
            if n > 1300:    #1300m = SLC avg height.    
                d = eq.descent_rate(n, pressure, temp)     #Increment by Descent Rate
                n += d
                pnot = (peak[0] + (peak[0] - p[0]),peak[1] + (peak[1] - p[1]),n)
                print pnot
                corrections.append(pnot)
                
        return corrections  
                
    def prediction(self, Vnot):
        """
        Base Piecewise handler function. Calls Ascent and Descent and returns a path vector to the caller.
        """
#        print "Starting prediction..."
        predict.AscentPoints.append((Vnot[0],Vnot[1],Vnot[2])) 
        ascent = self.__ascent(Vnot)
        point = eq.geodetic(ascent, Vnot)
        predict.AscentPoints.append((point[0],point[1],point[2])) 
        descent = self.__descent(point, ascent)
        finalPoint = predict.AscentPoints[len(predict.AscentPoints) - 1 ]#eq.geodetic(final, point)
        #predict.AscentPoints.append((finalPoint[0],finalPoint[1],finalPoint[2])) 
        print "Total flight time:", float(self.tick) / 3600, "hours."
        self.current_to_kml(finalPoint)
        return finalPoint
                            
    def _layers(self, layer, rev = False):
        """
        Iterator function for the layers built from weather data. Provides next and previous iteration
        object, in the event that the caller needs to know a parameter of a previous (or next) iteration.
        Currently, the only one used is previous.
        """
        if not rev:
            iterator = iter(layer)
            prev = None
            item = iterator.next()  # throws StopIteration if empty.
            for next in iterator:
                yield (prev,item,next)
                prev = item
                item = next
            yield (prev,item,None)
        else:
            iterator = iter(layer)
            prev = None
            item = iterator.next()  # throws StopIteration if empty.
            for next in iterator:
                yield (prev,item,next)
                prev = item
                item = next
            yield (prev,item,None)
    
    def __ascent(self, Vpos):
        """
        Piecewise Ascent prediction. 
        Takes the initial position and calculates the effect of wind as the balloon rises through the atmosphere.
        """
        Vavg = array([0,0,0])
        self.origin = Vpos
        for prev, current, next in self._layers(self.data):               
            floor = float(current[0])
            wind_dir = float(current[1])
            wind_spd = float(current[2])
            if(next is None):
                ceiling = self.peak 
            else:
                ceiling = float(next[0])
            if Vpos[2] is None:
                Vpos[2] = floor
            if Vpos[2] > ceiling:     # If Vpos altitude isn't in the current lyr, go to next iteration. 
                continue
            
            if(current[3]):
                pressure = float(current[3])
            else:
                pressure = None
            
            if(current[4]):
                temp = float(current[4])
            else:
                temp = None
            
            while (Vavg[2] < ceiling):
                Vavg[2] = Vavg[2] + eq.ascent_rate(Vavg[2], pressure, temp)      #Increment by Ascent Rate
                Vavg = Vavg + self.__wind_component(wind_spd, wind_dir)
                self.tick += 1
            point = eq.geodetic(Vavg, Vpos)
            predict.AscentPoints.append((point[0],point[1],point[2]))    
    
        return Vavg
               
    def __descent(self, Vpos, Vpeak):
        """
        Piecewise Descent prediction. Takes the result from @_ascent and the initial position, performs the same calculation as ascent, but in reverse order. 
        """
        Vpath = eq.geodetic(Vpeak, Vpos)
        n = float(Vpeak[2])
        Vavg = array([0,0,0])
        for prev, current, next in self._layers(reversed(self.data)):
            floor = float(current[0])
            wind_dir = float(current[1])
            wind_spd = float(current[2])
            
            if(current[3]):
                pressure = float(current[3])
            else:
                pressure = None
            
            if(current[4]):
                temp = float(current[4])
            else:
                temp = None
                
            if(next is None):
                floor = float(self.origin[2])
            elif current[0] > n:
                continue
                
            while (n > floor):
                d = eq.descent_rate(n, pressure, temp)     #Increment by Descent Rate
                n += d
                Vavg[2] = Vavg[2] + d
                Vavg = Vavg + self.__wind_component(wind_spd, wind_dir)
                self.tick = self.tick + 1
            point = eq.geodetic(Vavg, Vpos)
            self.AscentPoints.append((point[0],point[1],Vpeak[2]+point[2]))
            
        descent = eq.geodetic(Vavg, Vpos)

        #self.DescentPoints.append((descent[1],descent[0],descent[2]))    
        return descent   
                 
    def __wind_component(self, wind_spd, wind_dir):
        """
        Takes the provided wind speed and heading and breaks it down into component form. 
        Also takes the direction and converts it into degrees true.
        """
        theta = radians(wind_dir)
        if 0 < theta < pi/2:
            theta = pi/2 - theta # 90 - Theta if 0 <= Theta <= 90
        else:
            theta = 7.85398163 - theta # 450 - Theta if 90 < Theta < 360
        
        V = [-wind_spd * cos(theta), -wind_spd * sin(theta), 0]
        #print V, wind_spd, wind_dir, degrees(theta)
        return V    
          
    def __reference_frame(self, V):
        #TODO: Implement the formula to figure out the actual distance lat and longitude per degree. For greater accuracy.
        pass
    
    def current_to_kml(self, Final):
        '''
        Sends a blue line indicating predicted travel path.
        '''
        _kml = kml.WebOutput()
        ini = self.origin
        
        _kml.add_point([ini[0],ini[1],ini[2]], "Origin")
        _kml.add_point([Final[0],Final[1],Final[2]], "Destination")
        _kml.create_linestring(self.AscentPoints, "50f00014", 3,"Initial", "Initial path prediction via wind data.")
        _kml.save_kml("initial")
    

#===============================================================================
# TEST MAIN METHOD
#===============================================================================

def main():
#    test_winds_aloft()
#    test_GFS_file()
#    test_pred_comp()
    test_pred_modular()
#    test_path_correction()
    pass



#===============================================================================
# UNIT TESTS
#===============================================================================
tests = {}

def test_pred_modular():
    print "\nMODULAR PREDICTION TEST: "
    pre = predict(1,30000) # 1 for GFS data, 2 for Winds Aloft
    origin = array([40.7500,-111.8833,1300])
    V = pre.prediction(origin)

    cart = eq.cartesian(V, origin)
    print "Cartesian: \t", cart 
    print "Initial Position: \t", origin
    print "Final Position:   \t", V
    print "Vector:           \t", eq.to_vector(cart, origin)
    
def test_winds_aloft():
    pre = predict(2) # 1 for GFS data, 2 for Winds Aloft
    origin = array([40.7500,-111.8833,1377])
    V = pre.flight_prediction(origin)
    Fpos= eq.geodetic(V, origin)
    print "Initial Position: \t", origin
    print "Final Position:   \t", Fpos
    print "Vector:           \t", eq.to_vector(V), V 

def test_GFS_file():
    pre = predict(1) # 1 for GFS data, 2 for Winds Aloft
    origin = array([40.7500,-111.8833,1377])
    V = pre.flight_prediction(origin)
    Fpos= eq.geodetic(V, origin)
    #print V
    print "Initial Position: \t", origin
    print "Final Position:   \t", Fpos
    print "Vector:           \t", eq.to_vector(V), V
    
def test_GFS_web():
    pass

def test_path_correction():
    _kml = kml.WebOutput()
    origin = (40.75,-111.8833,1322)
    ini = origin
    _kml.add_point([ini[1],ini[0],ini[2]], "Origin")
    lat = 40.75
    lon = -111.8833
    i = 1322
    points = []
    points.append(origin)
    while i < 30000:
        lat += .002
        lon += -.0024
        i += 50
        points.append((lat,lon,i))

    pre = predict(1, 30000)

    _kml.create_linestring(points, "ff0000ff", 3,"Original path", "Original Path.")
    res = pre.path_correction(origin, points)
    print len(res)
#    _kml.add_point([Final[1],Final[0],Final[2]], "Destination")
    _kml.create_linestring(res, "50f00014", 3,"Path Correction", "Path Correction.")
    _kml.save_kml("correction")
        
    
if __name__ == "__main__":
    main()
    


    

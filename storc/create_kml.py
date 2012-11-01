import simplekml
import datetime
import time
'''
Created on Jul 14, 2012

@author: John Wells
@note:     General idea is to take a set of GPS points and create a KML file out of it. If the KML is already created, we will
            want to add linestrings (refer to KML spec) to connect the points.
            TODO: Research if it's possible to create different colored linestrings.
            BLUE = Traveled path
            RED = Predicted path
'''

class WebOutput(object):
    '''
    classdocs 

    '''
    
    def __init__(self):
        '''
        Create an instance for a kml file.
        '''
        self.kml = simplekml.Kml()
        self.points = []
        self.coord = []

    def save_kml(self, filename):
        netlink = self.kml.newnetworklink(name = filename)
        netlink.link.viewrefreshmode = simplekml.RefreshMode.oninterval
        netlink.link.refreshinterval = 2 # 60 seconds.
        self.kml.save("../data/%s.kml" % filename )

    def remote_save(self, filename):
        #TODO: Program in some FTP handling to send the files to the STORC web server.
        pass
    
    def create_linestring(self, data, color, thick, path_name, desc):
        points = []
        for lat, lon, alt in data:
            points.append((lon,lat,alt))
        line = self.kml.newlinestring(name=path_name, description=desc, coords=data, altitudemode="relativeToSeaFloor", extrude=1)
        line.linestyle.color = color
        line.linestyle.ColorMode = "normal"
        line.linestyle.width = thick
        
    def add_point(self, P, Name):        
        self.kml.newpoint(name=Name, coords=[(P[0],P[1],P[2])], altitudemode="relativeToSeaFloor")

#!/usr/bin/python
#-*- coding: iso-8859-15 -*-
import socket, re, logging, serial, time
from numpy import array, std

# Local imports
import prediction as pre
import create_kml as kml


logger = logging.getLogger('MyLogger')
debug = logger.debug
info = logger.info
exception = logger.exception

packet_format = {
"APRS" : re.compile(r"""(?P<callsign>[A-Z0-9-]*)(?:>.*)[=/z]{1}(?P<position>[0-9.]+[NS]{1}/[0-9.,]+[EW]{1})(?:.*)(?P<altitude>/A=[0-9]+)""", re.VERBOSE),

"GPGGA" : re.compile(r"""
            (?:\$GPGGA,[0-9a-z.]+),(?P<position>[0-9.,]+[E|W]{1},[0-9.,]+,[N|S]{1}),(?:.*),(?P<altitude>[0-9]+),(?:\.[0-9],M),(?:.*),(?P<callsign>[A-Z0-9-]*)""", re.VERBOSE),
                 
"GPGGA-RAW" : re.compile(r"""(?:.*h)(?P<position>\d{4}\.\d{2}[N|S]/\d{4,5}\.\d{2}[E|W])(?:.*/A=)(?P<altitude>\d+)(?:/(?P<callsign>[\d\w]+))?""", re.VERBOSE)}

class listener(object):

    def __init__(self, params):
        self.lat = float(params['lat'])
        self.lon = float(params['lon'])
        self.alt = float(params['alt'])
        self.lat_threshold = float(params['lat_threshold'])
        self.lon_threshold = float(params['lon_threshold'])
        self.alt_threshold = float(params['alt_threshold'])
        
        self.ds = int(params['source'])
        self.IP = params['ip']
        self.PORT = int(params['port'])
        self.max_alt = float(params['max_alt'])
        self.fmt = params['packet_format']
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.queue = []
        self.origin = array([self.lon, self.lat, self.alt])
        self.predict = pre.predict(self.ds, self.max_alt)
        self.predict.prediction(self.origin)
                
    def start(self):
        '''
        Loop that listens for traffic on the supplied port.
        When a packet is received, attempt to parse the APRS packet.
        The parser(packet) returns None in the event the packet could not be parsed properly.
        A proper packet will at least begin with the callsign (Hardcoded as of 8/10/2012) KE7SWA-STORC>
        
        Should the packet contain a valid APRS packet, it is added to the queue, and evaluated further.
        
        '''
        
        prev_alt = 0 
        packet_count = 0
        packet_stack = []
        self.sock.bind((self.IP, self.PORT - 1))
        self.sock.connect((self.IP, self.PORT))
        while True:
            packet = self.sock.recv(1024)
            print time.strftime("%H:%M:%S", time.localtime()), "Received packet: ", packet
            
            packet = self.parser((packet))
            print "Parsed packet point:", packet
            if packet is not None:
                packet_stack.append(packet)
                packet_count += 1
                
                # Error checking for packets. Ensures location is accurate.
                if(packet_count == 3):
                    lat_std = std([(t) for t, u, v in packet_stack])
                    lon_std = std([(u) for t, u, v in packet_stack])
                    alt_std = std([(v) for t, u, v in packet_stack])
                else:
                    continue
                   
                if(lat_std < self.lat_threshold) and (lon_std < self.lon_threshold): # and (alt_std < 400):
                    for p in packet_stack:
                        self.queue.append(p)  
                    self.print_info(packet_stack)         
                #END Error checking
                    for p in packet_stack:
                        try:
                            print "Trying to plot..."
                            index = len(self.queue)
                            if prev_alt > p[2]:
                                ascent = self.queue
                                apex = prev_alt # Set the apex, the highest point of ascent.

#                                print "Correcting path..."
#                                correction = self.predict.path_correction(self.origin, ascent, apex)
#                                print "To KML"
#                                self.correction_to_kml(correction)
                            
                            print "Sending queue to correction.kml"
                            self.current_to_kml(self.queue)
                            prev_alt = float(p[2])
                        
                        except: 
                            print "Invalid coordinate format for %s" % p
                            self.queue.remove(p)
                    
                    ## Reset the packet stack.
                    packet_stack = []
                    packet_count = 0
                
        
    def parser(self, packets):
        points = []
            
        mat = packet_format[self.fmt].match(packets) # Make me a match!
        print "Packet after regex:", mat
        if mat is not None:# and mat.group('callsign') == 'KE7SWA':
            if mat.group('callsign'):
                _callsign = mat.group('callsign')
#                _callsign = mat.group('callsign')
            _pos = mat.group('position')
            _pos = _pos.replace(',', '/') # Ensures continuity between packet formats.
            _alt = mat.group('altitude')
            _lat = _pos.split('/')[0]
            _lon = _pos.split('/')[1]
            print _lat, _lon
                # Dividing by 100 because the lat/lon seem to have DD(D)MM.SS format. Prediction takes a float in the form DD.MMSS...
                #Southern hemisphere is negative.
            if _lat[len(_lat) - 1] == 'N':
                lat_min = float(_lat[2:-1]) / 60
                lat = float(_lat[:2]) + lat_min
            else:
                lat_min = float(_lat[2:-1]) / 60
                lat = float(_lat[:2]) - lat_min
                    
                #Western hemisphere is negative.
            if _lon[-1] == "W":
                lon_min = float(_lon[3:-1]) / 60
                lon = float(_lon[:3]) + lon_min
                lon *= -1
            else:
                lon_min = float(_lon[3:-1]) / 60
                lon = float(_lon[:3]) + lon_min
            if "\A=" in _alt:
                alt = float(_alt[3:])
            else:
                alt = float(_alt) * 0.3048

            points = (lon, lat, alt)
            return points
        else:
            return None

    def current_to_kml(self, coords):
        '''
        Sends a RED line indicating CURRENT path.
        '''
        _kml = kml.WebOutput()
        #for c in coords:
            #print c
            #_kml.add_point(c, "Insert point timestamp")
        _kml.create_linestring(coords, "ff0000ff", 3, "Current Path", "Current path of the balloon, from real time updates.")
        _kml.save_kml("current_path")
        
    def correction_to_kml(self, coords):
        '''
        Sends a purple line indicating CURRENT path.
        '''
        _kml = kml.WebOutput()
#        for c in coords:
#            print c
#            _kml.add_point([c[1],c[0],c[2]], "Insert point timestamp")
        c = coords[len(coords) - 1]
        _kml.add_point([c[1], c[0], c[2]], "Projected landing site")
        _kml.create_linestring(coords, "5014F08C", 3, "Adjusted trajectory", "The project landing path given the course heading of the ascent.")
        _kml.save_kml("correction")
        
#===========================================================================
# Parse Testing
#===========================================================================
def test_listen():
    coords = []
    packets = [
             """AE6ST-2>S4QSUR,ONYX*,WIDE2-1,qAR,AK7V:`,6*l"Zj/]"?L}"""
             , """KE7SWA-STORC>APU25N,JM6ISF-3*,TRACE3-2,qAR,JA6YWR:=4101.57N/11183.33WIJ-net 144.66MHz 9600bps /A=12345 I-gate {UIV32N}"""
             , """KE7SWA-STORC>APU25N,JM6ISF-3*,TRACE3-2,qAR,JA6YWR:=4075.57N/11202.43WIJ-net 144.66MHz 9600bps /A=1135 I-gate {UIV32N}"""
             , """KE7SWA-STORC>APU25N,JM6ISF-3*,TRACE3-2,qAR,JA6YWR:=4101.57N/11183.33WIJ-net 144.66MHz 9600bps /A=12345 I-gate {UIV32N}"""
             , """KE7SWA-STORC>APU25N,JM6ISF-3*,TRACE3-2,qAR,JA6YWR:=4075.57N/11202.43WIJ-net 144.66MHz 9600bps /A=1135 I-gate {UIV32N}"""
             , """KE7SWA-STORC>APU25N,JM6ISF-3*,TRACE3-2,qAR,JA6YWR:=4101.57N/11183.33WIJ-net 144.66MHz 9600bps /A=12345 I-gate {UIV32N}"""
             , """KE7SWA-STORC>APU25N,JM6ISF-3*,TRACE3-2,qAR,JA6YWR:=4075.57N/11202.43WIJ-net 144.66MHz 9600bps /A=1135 I-gate {UIV32N}"""
            ]
#    lis = listener(params)
#    for p in packets:
#        x = lis.parser(p)
#        if x is not None:
#            coords.append(x)
#    print coords
#    lis.current_to_kml(coords)


def main():
    test_listen()
    pass
    
if __name__ == '__main__':
    main()

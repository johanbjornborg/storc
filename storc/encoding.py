#!/usr/bin/python
#-*- coding: iso-8859-15 -*-
import re
from numpy import array, std
strings = ["����fbb`�����@`����b@b����d@c�/052602h4038.37N/11153.91WO209/000/A=004300/KE7SWA",
          "����fbb`�����@`����b@b����d@c�/052608h4038.37N/11153.91WO209/000/A=004300",
          "����fbb`�����@`����b@b����d@c�/052618h4038.37N/11153.91WO209/000/A=004300/KE7SWA",
          "����fbb`�����@`����b@b����d@c�/052650h4038.37N/11153.91WO209/000/A=004300/KE7SWA",]

packet_format = {
"APRS" : re.compile(r"""(?P<callsign>[A-Z0-9-]*)(?:>.*)[=/z]{1}(?P<position>[0-9.]+[NS]{1}/[0-9.,]+[EW]{1})(?:.*)(?P<altitude>/A=[0-9]+)""", re.VERBOSE),

"GPGGA" : re.compile(r"""(?:\$GPGGA,[0-9a-z.]+),(?P<position>[0-9.,]+[E|W]{1},[0-9.,]+,[N|S]{1}),(?:.*),(?P<altitude>[0-9]+),(?:\.[0-9],M),(?:.*),(?P<callsign>[A-Z0-9-]*)""", re.VERBOSE),
                 
"GPGGA-RAW" : re.compile(r"""(?:.*h)(?P<position>\d{4}\.\d{2}[N|S]/\d{4,5}\.\d{2}[E|W])(?:.*/A=)(?P<altitude>\d+)(?:/(?P<callsign>[\d\w]+))?""", re.VERBOSE)}

fmt = "GPGGA-RAW"
def parser(packets):
        points = []

#            print packets.encode("ascii", 'ignore')
        packets = re.sub(r"[^\w]", ' ', packets)
        mat = packet_format["GPGGA-RAW"].match(packets)

        if mat is not None: #and mat.group('callsign') == 'KE7SWA':
            if mat.group('callsign'):
                _callsign = mat.group('callsign')
            _pos = mat.group('position')
            _pos = _pos.replace(',','/') # Ensures continuity between packet formats.
            _alt = mat.group('altitude')
            _lat = _pos.split('/')[0]
            _lon = _pos.split('/')[1]
            print _lat, _lon, _alt, _pos
            # Dividing by 100 because the lat/lon seem to have DD(D)MM.SS format. Prediction takes a float in the form DD.MMSS...
            #Southern hemisphere is negative.
            if _lat[len(_lat) - 1] == 'N':
                lat = float(_lat[0:len(_lat)-1]) / 100
            else:
                lat = float(_lat[0:len(_lat)-1]) / 100 * (-1)
                
            #Western hemisphere is negative.
            if _lon[-1] == "W":
                lon = float(_lon[0:-1]) / 100 * (-1)
            else:
                lon = float(_lon[0:-1]) / 100
            if "\A=" in _alt:
                alt = float(_alt[3:])
            else:
                alt = float(_alt)
            if "GPGGA-RAW" in fmt:
                alt *= 0.3048
                 
            points = (lat,lon,alt)
            return points
##            else:
##                return None
#        except:
#            print "broke it"
#            return None
packet_stack = []     
for s in strings:

    packet_stack.append(parser(s))
print packet_stack
lat_std = std([(t) for t,u,v in packet_stack])
lon_std = std([(u) for t,u,v in packet_stack])
alt_std = std([(v) for t,u,v in packet_stack])
print [(t) for t,u,v in packet_stack]
print lat_std, lon_std, alt_std

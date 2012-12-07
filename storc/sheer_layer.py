from urllib2 import urlopen
from time import gmtime, timezone
import re

'''
Created on Jul 8, 2012

@author: John Wells
@contact: john.wells@utah.edu
@summary: Pulls and parses weather data from GFS|NOAA. Data is parsed and organized into sheer layers, based on altitude reporting. 
'''
            
#TODO: Write function to retrieve GRIB data and pull useful data out of it.
def retrieve_grib():
    pass

def get_gfs():
    """
    Pulls weather information out of a file. 
    The file itself is obtained from  http://weather.uwyo.edu/upperair/sounding.html
    The format is as follows:
    
    PRES   HGHT   TEMP   DWPT   RELH   MIXR   DRCT   SKNT   THTA   THTE   THTV
     hPa     m      C      C      %    g/kg    deg   knot     K      K      K 
    873.0   1289   20.0    4.0     35   5.87    180      6  304.8  322.9  305.8.
    Currently we are only interested in Direction, Sknt (speed in knots), Height, and Temperature.
    In the future, pressure at altitude may be implemented as well.
    curl --data "region=naconf&TYPE=TEXT%3ALIST&YEAR=2012&MONTH=09&FROM=1400&TO=1500&STNM=72572" http://weather.uwyo.edu/cgi-bin/sounding > weather_test_dump.txt

    grep -Pzo '(?s)(?<=(<H2>))(.*?)(?=(</H2>))|(?<=(<PRE>))(.*?)(?=(</PRE>))|(?<=(<H3>))(.*?)(?=(</H3>))' weather_test_dump.txt > weather_test_parsed.txt

    """
    time = gmtime() #Greenwich mean time
    
    year = time[0]
    month = time[1]
    day = time[2]
    hour = time[3]
            
    if(hour < 12):
        hour = "00"
    elif(12 < hour < 23):
        hour = "12"
    else:
        hour = "00"
        day = time[2] + 1
    if(day < 10):
        day = "0" + str(day)
    else:
        day = str(day)
        
    fmt = (year, month, day, hour)
    print fmt
    url = "http://weather.uwyo.edu/cgi-bin/sounding?region=naconf&TYPE=TEXT%3ALIST&YEAR={0}&MONTH={1}&FROM={2}{3}TO={2}{3}&STNM=72572".format(fmt[0], fmt[1], fmt[2], fmt[3])
    print url
    website = urlopen(url).read() 
    print "Website read"
    regex = re.compile(r'[-][\d+-\.\s]+')
    matches = regex.findall(website)
    m = matches[2].split('\n')
    print "Matches made"
    for n in m:
        print n
        try:
            pres = n.split()[0]
            alt = n.split()[1]
            temp = n.split()[2]
            heading = n[43:49].strip()
            speed = n[49:58].strip()
            if(float(alt) and float(heading) and float(speed) and float(pres) and float(temp)):
                yield [float(alt), float(heading), float(speed) * 0.514, float(pres), float(temp)]
        except:
            continue
    print "End of sheer layer"

def get_gfs_local():
    """
    Retrieves a local cached copy of the GFS forecast data. 
    """
    f = open('../data/wind_data.txt', 'r+')
    data = f.read()
    regex = re.compile(r'[-][\d+-\.\s]+')
    matches = regex.findall(data)     
    m = matches[2].split('\n')
    for mat in matches:
        print mat
    for n in m:
        print n
        try:
            pres = n.split()[0]
            alt = n.split()[1]
            temp = n.split()[2]
            heading = n[43:49].strip()
            speed = n[49:58].strip()
            if(float(alt) and float(heading) and float(speed) and float(pres) and float(temp)):
                yield [float(alt), float(heading), float(speed) * 0.514, float(pres), float(temp)]
        except:
            continue
    print "End of sheer layer"

def get_winds_aloft():
    """
    Reads the Winds Aloft (WA) data from Weather.gov.
    
    The format is as follows:
    FT  3000    6000    9000   12000   18000   24000  30000  34000  39000
    SLC      9900    9900+18 2809+10 3027-08 2825-19 264334 254644 254153
    FT indicates the forecast location, the numbers indicate the forecast levels in feet. 
    
    Wind direction is coded as a number between 51 and 86 (vice 01 to 36) when the wind speed is 100 knots or greater. 
    To derive the actual wind direction, subtract 50 from the first pair of numbers. 
    To derive wind speed, add 100 to the second pair of numbers. 
    
    For example, a forecast at 39,000 feet of "731960" shows a wind direction from 230 degrees (73-50=23) with a wind speed of 119 knots (100+19=119). 
    Above 24,000 feet the temperature is assumed to be negative, therefore the third pair of numbers indicate a temperature of minus 60 degrees Celsius. 
    
    If the wind speed is forecast to be 200 knots or greater, the wind group is coded as 199 knots.
    For example, "7799" is decoded as 270 degrees at 199 knots or greater.
    
    Wind direction is coded to the nearest 10 degrees. 
    When the forecast speed is less than 5 knots, the coded group is "9900" and read, "LIGHT AND VARIABLE."
    
    All elevations are converted to meters. 
    
    For the fields that are used in GFS but not in WA, None is passed into the list. 
    """

    website = urlopen("http://aviationweather.gov/products/nws/saltlakecity").read() # Low Altitudes
    reg = re.compile(r'(SLC.*)')
    web_data = reg.findall(website)
    low_alt = web_data[0].split()
    website = urlopen("http://aviationweather.gov/products/nws/saltlakecity?fint=06&lvl=hi").read() # High Altitudes
    reg = re.compile(r'(SLC.*)')
    hi_data = reg.findall(website)
    high_alt = hi_data[0].split() 
    val = low_alt + high_alt[2:]
    altitudes = [6000, 9000, 12000, 18000, 24000, 30000, 34000, 39000, 45000, 53000]
    for i in range(1, len(val)):
        heading = float(val[i][0:2])
        wspd = float(val[i][2:4]) * 0.514444
        
        temp = val[i][4:]
        if(temp):
            if (temp[0:1] is '+'):
                temp = float(temp[1:])
            elif (temp[0:1] is '-'):
                temp = float(temp)
            elif (temp[0:1] is not '+' and temp[0:1] is not '-'):
                temp = -float(temp[0:])
        else:
            temp = None        
        if heading == 99 and wspd == 0:
            heading = 0
            wspd = 0
            #continue
        
        #If windspeed is 200 knots or greater... Find a bomb shelter.
        if heading > 50 and wspd > 99:
            heading = heading - 50
            wspd = 200
            
        #If windspeed is 100 knots or greater.
        if heading > 50:   
            heading = heading - 50
            wspd = wspd + 100

        yield [altitudes[i] * 0.348, heading * 10, wspd, None, temp] # Altitude, Heading, Speed, No value for Pressure, Temperature.


def print_tests():

    print "------WYOMING GFS DATA------"
    for d in get_gfs():
        print d
    print "-----WINDS ALOFT------"
    for c in get_winds_aloft():
        print c    
    print "------GFS LOCAL DATA-------"
    for d in get_gfs_local():
        print d
        
def main():
    print_tests()

if __name__ == "__main__":
    main()



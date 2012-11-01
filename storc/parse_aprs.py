import numpy as np
import socket
from numpy.numarray.numerictypes import Int16

class parse_aprs(object):
    '''
    classdocs
    '''

    def __init__(self, data):
        '''
        Constructor
        '''
        Callsign = "Unknown"
        PacketType = "Unknown"
        Latitude = ""
        Longitude = ""
        Altitude = "0"
        GPSTime = ""
        RawData = ""
        Symbol = ""
        Heading = "000"
        PHG = ""
        Speed = ""
        Destination = ""
        Status = ""
        WindDirection = ""
        WindSpeed = ""
        WindGust = ""
        WeatherTemp = ""
        RainHour = ""
        RainDay = ""
        RainMidnight = ""
        Humidity = ""
        Pressure = ""
        Luminosity = ""
        Snowfall = ""
        Raincounter = ""
        

    def Parse(self, line):
        
                #===============================================================
                # #/*  # Strip CR then LF at the EOL
                #  if (line[(line.Length - 1, 1) == "\r" or line[(line.Length - 1, 1) == "\n")
                #  
                #      line = line.Remove(0, (line.Length - 2))
                #  
                # */
                #===============================================================
        LongOffset = 0
        
        # Is this a valid APRS packet?
        FirstChr = line.find(">")
        if FirstChr != -1:
            #Parse Callsign
            Callsign = line.Remove(FirstChr, (line.Length - FirstChr))
            Destination = line[FirstChr + 1: 6]

            #Is this a status report?
            FirstChr = line.find(":>")
            if (FirstChr > line.find(">")):
                PacketType = "Status Report"
                RawArray = line[FirstChr + 2: len(line) - FirstChr - 2]
                
                if (RawArray[6].lower() == "z"):
                    GPSTime = line[FirstChr + 2:6]
                    Status = line[FirstChr + 9: len(line)- FirstChr - 9]
                
                else:
                    Status = line[FirstChr + 2: len(line) - FirstChr - 2]
                        
                    #Is this a GPGGA packet?
                FirstChr = line.find(":$GPGGA,")

                if (FirstChr != -1):
                    PacketType = "GPGGA"
                    RawData = line[FirstChr: (len(line)- FirstChr)]
                    Split = RawData.split(',')#.Split(new char[]  ',' )
                    GPSTime = Split[1]

                    #Latitude
                    degLatitude = Split[2]
                    degLatMin = float(degLatitude[2: len(degLatitude) - 2])
                    degLatMin = (degLatMin / 60)
                    Latitude = degLatitude[0:2] + degLatMin[1:len(degLatMin) - 1]

                    if (Split[3] == "S"):
                        Latitude = "-" + Latitude
                        

                    #Longitude
                    degLongitude = Split[4]
                    degLonMin = float(degLongitude[3: len(degLongitude)- 3])
                    degLonMin = (degLonMin / 60)
                    Longitude = degLongitude[0:3] + degLonMin[1: len(degLonMin)- 1]

                    if (Split[5] == "W"):
                        Longitude = "-" + Longitude
                    
                    Altitude = float(Split[9])
                    

                    # Is this a Mic-E packet?
                FirstChr = line.find(":`")
                SecondChr = line.find(":'")
                if ((FirstChr != -1) or (SecondChr != -1)):
                    if (FirstChr != -1):
                        PacketType = "New Mic-E"
                    else:
                        PacketType = "Old Mic-E"
                        FirstChr = SecondChr
                        
                    #DestinationArray = Destination.ToCharArray()
                    #Lattitude
                    degLatitude = (Int16(Destination[0]) & 0x0F) + (Int16(Destination[1]) & 0x0F)
                    degLatMin = float(Int16(Destination[2] & 0x0F) + Int16(Destination[3] & 0x0F) + "." + Int16(Destination[4] & 0x0F) + Int16(Destination[5] & 0x0F))
                    degLatMin = (degLatMin / 60)
                    Latitude = degLatitude + degLatMin[1:len(degLatMin)- 1]
                    if (Int16(Destination[3]) < 80):
                        Latitude = "-" + Latitude
                        
                    #Longitude
                    InformationField = line[FirstChr + 1: len(line)- FirstChr - 1]

                    if (Int16(Destination[4]) > 79):
                        LongOffset = 100
                        
                    degLongitude = Int16(InformationField[1]) - 28 + LongOffset
                    if ((degLongitude > 179) and (degLongitude < 188)):
                        degLongitude = degLongitude - 80
                        
                    if ((degLongitude > 190) and (degLongitude < 199)):
                        degLongitude = degLongitude - 190
                        
                    degLonMin = Int16(InformationField[2]) - 28
                    if (degLonMin > 59):
                        degLonMin = degLonMin - 60
                        
                    degLonMin = float(degLonMin + "." + str(Int16(InformationField[3]) - 28))
                    degLonMin = (degLonMin / 60)
                    Longitude = str(degLongitude) + str(degLonMin)[1: len(str(degLonMin))- 1]
                    if (Int16(Destination[5]) > 79):
                        Longitude = "-" + Longitude
                        
                    Symbol = str(InformationField[8]) + str(InformationField[7])

                    Speed = str(((float((Int16(InformationField[4])) - 28) * 10) + (np.floor((float(Int16(InformationField[5])) - 28) / 10))) % 800)
                    Heading = str((((((float(Int16(InformationField[5])) - 28) / 10) - np.floor((float(Int16(InformationField[5])) - 28) / 10)) * 1000) + (float(Int16(InformationField[6])) - 28)) % 400)
                    if (str(InformationField[13]) == ""):
                        Altitude = str((((np.int32(InformationField[10]) - 33) * 8281) + ((np.int32(InformationField[11]) - 33) * 91) + ((np.int32(InformationField[12]) - 33)) - (10000)))
                        

                    

                #Is this a location packet?
                FirstChr = line.find(":/")  # With Timestamp
                SecondChr = line.find(":!") # Without Timestamp
                ThirdChr = line.find(":@")  # With Timestamp and APRS Messaging
                FourthChr = line.find(":=") # Without Timestamp and Messaging

                if (ThirdChr != -1):
                    FirstChr = ThirdChr
                    
                if (FourthChr != -1):
                    SecondChr = FourthChr
                    

                if ((FirstChr != -1 and line[FirstChr + 8: 1].upper() == "H") or (FirstChr != -1 and line[FirstChr + 8: 1].upper() == "Z") or (FirstChr != -1 and line[FirstChr + 8: 1].upper() == "/") or (SecondChr != -1 and line[SecondChr + 9: 1].upper() == "S") or (SecondChr != -1 and line[SecondChr + 9: 1].upper() == "N")):
                    
                    PacketType = "Location"

                if ((FirstChr != -1 and line[FirstChr + 8: 1].upper() == "H") or (FirstChr != -1 and line[FirstChr + 8: 1].upper() == "Z") or (FirstChr != -1 and line[FirstChr + 8: 1].upper() == "/")):
                    GPSTime = line[FirstChr + 2: 6]
                        
                else:
                    FirstChr = SecondChr - 7
                        
                Symbol = line[FirstChr + 17: 1] + line[FirstChr + 27: 1]
                degLatMin = float(line[FirstChr + 11: 5])
                degLatMin = (degLatMin / 60)
                Latitude = line[FirstChr + 9: 2] + str(degLatMin)[1:str(len(degLatMin) - 1)]
                                                                  
#                if (line[FirstChr + 16: 1] == "S"):
#                    Latitude = "-" + Latitude
#                
                degLonMin = float(line[FirstChr + 21: 5])
                degLonMin = (degLonMin / 60)
                Longitude = line[FirstChr + 19: 2] + str(degLonMin)[1: str(len(degLonMin)- 1)]
                if (line[FirstChr + 26: 1] == "W"):
                    Longitude = "-" + Longitude
                        
                # Is this packet a Weather Report?
                if (line[FirstChr + 27: 1] == "_" and line[FirstChr + 31: 1] == "/"):
                    PacketType = "Weather Report"
                    WindDirection = line[FirstChr + 28: 3]
                    WindSpeed = line[FirstChr + 32: 3]
                    wrpos = [10]
                    wrpos[0] = line.find("g", FirstChr + 27)
                    wrpos[1] = line.find("t", FirstChr + 27)
                    wrpos[2] = line.find("r", FirstChr + 27)
                    wrpos[3] = line.find("p", FirstChr + 27)
                    wrpos[4] = line.find("P", FirstChr + 27)
                    wrpos[5] = line.find("h", FirstChr + 27)
                    wrpos[6] = line.find("b", FirstChr + 27)
                    wrpos[7] = line.find("L", FirstChr + 27)
                    wrpos[8] = line.find("s", FirstChr + 27)
                    wrpos[9] = line.find("#", FirstChr + 27)
                    if (wrpos[0] != -1):
                        WindGust = line[wrpos[0] + 1: 3]
                            
                    if (wrpos[1] != -1):
                        WeatherTemp = line[wrpos[1] + 1: 3]
                        
                    if (wrpos[2] != -1):
                        RainHour = line[wrpos[2] + 1: 3]
                            
                    if (wrpos[3] != -1):
                        RainDay = line[wrpos[3] + 1: 3]
                            
                    if (wrpos[4] != -1):
                        RainMidnight = line[wrpos[4] + 1: 3]
                            
                    if (wrpos[5] != -1):
                        Humidity = line[wrpos[5] + 1: 2]
                            
                    if (wrpos[6] != -1):
                        Pressure = line[wrpos[6] + 1: 3]
                            
                    if (wrpos[7] != -1):
                        Luminosity = line[wrpos[7] + 1: 3]
                            
                    if (wrpos[8] != -1):
                        Snowfall = line[wrpos[8] + 1: 3]
                            
                    if (wrpos[9] != -1):
                        Raincounter = line[wrpos[9] + 1: 3]
                        
                    else:

                        if (line.find("/A=") != -1):
                            Altitude = str(np.int32(float(line[line.find("/A=") + 3:6]) * 12 / 39.37))
                            
                        if (line[FirstChr + 28: 3].upper() == "PHG"):
                            PHG = line[FirstChr + 31: 4]
                            
                        if (line[FirstChr + 31: 1] == "/"):
                            Heading = line[FirstChr + 28: 3]
                            Speed = line[FirstChr + 32: 3]
                            
                        
                    
            #Is this packet a Positionless Weather Report?
            FirstChr = line.find(":_")
            if (FirstChr != -1):
                PacketType = "Weather Report"
                wrpos = []
                wrpos[0] = line.find("g", FirstChr)
                wrpos[1] = line.find("t", FirstChr)
                wrpos[2] = line.find("r", FirstChr)
                wrpos[3] = line.find("p", FirstChr)
                wrpos[4] = line.find("P", FirstChr)
                wrpos[5] = line.find("h", FirstChr)
                wrpos[6] = line.find("b", FirstChr)
                wrpos[7] = line.find("L", FirstChr)
                wrpos[8] = line.find("s", FirstChr)
                wrpos[9] = line.find("#", FirstChr)
                wrpos[10] = line.find("c", FirstChr)
                wrpos[11] = line.find("s", FirstChr)

                if (wrpos[0] != -1):
                    WindGust = line[wrpos[0] + 1: 3]
                        
                if (wrpos[1] != -1):
                    WeatherTemp = line[wrpos[1] + 1: 3]                        
                if (wrpos[2] != -1):
                    RainHour = line[wrpos[2] + 1: 3]
                if (wrpos[3] != -1):
                    RainDay = line[wrpos[3] + 1: 3]
                if (wrpos[4] != -1):
                    RainMidnight = line[wrpos[4] + 1: 3]
                if (wrpos[5] != -1):
                    Humidity = line[wrpos[5] + 1: 2]
                if (wrpos[6] != -1):
                    Pressure = line[wrpos[6] + 1: 3]
                if (wrpos[7] != -1):
                    Luminosity = line[wrpos[7] + 1: 3]
                if (wrpos[8] != -1):
                   Snowfall = line[wrpos[8] + 1: 3]
                if (wrpos[9] != -1):
                    Raincounter = line[wrpos[9] + 1: 3]
                if (wrpos[10] != -1):
                    WindDirection = line[wrpos[10] + 1: 3]
                if (wrpos[11] != -1):
                    WindSpeed = line[wrpos[11] + 1: 3]
                        
                GPSTime = line[FirstChr + 2: 8]
      
      
def main():
    s = socket.socket()
    host = socket.gethostname()
    port = 12255
    s.bind((host,port))
    pass
              
if __name__ == "__main__":
    main()          
            

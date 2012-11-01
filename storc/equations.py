from numpy import array, cos, sin, arctan, sqrt, pi, radians, degrees, e, log, absolute
from math import pow
import exceptions
'''
Created on Jul 8, 2012

@author:  John Wells
@author:  Team STORC

'''

test_eq = {}
initials = {}
free_lift = 9.81*(1.3+1)    

#===============================================================================
# Equations
#===============================================================================

def ascent_rate(alt, Pnot = None, Temp = None):
    '''
    Calculates the ascent rate of the balloon.
    Currently assumes a payload mass of 1.3 kg.
    Formula: (8*R*g / 3*Cd) * (1 - (3*m/4*pi*Pair^3))
    Where:
    R = Radius of the balloon.
    g = force of gravity
    m = mass
    Cd = Coefficient of Drag. Assumed to be .25 (drag of a sphere). 
    '''
    if(Pnot is None):
        Pnot = pressure(alt)
    if(Temp is not None):
        Temp += 274.15
        Pair = air_density(Pnot, Temp)
    else:
        Pair = air_density(Pnot, 288.15) # 15 degrees Celsius.
    
    # TRYING A NEW EQUATION HERE:
    
    #Equation Known values.   
    R = 4*pi*balloon_radius(3.048, alt)**3
    Cd = 0.25
    g = 9.80
    m = 1.3 # Kg
    num1 = 8*R*g
    den1 = 3*Cd
    num2 = 3*m
    den2 = 4*pi*Pair*(R**3)
    try:
        res = (num1/den1)*(1-(num2/den2))
    except exceptions.ZeroDivisionError:
        print "Division by zero at Altitude: ", alt
        return 5
    #R = NET LIFT
    # DEBUG VALUES:
    #V = (8Rg/3Cd)(1-(3m/4pipairR**3))
#    print pow(absolute(res),(float(1)/float(3)))
#    return pow(absolute(res),(float(1)/float(3)))
    return 5
    
def descent_rate(alt, Pnot = None, Temp = None):
    # DEBUG VALUES:
    # Formula: D = sqrt( 8*m*g / pi*pressure*Drag*impact velocity^2 )
    if(Pnot is None):
        Pnot = pressure(alt)
    if(Temp is not None):
        Temp += 274.15
        Pair = air_density(Pnot, Temp)
    else:
        Pair = air_density(Pnot, 288.15) # 15 degrees Celsius.
    
    #Equation Knowns.    
#    R = 4*pi*balloon_radius(3.048, alt)**3 ## Bad code? There is no balloon to affect drag.
    R = 4*pi*(0.762)**3
    Cd = 1.5
    g = 9.80
    m = 1.3 # Kg
    num1 = 8*R*g
    den1 = 3*Cd
    num2 = 3*m
    den2 = 4*pi*Pair*(R**3)

    try:
        res = (num1/den1)*(1-(num2/den2))

    except exceptions.ZeroDivisionError:
        print "Division by zero at Altitude: ", alt
        return -3
    #print -pow(res,(float(1)/float(3)))
    return -pow(absolute(res),(float(1)/float(3)))
    #return -3

def air_density(Pnot, T):
    '''
    http://en.wikipedia.org/wiki/Density_of_air#Altitude
    Density at altitude = p*M / R*T
    p = Pressure at altitude
    M = Molar mass of air = 0.0289644 kg/mol
    R = Ideal gas constant = 8.31447
    T = Temperature at altitude
    '''
    numer = (Pnot/10) * 0.0289644 
    denom = 8.31447 * T 
    return numer/denom

def balloon_radius(r0, alt):
    '''
    Calculated using Ideal gas law:
    P1V1 = P2V2
    
    V2 = P1V1 / P2
    Where V2 can be broken down into 4/3*pi*r^3 (Balloon is assumed to be spherical).
    '''
    #r = [(3*P0V0)/(4pi*P1)]^1/3
    P0 = pressure(1300) #1300 meters is SLC altitude approx.
    V0 = (4/3)*pi*(r0**3)
    P1 = pressure(alt)
    numer = 3*P0*V0
    denom = 4*P1*pi
    res = pow((numer/denom),(1/3))#(numer/denom)**(1/3)
    return res
     
    pass

def launch_radius(alt, V, Temp):
    '''
    TODO: Figure out how to determine launch radius.    
    ''' 
    return 2
    
    
def launch_gas_amount(alt, Temp):
    '''
    
    '''
    pass

def pressure(alt):
    '''
    Given an altitude, determine the atmospheric pressure.
    Limitations: Assumes a constant temp of 200.15 Kelvin... A little low.
    http://en.wikipedia.org/wiki/Atmospheric_pressure#Altitude_atmospheric_pressure_variation
    pnot*e^(-(g*m*alt)/(R*T0))
    
    '''
    # Formula: P0*e(- g*M*alt / R*T0 )
    # Knowns:
    P0 = 101325
    T0 = 200.15 # Kelvin
    g = 9.80665
    M = 0.0289644
    R = 8.31447
    Rm = 0.034
    # Equation
    Ans =  P0 * e**(-(g*alt*0.0289644)/(R*T0))
    return Ans
    
    pass

def burst_alt(Dl, Db):
    '''
    http://endeavours.org/Events/BalloonFest2012/Documents/Balloon%20Rise%20Rate%20and%20Bursting%20Altitude.pdf
    -OR-
    Air density Model*ln(1/Burst Vol Ratio)
    '''
    alt = 102500 * log(Db/Dl)
    return alt
    
def time_to_burst():
    '''
    Burst height / Ascent Rate
    '''
    pass

def predicted_ascent_rate(alt):
    '''
    Credit to Steve Randall for his spreadsheet.
    sqrt(Lift_free / .5*Cd*Pair*A)
    Pair = air density at STP = 1.205
    A = Cross sectional area of launch radius. pir**2
    '''
    Lf = float(free_lift())
    denom = (.5*.25*float(pressure(alt))*float(cross_area(alt)))
    res = Lf / denom
    return sqrt(res)

def cross_area(alt):
    '''
    Cross-sectional radius at altitude
    '''
    
    r0 = initials['radius']
    r = float(balloon_radius(r0, alt))
    return pi*r**2

def free_lift():
    '''
    Gross lift: G_l = V_L *(Pair - Phe)
    Vol at launch = V_L
    Pair STP = 1.205
    Phe STP = .1786
    
    Free(net) lift F_l = G_l - (M_balloon + M_payload) * 9.81 (Newtons)
    '''
    V_L = float(launch_volume())
    Phe = 0.1786
    Pair = 1.205
    M_b = float(initials['balloon_mass'])
    M_p = float(initials['balloon_payload'])
    G_l = V_L *(Pair - Phe)
    F_l = G_l - (M_b + M_p) * 9.81
    return F_l

#===============================================================================
# Vector / Coordinate equations
#===============================================================================


def launch_volume():
    pass

def geodetic(V, Pos):
    """
    Takes the change in position given by a Vector V and returns the latitude / longitude equivalent (in kilometers). 
    Initial units of V are in meters. 
    Returns a vector containing Geodatic coordinates for V.
    @V: Distance vector. X,Y,Z representation of movement.
    @Pos: Initial Position. Geodatic coordinates.
    @lat_len: Length of 1 degree of latitude at 40 degrees north of equator.
    @long_len: Length of 1 degree of longitude at 40 degrees north of equator.
    
    TODO: Look up Haversine distance, and try to implement.
    R = earth radius (mean radius = 6371km)
    Delta_lat = lat2 - lat1
    Delta_long = long2 - long1
    a = sin2(Delta_lat/2) + cos(lat1).cos(lat2).sin2(Delta_85long/2)
    c = 2.atan2(sqrt(a), sqrt(1-a))
    d = R.c
    """
    
    lat_len = 111.034637791
    long_len = 85.39382609
    deltaLat = (V[1] / 1000) / lat_len
    deltaLon = (V[0] / 1000) / long_len
    
    return array([Pos[0] + deltaLon, Pos[1] + deltaLat,V[2]])

def cartesian(V, Pos):
    lat_len = 111.034637791
    long_len = 85.39382609
    deltaLat = (V[1] - Pos[1]) * lat_len
    deltaLon = (V[0] - Pos[0]) * long_len
    return array([deltaLon, deltaLat, V[2]])
    

def to_vector(V, origin):
    """
    Converts an XYZ coordinate into a vector.
    Returns a tuple [magnitude (distance), direction]
    Ignores height vector. This is primarily for distance. in XY or Lat/Long
    """
    X = radians(V[0])# - (origin[0])
    Y = radians(V[1])# - (origin[1])
    
    magnitude = sqrt(V[0]**2  + V[1]**2)
    if X >= 0 and Y >= 0: # Quadrant 1
        dir = arctan(X/Y)
    elif (X < 0 and Y > 0) or (X < 0 and Y < 0): # Quadrants 2 and 3
        dir = arctan(X/Y) + pi
    elif (X > 0 and Y < 0): # Quadrant 4
        dir = arctan(X/Y) + (2*pi)
        
    theta = dir
    if 0 < theta < pi/2:
        theta = pi/2 - theta # 90 - Theta if 0 <= Theta <= 90
    else:
        theta = 7.85398163 - theta # 450 - Theta if 90 < Theta < 360
    return [magnitude , degrees(theta)]
    
def geo_to_ECEF():
    pass

def ECEF_to_geo():
    pass    
    
    
#===============================================================================
# UNIT TESTS
#===============================================================================

def test_pressure():
    print "Pressure test 0:i:25 * 1000"
    for i in range(25):
        print pressure(i*1000)
        
def test_ascent():
    print "Ascent Rates [3000,10000,20000,25000,30000]meters"
    print ascent_rate(3000)
    print ascent_rate(10000)
    print ascent_rate(20000)
    print ascent_rate(25000)
    print ascent_rate(30000)
    
def test_descent():
    
    print "Descent Rates [3000,10000,20000,25000,30000]meters"
    print descent_rate(3000)
    print descent_rate(10000)
    print descent_rate(20000)
    print descent_rate(25000)
    print descent_rate(30000)


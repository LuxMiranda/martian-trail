import numpy as np
import math
from random import randint
from bettermcd import getDatum


#############################
### Tweak-able parameters ###
#############################

SOLS_PER_WAVE = 759
BACK_FRAMES = 2
DEFAULT_STORM_CHANCE = 3
FORMATION_SMOOTHING = 10
DISSIPATION_SMOOTHING = 60

#################
### Constants ###
#################

SOLS_PER_MARTIAN_YEAR = 669
FIRST_SOL_IN_STORM_DATA = 372
LAST_SOL_IN_STORM_DATA = 668

# Convert number of shipment periods to Martian sols
def wavesToSols(waves):
    return waves*SOLS_PER_WAVE

# Generate the next state given the environment and previous state
def makeState(env, prevState=np.array([])):
    # If prevState was not given, assume initial state
    #if prevState.size == 0:
    return prevState

# Get Martian year time-series of the specified scenario
def getScenario(scenario, lat, lon):
    # Initialize time-series to empty lists
    SOLAR_FLUX, AIR_DENSITY, WIND_SPEED = [],[],[]

    # Fetch data for each sol, with an extra day of the following year
    # tacked on for interpolation purposes
    for sol in range(SOLS_PER_MARTIAN_YEAR+1):
        for hour in range(24):
            scen = scenario
            if scenario == 'dust' and (sol < FIRST_SOL_IN_STORM_DATA or sol > LAST_SOL_IN_STORM_DATA):
                scen = 'climatology'
            T, D, W, S = getDatum(lat=lat,lon=lon,sol=sol,local_time=hour,scenario=scen)
            SOLAR_FLUX.append(S)
            AIR_DENSITY.append(D)
            WIND_SPEED.append(W)

    # Smooth transition data if the scenario is dust-storm
    if scenario == 'dust':
        SOLAR_FLUX  = smooth(SOLAR_FLUX)
        AIR_DENSITY = smooth(AIR_DENSITY)
        WIND_SPEED  = smooth(WIND_SPEED)
 
    
    # Chop off the extra day and return
    return SOLAR_FLUX[:-1], AIR_DENSITY[:-1], WIND_SPEED[:-1]

# Probabilistically generate a new environment of the given length
def generateEnvironment(num_sols=10*SOLS_PER_WAVE, start_sol=0, lat=0, lon=0):
    # Initialize time-series to empty lists
    SOLAR_FLUX, AIR_DENSITY, WIND_SPEED = [],[],[]

    # Keep track of whether or not the previous year was a storm year
    prevYearStorm = False

    # Calculate how many years the environment should encompass
    minSols = num_sols + start_sol
    years = math.ceil(float(minSols) / float(SOLS_PER_MARTIAN_YEAR))
            
    Sdust, Adust, Wdust = getScenario('dust', lat, lon)
    Sclim, Aclim, Wclim = getScenario('climatology', lat, lon)

    # Append a new yearly timeseries for every year
    for _ in range(0,years):
        # Dust storm if you roll a 1!
        if randint(1,DEFAULT_STORM_CHANCE) == 1 and not prevYearStorm:
            prevYearStorm = True
            SOLAR_FLUX  += Sdust
            AIR_DENSITY += Adust
            WIND_SPEED  += Wdust
        else:
            prevYearStorm = False
            SOLAR_FLUX  += Sclim
            AIR_DENSITY += Aclim
            WIND_SPEED  += Wclim

    # Start time is the starting sol times 24 hours
    start = 24*start_sol
    # Return the time-series with the appropriate start time
    return SOLAR_FLUX[start:], AIR_DENSITY[start:], WIND_SPEED[start:]

# Generate the environment and initial state
def generateSim(num_waves=10, lat=0, lon=0):
    sols  = wavesToSols(num_waves) + wavesToSols(BACK_FRAMES)
    env   = generateEnvironment(sols, lat, lon)
    state = makeState(env)
    return state, env

# Interpolate a series over the given interval.
def interpolate(series, START_HOUR, END_HOUR, SMOOTHING_RANGE):
    # Woe to ye who enter these arcane depths.
    # The idea is to slowly incorporate an increasing amount of the
    # terminal data-point into the current data-point over the course 
    # of the range. After every 24 hours, the hours count is reset and 
    # factor by which the terminal data-point is being incorporated increments.
    
    factor = float(1.0 / SMOOTHING_RANGE)
    diff   = factor
    hour   = 0 
    for t in range(START_HOUR, END_HOUR+1):
        hour += 1
        if hour == 24:
            hour = 0
            factor += diff
        series[t] = (1.0-factor)*series[t] + factor*series[END_HOUR+hour]
    return series

def smooth(series):
    # Interpolate the storm's formation.
    # Dust storm begins on FIRST_SOL_IN_STORM_DATA, times 24 hours
    endForm   = 24*FIRST_SOL_IN_STORM_DATA
    startForm = 24*(FIRST_SOL_IN_STORM_DATA-FORMATION_SMOOTHING)
    series = interpolate(series, startForm, endForm, FORMATION_SMOOTHING)

    # Interpolate the storm's dissipation.
    # Dust storm ends on LAST_SOL_IN_STORM_DATA+1, times 24 hours
    endDis   = 24*(LAST_SOL_IN_STORM_DATA+1)
    startDis = 24*(LAST_SOL_IN_STORM_DATA+1-DISSIPATION_SMOOTHING)
    series = interpolate(series, startDis, endDis, DISSIPATION_SMOOTHING)

    return series

import matplotlib.pyplot as plt

state, (S, A, W) = generateSim()
plt.plot(S)
plt.show()

import numpy as np
import math
from random import randint
from bettermcd import getDatum
from pickle_n_parse import getScenario

#################
### Constants ###
#################

SOLS_PER_MARTIAN_YEAR = 669

#############################
### Tweak-able parameters ###
#############################

SOLS_PER_WAVE = 759
BACK_FRAMES = 2
DEFAULT_STORM_CHANCE = 3

# Convert number of shipment periods to Martian sols
def wavesToSols(waves):
    return waves*SOLS_PER_WAVE

# Generate the next state given the environment and previous state
def makeState(env, prevState=np.array([])):
    # If prevState was not given, assume initial state
    #if prevState.size == 0:
    return prevState

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
    env   = generateEnvironment(num_sols=sols, lat=lat, lon=lon)
    state = makeState(env)
    return state, env

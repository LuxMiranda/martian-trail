import numpy as np
import math
from random import randint
from bettermcd import getDatum

SOLS_PER_WAVE = 759
BACK_FRAMES = 2
DEFAULT_STORM_CHANCE = 3
SOLS_PER_MARTIAN_YEAR = 669

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

    for sol in range(SOLS_PER_MARTIAN_YEAR):
        for hour in range(24):
            T, D, W, S = getDatum(lat=lat,lon=lon,sol=sol,local_time=hour,scenario=scenario)
            SOLAR_FLUX.append(S)
            AIR_DENSITY.append(D)
            WIND_SPEED.append(W)
    return SOLAR_FLUX, AIR_DENSITY, WIND_SPEED

# Probabilistically generate a new environment of the given length
def generateEnvironment(num_sols=10*SOLS_PER_WAVE, start_sol=0, storm_chance=DEFAULT_STORM_CHANCE, lat=0, lon=0):
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
        if randint(1,storm_chance) == 1 and not prevYearStorm:
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
def generateSim(num_waves, lat, lon):
    sols  = wavesToSols(num_wave) + wavesToSols(BACK_FRAMES)
    env   = generateEnvironment(sols, lat, lon)
    state = makeState(env)
    return state, env


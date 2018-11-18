import numpy as np
import math
from random import randint

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
    if prevState.size == 0:
        continue
    
    return prevState
    

# Probabilistically generate a new environment of the given length
def generateEnvironment(num_sols=10*SOLS_PER_WAVE, start_sol=0, storm_chance=DEFAULT_STORM_CHANCE):
    # Initialize time-series to empty lists
    SOLAR_FLUX, AIR_DENSITY, WIND_SPEED = [],[],[]

    # Keep track of whether or not the previous year was a storm year
    prevYearStorm = False

    # Calculate how many years the environment should encompass
    minSols = wavesToSols(num_waves) + start_sol
    years = math.ceil(float(minSols) / float(SOLS_PER_MARTIAN_YEAR))

    # Append a new yearly timeseries for every year
    for _ in range(0,years):
        # Initialize new series to append
        S, A, W = [],[],[]

        # Dust storm if you roll a 1!
        if randint(1,storm_chance) == 1 and not prevYearStorm:
            prevYearStorm = True
            S, A, W = getScenario('dust')
        else:
            prevYearStorm = False
            S, A, W = getScenario('climatology')
        SOLAR_FLUX  += S
        AIR_DENSITY += A
        WIND_SPEED  += W

    # Start time is the starting sol times 24 hours
    start = 24*start_sol
    # Return the time-series with the appropriate start time
    return SOLAR_FLUX[start:], AIR_DENSITY[start:], WIND_SPEED[start:]




# Generate the environment and initial state
def generateSim(num_waves):
    sols  = wavesToSols(num_wave) + wavesToSols(BACK_FRAMES)
    env   = generateEnvironment(sols)
    state = makeState(env)
    return state, env


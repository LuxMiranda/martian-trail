import numpy as np
import math

from random import randint
from bettermcd import getDatum
from pickle_n_parse import getScenario

from params import (PV_EFFICIENCY, TURBINE_EFFICIENCY, WINDMILL_SURFACE_AREA,
        HOURS_PER_WAVE, SOLS_PER_WAVE, SOLS_PER_MARTIAN_YEAR, EXTRA_YEARS,
        DEFAULT_STORM_CHANCE, SHIPMENT_MASS, NUM_WAVES, BUCKETS, DEATH_REWARD,
        STORM_PROB, NONSTORM_PROB, DENA_LAT, DENA_LON)

## Constants ##

# List of all possible actions
ACTION_SET = getActionSet()

SOLAR_DUST, AIR_DENSITY_DUST, WIND_DUST = getScenario('dust', DENA_LAT, DENA_LON)
SOLAR_CLIM, AIR_DENSITY_CLIM, WIND_CLIM = getScenario('climatology', DENA_LAT, DENA_LON)
###############

# Get a solar output timepoint from the state and the current flux
def solarOutput(state, flux):
    return PV_EFFICIENCY*flux*state['PV_area']

# Get wind power output timepoint from the state and current density/windspeed
def windOutput(state, density, windspeed):
    return 0.5*density*TURBINE_EFFICIENCY*WINDMILL_SURFACE_AREA*(windspeed**3)*state['num_turbines']

# Add the shipment contents to the state, but don't accumulate anything yet
def addShipment(state, shipment):
    transientState = state.copy()
    transientState['PV-area']          += shipment['PV-area'] 
    transientState['num-turbines']     += shipment['num-turbines'] 
    transientState['population']       += shipment['population'] 
    transientState['battery-capacity'] += shipment['battery-capacity'] 
    transientState['mass']             += shipment['mass'] 
    return transientState

# Propagate the power generation timeseries
# with the new shipment in the environment 
def evaluateShipment(transientState, env):
    # Calculate start and end points
    currentHour = transientState['current-sol']*24
    endHour     = currentHour + HOURS_PER_WAVE

    # Initialize timeseries
    solarPower,windPower = [],[]

    # Unpack environment
    solarFlux, airDensity, windSpeed = env

    # Propagate!
    for hour in range(currentHour, endHour):
        solarPower.append(solarOutput(transientState, solarFlux[hour]))
        windPower.append(windOutput(transientState, airDensity[hour], windSpeed[hour]))

    # Return the timeseries
    return solarPower, windPower

# Reconstruct the full internal state from the compressed table state
def reconstruct(state):
    # TODO
    reconstructed = state.copy()
    reconstructed['current-sol'] += SOLS_PER_WAVE
    return reconstructed

# Ship a configuration and evaluate its performance
def ship(shipment, state, env):
    # Reconstruct the full internal state from the compressed table state
    reconstructedState = reconstruct(state)
    # Add the new shipment to the internal state
    internalState      = addShipment(reconstructedState, shipment) 
    # Calculate the reward of this new state
    reward             = getReward(internalState)
    # Recompress the new state and return
    newState           = compress(internalState)
    return newState, reward

# Convert number of shipment periods to Martian sols
def wavesToSols(waves):
    return waves*SOLS_PER_WAVE

# Generate the initial state
def initialState():
    return { 'PV-area'          : 0.0   ,
             'num-turbines'     : 0     ,
             'battery-capacity' : 0.0   ,
             'population'       : 0     ,
             'storm-since-last' : False ,
             'mass'             : 0     ,
             'current-sol'      : 0     }

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
    sols  = wavesToSols(num_waves) + wavesToSols(EXTRA_YEARS)
    env   = generateEnvironment(num_sols=sols, lat=lat, lon=lon)
    state = initialState()
    return state, env

# Generate the list of all possible actions
def getActionSet():
    # Beautiful list comprehension of all permutations
    return [ {'pop'   : p ,
              'solar' : s ,
              'wind'  : w ,
              'bat'   : b ,
              't'     : t }
              for p in BUCKETS
              for s in BUCKETS
              for w in BUCKETS
              for b in BUCKETS
              for t in range(NUM_WAVES)
              if (p + s + w + b) == 1.0 ]

# Return a list of (s',a,r) where:
# s' is a possible next state
# a  is the action taken to get to s'
# r  is the reward for taking action a
def getNextStates(state):
    # If all of our friends are dead, we get nothing
    if state['pop'] <= 0:
        return []
    # Otherwise, use every possible action to get the list of all possible states
    return [ takeAction(state, a) for a in ACTION_SET ]

# Given an action of (s',a,r) where:
# s' is the new state
# a  is the given action that was used to get to s'
# r  is the reward for taking action a
def takeAction(state, a):
    newState = updateState(state, a)
    return (newState, a, getReward(newState))

# Determine if a death occurs in the given (reconstructed) state
# in either scenario
def deathOccurs(state):
    # Calculate the minimum load for survival
    minLoad = state['pop']*MIN_LOAD_PER_PERSON
    # For every hour in the appropriate range
    for h in getHourRange(state):
        # Return true if the load is below minimum
        dustAvail = availablePower(h, state, 'dust')
        climAvail = availablePower(h, state, 'clim')
        if dustAvaiil < minLoad or climAvail < minLoad:
            return True
    # Otherwise
    return False

def intermediateReward(state, yearType):
    reward = 0
    # For every hour in the appropriate range
    for h in getHourRange(state)
        # Compute the hourly reward
        reward += hourlyReward(h, state, yearType)
    # Return the summation
    return reward

# The expected reward of the given
# state in both dust and non-dust scenarios
def expectedReward(state):
    return STORM_PROB*intermediateReward(state, 'dust')
        + NONSTORM_PROB*intermediateReward(state, 'clim')

# Calculate the reward for a terminal state
def terminalReward(state):
    if deathOccurs(state):
        return DEATH_REWARD
    else:
        return TERMINAL_SUCCESS_REWARD

# Calculate the reward given a new state
def getReward(tableState):
    state = reconstruct(tableState)
    if isTerminal(state):
        return terminalReward(state)
    else:
        return expectedReward(state)

# Perform an action and get the updated state
def updateState(currentState, a):
    # Copy the state because references are devil spawn amirite
    newState = currentState.copy()
    # Update each ratio!
    newState['pop']   = updateRatio('pop',   currentState, a)
    newState['solar'] = updateRatio('solar', currentState, a)
    newState['wind']  = updateRatio('wind',  currentState, a)
    newState['bat']   = updateRatio('bat',   currentState, a)
    # Increment the timestep
    newState['t'] += 1
    return newState

# Calculate the new ratio for a state value given the
# value, current state, and action (shipment)
def updateRatio(value, currentState, a):
    # Current mass is simply the current timestep * shipment mass
    currentMass = currentState['t']*SHIPMENT_MASS
    # Recalculate the ratio given the new ratio and shipment mass
    return ((currentState[value]*currentMass)+(a[value]*SHIPMENT_MASS))/(currentMass + SHIPMENT_MASS)

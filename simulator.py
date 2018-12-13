import numpy as np
import math

from random import randint
from bettermcd import getDatum
from pickle_n_parse import getScenario

from params import *

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

## Constants ##

# List of all possible actions
ACTION_SET = getActionSet()

SOLAR_FLUX_DUST, AIR_DENSITY_DUST, WIND_DUST = getScenario('dust', DENA_LAT, DENA_LON)
SOLAR_FLUX_CLIM, AIR_DENSITY_CLIM, WIND_CLIM = getScenario('climatology', DENA_LAT, DENA_LON)

AVAIL_POWER = {}

###############

# Accessor functions for the climate timeseries
def solarFlux(h, yearType):
    if yearType == 'clim':
        return SOLAR_FLUX_CLIM[h]
    elif yearType == 'dust':
        return SOLAR_FLUX_DUST[h]
    else:
        raise Exception("Invalid year type!")

def airDensity(h, yearType):
    if yearType == 'clim':
        return AIR_DENSITY_CLIM[h]
    elif yearType == 'dust':
        return AIR_DENSITY_DUST[h]
    else:
        raise Exception("Invalid year type!")

def windSpeed(h, yearType):
    if yearType == 'clim':
        return WIND_CLIM[h]
    elif yearType == 'dust':
        return WIND_DUST[h]
    else:
        raise Exception("Invalid year type!")


# Get a solar output timepoint from the state and the current flux (Joules)
def solarOutput(state, flux):
    return PV_EFFICIENCY*flux*state['PV_area']*EARTH_SECONDS_IN_A_MARS_HOUR

# Get wind power output timepoint from the state and current density/windspeed (Joules)
def windOutput(state, density, windspeed):
    return 0.5*density*TURBINE_EFFICIENCY*WINDMILL_SURFACE_AREA*(windspeed**3)*state['num_turbines']*EARTH_SECONDS_IN_A_MARS_HOUR

# Add the shipment contents to the state, but don't accumulate anything yet
def addShipment(state, shipment):
    transientState = state.copy()
    transientState['PV_area']          += shipment['PV_area'] 
    transientState['num_turbines']     += shipment['num_turbines'] 
    transientState['population']       += shipment['population'] 
    transientState['battery_capacity'] += shipment['battery_capacity'] 
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

# Generate the initial table state
def blankTableState():
    return { 'pop'    : 0.0  ,
             'solar'  : 0.0  ,
             'wind'   : 0.0  ,
             'bat'    : 0.0  ,
             'season' : 0    ,
             'storm'  : False,
             't'      : 0    }

# Generate a test table state
def testTableState():
    return { 'pop'    : 0.1 ,
             'solar'  : 0.3 ,
             'wind'   : 0.3 ,
             'bat'    : 0.3 ,
             'season' : 3   ,
             't'      : 1   }


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

# Return a list of (s',a,r) where:
# s' is a possible next state
# a  is the action taken to get to s'
# r  is the reward for taking action a
def getNextStates(state):
    # Use every possible action to get the list of all possible states
    return [ takeAction(state, a) for a in ACTION_SET if a['t'] > state['t'] ]

# Given an action return (s',a,r) where:
# s' is the new state
# a  is the given action that was used to get to s'
# r  is the reward for taking action a
def takeAction(state, a):
    newState = updateState(state, a)
    return (newState, a, getReward(newState))

# Determine if a death occurs in the given (reconstructed) state
# in the given scenario
def deathOccurs(state, yearType):
    # Calculate the minimum load for survival
    minLoad = state['population']*MIN_HOURLY_LOAD_PER_PERSON
    # Get the available power timeseries
    power = availablePower(state, yearType)
    # Iterate through the timeseries
    for p in power:
        # Return true if the load falls below the minimum
        if p < minLoad:
            return True
    return False

# Memoize the power generation timeseries
def availablePower(state, yearType):
    global AVAIL_POWER
    key = str(state)

    if key not in AVAIL_POWER:
        AVAIL_POWER[key] = {}
        AVAIL_POWER[key][yearType] = _availablePower(state, yearType)

    if yearType not in AVAIL_POWER[key]:
        AVAIL_POWER[key][yearType] = _availablePower(state, yearType)
    
    return AVAIL_POWER[key][yearType]

# Generate the available power timeseries given a yeartype.
# Implements a simple battery policy of charging batteries
# during energy surplus and discharging them during energy deficit.
# TODO break down this monster function
def _availablePower(state, yearType):
    # Set battery level to 0
    batLevel = 0
    availablePower = []
    hourlyLoadTarget = MAX_HOURLY_LOAD_PER_PERSON*state['population']
    # Begin simulating!
    for h in getHourRange(state):
        # Generate power
        s = solarOutput(state, solarFlux(h, yearType))
        w = windOutput(state, airDensity(h, yearType), windSpeed(h, yearType))
        output = s + w
        # If we generated more than neccesarry, try charging batteries
        if output > hourlyLoadTarget:
            batLevel += output - hourlyLoadTarget
            excess = 0
            # If batteries fully charge, keep them full and keep track of the excess
            if batLevel > state['battery_capacity']:
                excess   = batLevel - state['battery_capacity']
                batLevel = state['battery_capacity']
            availablePower.append(output + excess) 
        # If we precisely meet the target, do nothing with batteries
        elif output == hourlyLoadTarget:
            availablePower.append(output)
        # If the output is less than we need, try discharging batteries
        elif output < hourlyLoadTarget:
            # If output + batLevel is less than or as much as we need, fully discharge
            if output + batLevel <= hourlyLoadTarget:
                availablePower.append(output + batLevel)
                batLevel = 0
            # Otherwise, only discharge as much as we need to meet the target
            elif output + batLevel > hourlyLoadTarget:
                difference = hourlyLoadTarget - output
                availablePower.append(output + difference)
                batLevel -= difference
    return availablePower

# Generate a list of each hour in a mission. If
# starting_hours_only is True, only the first hour of each day is included.
# Special logic is used to handle going beyond the start of a new year.
def getHourRange(state, starting_hours_only=False):
    # Compute starting day
    startingDay = int((state['season']/NUM_SEASONS)*SOLS_PER_MARTIAN_YEAR)
    # Modulo is used to avoid indexing out of bounds
    if starting_hours_only:
        return [ (day % SOLS_PER_MARTIAN_YEAR)*24
                 for day in range(startingDay, startingDay+SOLS_PER_WAVE) ]
    else:
        return [ (hour % (SOLS_PER_MARTIAN_YEAR*24))
                 for hour in range(startingDay*24, ((startingDay+SOLS_PER_WAVE)*24)) ]

# Compute the daily reward given:
# h          : starting hour
# availPower : available power timeseries
# load       : the maximal load
def dailyReward(h, availPower, load):
    totalDayPower = sum(availPower[h:h+24]) # TODO confirm correct indexing
    if totalDayPower < load:
        return 0
    elif totalDayPower == load:
        # Return the inverse square of the smallest non-zero difference
        return INTERNAL_POWER_DIFF**(-2.0)
    elif totalDayPower > load:
        return (totalDayPower - load)**(-2.0)


# Determine the intermediate reward of a given state with
# the given yeartype 'clim' or 'dust'
def intermediateReward(state, yearType):
    if deathOccurs(state, yearType):
        return DEATH_REWARD

    reward  = 0
    load = state['population']*MAX_DAILY_LOAD_PER_PERSON

    # Fetch the available power timeseries
    availPower = availablePower(state, yearType)

    # For every hour in the appropriate range
    for h in getHourRange(state, starting_hours_only=True):
        # Compute the daily reward
        reward += dailyReward(h, availPower, load)
    # Return the summation
    return reward


# The expected reward of the given
# state in both dust and non-dust scenarios
def expectedReward(state):
    return STORM_PROB*intermediateReward(state, 'dust') + NONSTORM_PROB*intermediateReward(state, 'clim')

# Calculate the reward for a terminal state
def terminalReward(state):
    if deathOccurs(state, 'clim') or deathOccurs(state, 'dust'):
        return DEATH_REWARD
    else:
        return TERMINAL_SUCCESS_REWARD

# Reconstruct a tableState of ratios into a more useful
# internal state of mass and actual values
def reconstruct(tableState):
    currentMass = tableState['t']*SHIPMENT_MASS
    return {'population'       : (tableState['pop']*currentMass)/(HUMAN_MASS),
            'PV_area'          : (tableState['solar']*currentMass)/(PV_MASS_PER_M2),
            'num_turbines'     : (tableState['wind']*currentMass)/(TURBINE_MASS),
            'battery_capacity' : (tableState['bat']*currentMass)*BATTERY_JOULES_PER_KG,
            'season'           : tableState['season'],
            'mass'             : currentMass,
            't'                : tableState['t'],
            'storm'            : tableState['storm']}


def rollForStorm(state):
    if state['storm']:
        return False
    return (np.random.randint(0, DEFAULT_STORM_CHANCE) == 0)

# Check to see if the given state is a terminal one
def isTerminal(state):
    return state['t'] == NUM_WAVES - 1

# Calculate the reward given a new state
def getReward(tableState):
    state = reconstruct(tableState)
    if isTerminal(state):
        return terminalReward(state)
    elif state['storm']:
        return intermediateReward(state, 'dust')
    else:
        return intermediateReward(state, 'clim')


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

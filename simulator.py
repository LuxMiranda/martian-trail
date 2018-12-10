import numpy as np
import math
from random import randint
from bettermcd import getDatum
from pickle_n_parse import getScenario

#############################
### Tweak-able parameters ###
#############################

SOLS_PER_WAVE = 759
BACK_FRAMES = 2
DEFAULT_STORM_CHANCE = 3

PV_EFFICIENCY = 0.3
TURBINE_EFFICIENCY = 0.9
WINDMILL_SURFACE_AREA = 1.0

#################
### Constants ###
#################

SOLS_PER_MARTIAN_YEAR = 669
HOURS_PER_WAVE = SOLS_PER_WAVE*24

# Get a solar output timepoint from the state and the current flux
def solarOutput(state, flux):
    return PV_EFFICIENCY*flux*state['PV-area']

# Get wind power output timepoint from the state and current density/windspeed
def windOutput(state, density, windspeed):
    return 0.5*density*TURBINE_EFFICIENCY*WINDMILL_SURFACE_AREA*(windspeed**3)*state['num-turbines']

# Add the shipment contents to the state, but don't accumulate anything yet
def addShipment(state, shipment):
    transientState = state.copy()
    transientState['PV-area']      += shipment['PV-area']
    transientState['num-turbines'] += shipment['num-turbines']
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

# Update the transient state with appropriate accumulations
# from the power generation timeseries
def accumulatePowerState(transientState, powerTimeseries):
    # TODO
    newState = transientState.copy()
    newState['current-sol'] += SOLS_PER_WAVE
    return newState

# Compute the timestep reward
def timestepReward(state, newState, powerTimeseries):
    # TODO
    return 0.0

# Ship a configuration and evaluate its performance
def ship(shipment, state, env):
    transientState = addShipment(state, shipment)
    powerTimeseries = evaluateShipment(transientState, env)
    newState = accumulatePowerState(transientState, powerTimeseries)
    reward = timestepReward(state, newState, powerTimeseries)
    return newState, reward, powerTimeseries

# Convert number of shipment periods to Martian sols
def wavesToSols(waves):
    return waves*SOLS_PER_WAVE

# Generate the initial state
def initialState():
    return { 'PV-area'      : 0.0,
             'num-turbines' : 0  ,
             'current-sol'  : 0  }

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
    for _ in range(0,int(years)):
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
    state = initialState()
    return state, env

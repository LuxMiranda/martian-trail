from bettermcd import getDatum
import pickle

from params import (FIRST_SOL_IN_STORM_DATA, LAST_SOL_IN_STORM_DATA,
        FORMATION_SMOOTHING, DISSIPATION_SMOOTHING)

def getPickleFilename(scenario, lat, lon):
    return './pickle-jar/' + scenario + '_' + str(lat) + '_' + str(lon) + '.pickle'

def getScenario(scenario, lat, lon):
    return pickle.load(open(getPickleFilename(scenario, lat, lon), 'rb'))

# Pickle Martian year time-series of the specified scenario
def pickleScenario(scenario, lat, lon):
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
    
    # Chop off the extra day and pickle
    filename = getPickleFilename(scenario, lat, lon)
    with open(filename, 'wb') as f:
        pickle.dump([SOLAR_FLUX[:-1], AIR_DENSITY[:-1], WIND_SPEED[:-1]],f)


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


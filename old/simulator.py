import dataparser

# Fetch all data for the given climate synthetic scenario
def getScenario(scenario):
    # Initialize time-series to empty lists
    SOLAR_FLUX, AIR_DENSITY, WIND_SPEED = [],[],[]
    # Parse every sol file and add to the lists
    for sol in range(1, 670):
        with open('data/' + scenario + '/' + str(sol).zfill(3) + '.txt') as f:
            # Strip each line of whitespace and pass it to the parser
            S,A,W = parse([x.strip() for x in f.readlines()])
            # Concatenate the new components to each time-series
            SOLAR_FLUX  += S
            AIR_DENSITY += A
            WIND_SPEED  += W

    # Smooth transition data if the scenario is dust-storm
    if scenario == 'dust-storm':
        SOLAR_FLUX  = smooth(SOLAR_FLUX)
        AIR_DENSITY = smooth(AIR_DENSITY)
        WIND_SPEED  = smooth(WIND_SPEED)
        
    # Return the time-series
    return SOLAR_FLUX, AIR_DENSITY, WIND_SPEED

# Generate a muli-year environment timeseries with probabilistically determined dust storms
def getEnvironment(num_years=10, start_sol=0, storm_chance=3):
    from random import randint
    # Initialize time-series to empty lists
    SOLAR_FLUX, AIR_DENSITY, WIND_SPEED = [],[],[]

    # Keep track of whether or not the previous year was a storm year
    prevYearStorm = False

    # Append a new yearly timeseries for every year
    for _ in range(0,num_years):
        # Initialize new series to append
        S, A, W = [],[],[]

        # Dust storm if you roll a 1!
        if randint(1,storm_chance) == 1 and not prevYearStorm:
            prevYearStorm = True
            S, A, W = getScenario('dust-storm')
        else:
            prevYearStorm = False
            S, A, W = getScenario('avg-climate')
        SOLAR_FLUX  += S
        AIR_DENSITY += A
        WIND_SPEED  += W

    # Start time is the starting sol times 24 hours
    start = 24*start_sol
    # Return the time-series with the appropriate start time
    return SOLAR_FLUX[start:], AIR_DENSITY[start:], WIND_SPEED[start:]



# Plot the solar flux at the Dena site versus the two different scenarios
def sunnyPlot():
    SOLAR_FLUX_DUST, AIR_DENSITY_DUST, WIND_SPEED_DUST = getScenario('dust-storm')
    SOLAR_FLUX_NORM, AIR_DENSITY_NORM, WIND_SPEED_NORM = getScenario('avg-climate')
    import matplotlib.pyplot as plt
    plt.title('How sunny is the Dena skylight? (-6.084°N 239.061°E)')
    plt.xlabel('Hours into the Martian year')
    plt.ylabel('Maximum solar flux to surface ($W/m^2$)')
    plt.plot(SOLAR_FLUX_NORM, label='Average stormless year')
    plt.plot(SOLAR_FLUX_DUST, label='Average year with global dust storm')
    plt.legend()
    plt.grid()
    plt.show()

import matplotlib.pyplot as plt

# Extract the value from a sol file line.
# Returns a float.
def extractVal(line):
    return tuple(map(eval, line.split('    ')))[1]

# Parse the contents of a sol file into time-series components
def parse(solFile):
    # Solar data is on lines 10 through 34
    SOLAR_FLUX  = list(map(extractVal, solFile[10:35]))
    # Density data is on lines 45 through 69
    AIR_DENSITY = list(map(extractVal, solFile[45:70]))
    # Horizontal wind speed  data is on line 80 and onwards
    WIND_SPEED  = list(map(extractVal, solFile[80:]))
    return SOLAR_FLUX, AIR_DENSITY, WIND_SPEED


# Fetch all data for the average climate synthetic scenario
def getScenario():
    # Initialize time-series to empty lists
    SOLAR_FLUX, AIR_DENSITY, WIND_SPEED, MAX_FLUX = [],[],[],[]
    # Parse every sol file and add to the lists
    for sol in range(1, 500):
        with open('data/avg-climate/' + str(sol).zfill(3) + '.txt') as f:
            # Strip each line of whitespace and pass it to the parser
            S,A,W = parse([x.strip() for x in f.readlines()])
            # Concatenate the new components to each time-series
            SOLAR_FLUX  += S
            AIR_DENSITY += A
            WIND_SPEED  += W
            MAX_FLUX.append(max(S))

    # Return the time-series
    return SOLAR_FLUX, AIR_DENSITY, WIND_SPEED, MAX_FLUX

SOLAR_FLUX, AIR_DENSITY, WIND_SPEED, MAX_FLUX = getScenario()

plt.title('How sunny is Dena?')
plt.xlabel('Martian Sol')
plt.ylabel('Maximum solar flux to surface ($W/m^2$)')
plt.plot(MAX_FLUX)
plt.grid()
plt.show()

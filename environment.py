import matplotlib.pyplot as plt

def extractVal(line):
    return tuple(map(eval, line.split('    ')))[1]

def parse(content):
    SOLAR_FLUX, AIR_DENSITY, WIND_SPEED = [],[],[]
    SOLAR_FLUX  += map(extractVal, content[10:35])
    AIR_DENSITY += map(extractVal, content[45:70])
    WIND_SPEED  += map(extractVal, content[80:])
    return SOLAR_FLUX, AIR_DENSITY, WIND_SPEED

SOLAR_FLUX, AIR_DENSITY, WIND_SPEED, MAX_FLUX = [],[],[],[]
for sol in range(1, 500):
    with open('data/avg-climate/' + str(sol).zfill(3) + '.txt') as f:
        lines = f.readlines()
        content = [x.strip() for x in lines]
        S,A,W = parse(content)
        SOLAR_FLUX  += S
        AIR_DENSITY += A
        WIND_SPEED  += W
        MAX_FLUX.append(max(S))

plt.plot(MAX_FLUX,  label='solar flux to surface ($W/m^2$)')
plt.show()

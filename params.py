import numpy as np

#############################
### Tweak-able parameters ###
#############################


# Number of seasons in the state variable
N_SEASONS = 4

# Discount rate for next time step
DISCOUNT = .9

# Mean and Variance to initialize V-Table
V_INIT_MEAN = 100
V_INIT_VAR = 5

# Number of missions
NUM_WAVES           = 10

# Number of sols per mission
# (calculated in accordance with Aldrin cycler)
SOLS_PER_WAVE        = 759

# Extra Martian years to include in the simulation
EXTRA_YEARS          = 2

# Denominator in the annual storm likelihood for
# procedural generation of timeseries
# (e.g., if 3 then every year has a 1/3 chance of storm)
DEFAULT_STORM_CHANCE = 3.0

# Efficiency of the PV systems
PV_EFFICIENCY         = 0.3
# Mass per square meter of PV surface area (kg)
PV_MASS_PER_M2        = 10.0

# Efficiency of the wind turbines
TURBINE_EFFICIENCY    = 0.9
# Surface area per each turbine's windmill
WINDMILL_SURFACE_AREA = 1.0
# Mass of each turbine (kg)
TURBINE_MASS          = 100.0

# Energy density of the batteries (J / kg)
BATTERY_JOULES_PER_KG = 100.0


# Mass of each human (kg)
HUMAN_MASS = 85.0

# Number of days it takes for a global storm to form
FORMATION_SMOOTHING   = 10
# Number of days it takes for a global storm to dissipate
DISSIPATION_SMOOTHING = 60

# Mass of each shipment (in kg)
SHIPMENT_MASS = 100000

# List of possible values for state ratios
BUCKETS = np.arange(0.0,1.1,0.1)

# Negative reward accrued for following below life support levels
DEATH_REWARD = -100

# Large terminal reward for a successful run
TERMINAL_SUCCESS_REWARD = 100

# Smallest difference for internal tracking of power (Joules, I guess)
INTERNAL_POWER_DIFF = 0.1

# Number of seasons to divide the Martian year into for
# possible mission start dates.
NUM_SEASONS = 4

# Maximum loads as functions of the population (joules)
# Based on estimate of 5kW/person
MIN_HOURLY_LOAD_PER_PERSON = 18490000
MIN_DAILY_LOAD_PER_PERSON  = MIN_HOURLY_LOAD_PER_PERSON*24

MAX_HOURLY_LOAD_PER_PERSON = MIN_HOURLY_LOAD_PER_PERSON*3
MAX_DAILY_LOAD_PER_PERSON  = MAX_HOURLY_LOAD_PER_PERSON*24

#################
### Constants ###
#################

# Some astronomical business.
SOLS_PER_MARTIAN_YEAR   = 669
FIRST_SOL_IN_STORM_DATA = 372
LAST_SOL_IN_STORM_DATA  = 668
SOLS_PER_MARTIAN_YEAR   = 669
HOURS_PER_WAVE          = SOLS_PER_WAVE*24

EARTH_SECONDS_IN_A_MARS_HOUR = 3698.96

# Latitude and longitude of the Dena Skylight at Asria Mons
DENA_LAT = 239.061
DENA_LON = -6.084

# Scenario probabilities computed from dust storm chance
STORM_PROB    = 1.0 / DEFAULT_STORM_CHANCE
NONSTORM_PROB = (1.0 - 1.0 / DEFAULT_STORM_CHANCE)

#############################
### Tweak-able parameters ###
#############################

# Number of bins for digitizing state variables
N_BINS = 10

# Number of time steps
N_SHIPMENTS = 10

# Number of seasons in the state variable
N_SEASONS = 4

# Discount rate for next time step
DISCOUNT = .9

# Mean and Variance to initialize V-Table
V_INIT_MEAN = 100
V_INIT_VAR = 5

# Number of sols per mission
# (calculated in accordance with Aldrin cycler)
SOLS_PER_WAVE        = 759

# Extra Martian years to include in the simulation
EXTRA_YEARS          = 2

# Denominator in the annual storm likelihood
# (e.g., if 3 then every year has a 1/3 chance of storm)
DEFAULT_STORM_CHANCE = 3

# Efficiency of the PV systems
PV_EFFICIENCY         = 0.3

# Efficiency of the wind turbines
TURBINE_EFFICIENCY    = 0.9
# Surface area per each turbine's windmill
WINDMILL_SURFACE_AREA = 1.0

# Number of days it takes for a global storm to form
FORMATION_SMOOTHING   = 10
# Number of days it takes for a global storm to dissipate
DISSIPATION_SMOOTHING = 60

#################
### Constants ###
#################

# Some astronomical business.
SOLS_PER_MARTIAN_YEAR   = 669
FIRST_SOL_IN_STORM_DATA = 372
LAST_SOL_IN_STORM_DATA  = 668
SOLS_PER_MARTIAN_YEAR   = 669
HOURS_PER_WAVE          = SOLS_PER_WAVE*24

# Latitude and longitude of the Dena Skylight at Asria Mons
DENA_LAT = 239.061
DENA_LON = -6.084

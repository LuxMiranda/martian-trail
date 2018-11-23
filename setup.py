import bettermcd as bmcd
import pickle_n_parse as pnp

DENA_LAT = 239.061
DENA_LON = -6.084

print("Beginning martian-trail setup...")

if bmcd.test_mcd():
    pnp.pickleScenario('dust', DENA_LAT, DENA_LON)
    pnp.pickleScenario('climatology', DENA_LAT, DENA_LON)

print("Finished!")

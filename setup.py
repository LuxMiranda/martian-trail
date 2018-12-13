import bettermcd as bmcd
import pickle_n_parse as pnp

from params import (DENA_LAT, DENA_LON)

print("Beginning martian-trail setup...")

if bmcd.test_mcd():
    pnp.pickleScenario('dust', DENA_LAT, DENA_LON)
    pnp.pickleScenario('climatology', DENA_LAT, DENA_LON)
    print("Finished!")



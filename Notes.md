Useful variables provided by Mars Climate Database (MCD):
*  Pressure
*  Atmospheric Density
*  Temperature
*  Winds
*  Thermal and solar radiative fluxes
*  Dust column opacity
*  Dust effective radius and dust deposition rate

4 synthetic dust scenarios to bracket reality:
*  Climatology "best guess" - Does NOT incorporate global dust storm
*  Cold; clear skies
*  Warm; dusty skies
*  Severe global dust storm

Can perhaps construct an environment that probabilisticly strings together these different types of years. Can linearly interpolate over some time period if they don't "fit" together nicely.

MCD generally _very_ accurate for our surface needs. See [here](http://www-mars.lmd.jussieu.fr/mars/mcd_training/MCD5.2_Validation.pdf) for details.

"Dena" skylight (-6.084°N 239.061°E) near Arsia Mons is a potentially attractive settlement location due to potentially being a lava tube entrance, proximity to craters for wind turbine utilization, and possible geothermal capability being equatorial (plus lots of sunlight). See [this paper](https://www.lpi.usra.edu/meetings/lpsc2007/pdf/1371.pdf).

Wind turbine power is calculated as ``P=0.5*n*A*p*v*v*v``, where ``P`` is power (W), ``n`` is turbine efficiency, ``A`` is the wind mill surface area perpendicular to the wind (m^2), ``p`` is the air density (kg/m^3), and ``v`` is the wind speed (m/s). See [this paper](https://www.hou.usra.edu/meetings/amazonian2018/pdf/4004.pdf)

Dust storm scenario does not perfectly fit with climatology scenario, so interpolation over 10 days shall be used.

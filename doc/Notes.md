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

Dust storm scenario does not perfectly fit with climatology scenario, so interpolation over 10 days shall be used on the left and 60 days on the right. 

For probabilistic scenarios, a 3-sided die is rolled to determine if the next year in the scenario will contain a dust storm. Additionally, there may not be two years in a row with a global dust storm.

Each shipment period is 759 martian sols

State tensors will be 3D:
    * D1: use last three shipment periods
    * D2: 
        * Divide each shipment period into baker's decameron (11 sols) for a total of 69 baker's decamerons.
        * Also include non-aggregate state variables that persist for the entire shipment period:
            * Load
            * Battery capacity
            * Number of PV systems
            * Number of turbines
    * D3: Each baker's decameron is an array with the aggregated state variables for the week
        * Solar flux (avg)
        * Wind speed (avg)
        * Air density (avg)
        * PV power (sum)
        * Wind power (sum)

On second thought, if we're using a table first instead...
The state of the system can be represented with a simple Markov chain:  

![markov.png](Markov chain with transition probabilities where the states are Martian years)

In this way, we can encode a very small Markov state with perhaps just a few entries:
*  Current year type (binary: storm or no storm)
*  Previous _n_ year types (where _n_ is small; say, _n=2_)
*  The usual suspects:
    *  Load, battery capacity, number of PV systems and turbines
    *  ~~Some kind of encoded information about how well the systems have been doing in the environment~~

State v1:
    * PV area (m2)
    * Number of wind turbines
    * Population/load
    * Battery capacity
    * Was there a dust storm since the last shipment? (boolean)
    * Bucketized Martian date (optional)


State v2:
    * Each state parameter expressed as a ratio related to the total mass
    * Was there a dust storm since the last shipment? (boolean)
    * Bucketized Martian date

Actions are a function of mass and also express ratios to that mass

Reward:
    Terminal: BIG reward for success
              Minus infinity for killing everyone

    Intermediate: 
             Accumulate how well the daily reward is being met with MSE


---

Potential error:
    In computing the intermediate reward, beginning with season 3 in a dust storm year will extend into another dust storm, potentially throwing off reward calculations.

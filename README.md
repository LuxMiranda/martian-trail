# Martian Trail

Use V-Table Reinforcement Learning to plan your next clean energy powered vacation to Mars for you and a thousand of your closest friends!

## Installation and setup

1. Set up your environment with an installation of Python 3. This as designed and tested using Ubuntu. Windows and Mac may be viable choices, but they have not been tested and will be harder to set up the Mars Climate Database with.

2. You'll need access to the full version of the [Mars Climate Database version 5.3](http://www-mars.lmd.jussieu.fr/). Download and extract it to a location of your choice. 

    ``martian-trail`` also utilizes the synthetic dust storm scenario available as an addon from the MCD server as ``strm.tar.gz``, so be sure to get that as well and extract it to the MCD ``data/`` folder. 

    You'll also need to get NetCDF and the MCD python interface working; the installation scripts over at [mcd-python](https://github.com/aymeric-spiga/mcd-python) are most helpful for this. 

    Make sure the ``martian-trail/`` directory has access to the generated ``fmcd.so`` that results from generating the python interface. 

3.  Run ``setup.py``. It will automatically test to see if your MCD installation is up to snuff. If the tests pass, it will begin the pickling process for the primary time-series that ``martian-trail`` needs by default.

## Running

1. Run ``agent.py`` to begin the simulation. The program will output the agent's decisions at each time step. 

2. Tweak the parameters in ``params.py`` to model whatever specifications you want!

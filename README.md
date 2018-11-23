# Martian Trail

Whaddup. Mars and stuff.

## Installation and setup

1.  Firstly, you'll need access to the full version of the [Mars Climate Database version 5.3](http://www-mars.lmd.jussieu.fr/). Download and extract it to a location of your choice. 

   ``martian-trail`` also utilizes the synthetic dust storm scenario available as an addon from the MCD server as ``strm.tar.gz``, so be sure to get that as well and extract it to the MCD ``data/`` folder. 

   You'll also need to get NetCDF and the MCD python interface working; the installation scripts over at [mcd-python](https://github.com/aymeric-spiga/mcd-python) are most helpful for this. 

   Make sure the ``martian-trail/`` directory has access to the generated ``fmcd.so`` that results from generating the python interface. 

2.  Run ``setup.py``. It will automatically test to see if your MCD installation is up to snuff. If the tests pass, it will begin the pickling process for the primary time-series that ``martian-trail`` needs by default.

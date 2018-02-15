# Straggler Simulator

Simulator of a parallized multi-task platform with potential stragglers.

Run simulator using default setting:
```
python simulator.py
```
Import simulator:
```
from simulator import Simulator
sim = Simulator() # using default.conf as configuration file
sim1 = Simulator(filepath) # using the config file from filepath
sim.run() # run simulator
```

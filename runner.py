from __future__ import absolute_import
from __future__ import print_function

import os
import sys
import optparse
import subprocess
import random

import math

# we need to import python modules from the $SUMO_HOME/tools directory
try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary
except ImportError:
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci


def run(interval):
    """execute the TraCI control loop"""
    step = 0
    idVehicle = 1
    vehicles = {}
    nVehicles = 0

    f = open("states_test.txt", "w")
    t = open("traffic_flow_test.txt","w")
    while traci.simulation.getMinExpectedNumber() > 0:
        currentTime = traci.simulation.getCurrentTime()
        traci.simulationStep()      
        if (currentTime % interval) == 0:
            # print("time ", currentTime)
            nVehicles = 0
            for veh_id in traci.vehicle.getIDList():
                speed = traci.vehicle.getSpeed(veh_id)
                print(veh_id," ",speed," ", currentTime)
                x, y = traci.vehicle.getPosition(veh_id)
                lon, lat = traci.simulation.convertGeo(x, y)
                x2, y2 = traci.simulation.convertGeo(lon, lat, fromGeo=True)

                index = idVehicle
                if veh_id not in vehicles:
                    idVehicle += 1
                    vehicles[veh_id] = idVehicle
                    nVehicles += 1
                else:
                    index = vehicles[veh_id]
                f.write(str(index)+":"+str(x2)+":"+str(y2)+"\n")
                # print("id: ",veh_id," pos: ",x2,y2)
                # neighbors = traci.vehicle.getNeighbors(veh_id, 2)
                # print(veh_id,neighbors)
            if nVehicles >= 1:
                t.write(str(currentTime)+" "+str(nVehicles)+"\t")
                f.write("END "+str(currentTime)+" \n")
                
            step += 1    
    f.close()
    t.close()
    sys.stdout.flush()

if __name__ == "__main__":
    
    sumocfg = sys.argv[1]
    tripinfo = sys.argv[2]
    
    seconds = 60
    milisseconds = 1000
    minutes = 10 #number of minutes to extract a graph 
    extractInformation = minutes * seconds * milisseconds

    # this is the normal way of using traci. sumo is started as a
    # subprocess and then the python script connects and runs
    traci.start(["sumo", "-c", sumocfg,
                             "--tripinfo-output", tripinfo])
    run(extractInformation)
    # buldingGraphs()

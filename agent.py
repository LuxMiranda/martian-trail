import simulator as sim
import matplotlib.pyplot as plt
from params import DENA_LAT, DENA_LON

NUM_EPISODES = 1
NUM_WAVES    = 10

def getShipment(state):
    # TODO
    return { 'PV-area' : 10.0, 'num-turbines' : 10 }

def train():
    # Train over NUM_EPISODES
    for i_episode in range(NUM_EPISODES):
        # FIXME Temporary plotting
        windPower = []

        # Probabilistically generate a new environment
        state, env = sim.generateSim(num_waves=NUM_WAVES, lat=DENA_LAT, lon=DENA_LON)

        # Begin sending cargo waves
        for wave in range(NUM_WAVES):
            # Get a shipment configuration by giving the current state to the Q-net 
            shipment = getShipment(state)

            # Ships the configuration and evaluates its performance
            newState, reward, timeseries = sim.ship(shipment, state, env)

            # FIXME Temporary plotting
            S, W = timeseries
            windPower += W

            # Update the Q-net
            # updateQ(newState, reward)

            # Update the current state
            state = newState

        # FIXME Temporary plotting
        plt.plot(windPower)
        plt.xlabel("Hour of Martian Year")
        plt.ylabel("Power output of wind turbines (Watts)")
        plt.show()

if __name__ == '__main__':
    train()

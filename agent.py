import simulator as sim
import matplotlib.pyplot as plt

NUM_EPISODES = 1
NUM_WAVES    = 10

def train():
    # Train over NUM_EPISODES
    for i_episode in range(NUM_EPISODES):
        # Probabilistically generate a new environment
        state, env = sim.generateSim(num_waves=NUM_WAVES)

        # Begin sending cargo waves
        for wave in range(NUM_WAVES):
            # Get a shipment configuration by giving the current state to the Q-net 
            shipment = getShipment(state)

            # Ships the configuration and evaluates its performance
            newState, reward = sim.ship(shipment, state, env)

            # Update the Q-net
            updateQ(newState, reward)

            # Update the current state
            state = newState

state, (S, A, W) = sim.generateSim(num_waves=10, lat=239.061, lon=-6.084)
plt.plot(S)
plt.show()

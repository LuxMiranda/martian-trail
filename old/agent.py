import simulator as sim

NUM_EPISODES = 1
NUM_WAVES    = 10

env = sim.init(NUM_WAVES)

def train():
    # Train over NUM_EPISODES
    for i_episode in range(NUM_EPISODES):
        # Regenerate a new random environment
        state = env.regenerate()

        # Begin sending cargo waves
        for wave in range(NUM_WAVES):
            # Get a shipment configuration by giving the current state to the Q-net 
            shipment = getShipment(state)

            # Ships the configuration and evaluates its performance
            newState, reward = env.ship(shipment)

            # Update the Q-net
            updateQ(newState, reward)

            # Update the current state
            state = newState

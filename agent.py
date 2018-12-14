from __future__ import division, print_function

import simulator as sim
# import matplotlib.pyplot as plt
from params import *
import numpy as np
import pickle

NUM_EPISODES = 100
NUM_WAVES = 10


def initVTable():
    n_bins = len(BUCKETS)
    # Order of axes is shipment, population, solar, wind, battery, season, storm
    v_table = np.random.normal(loc=V_INIT_MEAN, scale=V_INIT_VAR,
                               size=(NUM_WAVES, n_bins, n_bins, n_bins, n_bins, N_SEASONS, 2))
    return v_table


# Updates the v-table slot for state. Returns the change in the value
def updateVAndGetAction(v_table, state, next_states, reward):
    # Unpack state
    t = state["t"]
    pop = np.digitize(state["pop"], BUCKETS, right=True)
    solar = np.digitize(state["solar"], BUCKETS, right=True)
    wind = np.digitize(state["wind"], BUCKETS, right=True)
    bat = np.digitize(state["bat"], BUCKETS, right=True)
    season = state["season"]
    storm = state["storm"]

    # Everyone's dead. Negative terminal reward for this state
    if next_states == []:
        v_table[t][pop][solar][wind][bat][season][storm] = DEATH_REWARD
        return


    max_e_v = -10000
    max_i = -1

    # Collapse all next possible states by the action to get them there so they can be evaluated together
    next_states_collapsed = []
    while len(next_states) > 0:
        # Get the first state from next_states
        cur_state = next_states.pop()

        # Split states into sister_states, which is the cur_state and any siblings, and all the other states.
        sister_states = [s for s in next_states if s[1] == cur_state[1]]
        next_states = [s for s in next_states if s[1] != cur_state[1]]

        # Add cur state back to sister states
        sister_states.append(cur_state)

        # Add the sister states to next_states_collapsed
        next_states_collapsed.append(sister_states)

    # Get the best action and its expected V
    for i in range(len(next_states_collapsed)):
        e_v = 0
        for sister_state in next_states_collapsed[i]:
            # Unpack this sister state
            next_state, next_action, next_reward = sister_state
            n_t = next_state["t"]
            n_pop = np.digitize(next_state["pop"], BUCKETS, right=True)
            n_solar = np.digitize(next_state["solar"], BUCKETS, right=True)
            n_wind = np.digitize(next_state["wind"], BUCKETS, right=True)
            n_bat = np.digitize(next_state["bat"], BUCKETS, right=True)
            n_season = next_state["season"]
            n_storm = 1 if next_state["storm"] else 0

            # Get the v value for the current next state
            next_v = v_table[n_t][n_pop][n_solar][n_wind][n_bat][n_season][n_storm]

            # If we're in a storm, disregard having a storm next.
            if state["storm"]:
                if n_storm:
                    e_v += reward + (DISCOUNT * next_v)

            # Otherwise we aren't in a storm, calculate both
            else:
                if n_storm:
                    e_v += 0.667 * (reward + (DISCOUNT * next_v))
                else:
                    e_v += 0.333 * (reward + (DISCOUNT * next_v))

        # Update best expected value and index of best action if needed.
        if e_v > max_e_v:
            max_e_v = e_v
            max_i = i
    v_table[t][pop][solar][wind][bat][season][storm] = max_e_v
    return next_states_collapsed[max_i][0][1]


def train(v_table):
    # Train over NUM_EPISODES
    for i_episode in range(NUM_EPISODES):
        # Generate a blank initial state
        state = sim.blankTableState()
        reward = 0
        totalReward = 0
        # Begin sending cargo waves
        for wave in range(NUM_WAVES):
            # Get possible next states
            print('Generating next states for state: ' + str(state))
            next_states = sim.getNextStates(state)

            # If there are no next states, that probably means everyone died. Update the v-table with a negative
            # terminal reward and break to a new episode
            shipment = updateVAndGetAction(v_table, state, next_states, reward)
            if next_states == []:
                break

            print('Taking action: ' + str(shipment))
            
            # Ships the configuration
            state = sim.updateState(state, shipment)
            
            # Probabilistically assign either a storm or no storm to the next state
            state['storm'] = sim.rollForStorm(state)

            # Update the reward using the new state
            reward = sim.getReward(state)
            totalReward += reward
            if sim.isTerminal(state):
                t = state["t"]
                pop = np.digitize(state["pop"], BUCKETS, right=True)
                solar = np.digitize(state["solar"], BUCKETS, right=True)
                wind = np.digitize(state["wind"], BUCKETS, right=True)
                bat = np.digitize(state["bat"], BUCKETS, right=True)
                season = state["season"]
                storm = state["storm"]
                v_table[t][pop][solar][wind][bat][season][storm] = TERMINAL_SUCCESS_REWARD

        print('Finished episode ' + str(i_episode) + ' with total reward ' + str(totalReward) + '!')
        with open("rewards.txt", "a") as f:
            f.write(str(totalReward) + '\n')

dummy_data = [
    (
        {
            "t": 4,
            "pop": .2,
            "solar": .2,
            "wind": .1,
            "bat": .5,
            "season": 2,
            "storm": False
        },
        {
            "pop": .5,
            "solar": 0.0,
            "wind": .3,
            "bat": .2,
        },
        -300,
    ),
    (
        {
            "t": 5,
            "pop": 1.0,
            "solar": 0.0,
            "wind": 0.0,
            "bat": 0.0,
            "season": 3,
            "storm": True
        },
        {
            "pop": .5,
            "solar": 0.0,
            "wind": .3,
            "bat": .2,
        },
        150
    ),
    (
        {
            "t": 4,
            "pop": .2,
            "solar": .2,
            "wind": .1,
            "bat": .5,
            "season": 2,
            "storm": False
        },
        {
            "pop": .3,
            "solar": .2,
            "wind": .3,
            "bat": .2,
        },
        200
    ),
    (
        {
            "t": 4,
            "pop": .2,
            "solar": .2,
            "wind": .1,
            "bat": .5,
            "season": 2,
            "storm": True
        },
        {
            "pop": .3,
            "solar": .2,
            "wind": .3,
            "bat": .2,
        },
        150
    )
]


def save(obj, fpath):
    with open(fpath, "wb") as f:
        pickle.dump(obj, f)


def load(fpath):
    with open(fpath, "rb") as f:
        return pickle.load(f)


if __name__ == '__main__':
    v_table = None

    # Try to load the v-table
    try:
        v_table = load(V_TABLE_PATH)
        print("Loaded v-table")

    # Initialize a new V table if it couldn't be loaded
    except IOError:
        v_table = initVTable()
        print("Created new v-table")

    #action = updateVAndGetAction(v_table, dummy_data[0][0], 150, dummy_data)
    train(v_table)
    save(v_table, V_TABLE_PATH)

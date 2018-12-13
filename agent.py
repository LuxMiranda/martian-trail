from __future__ import division

import simulator as sim
# import matplotlib.pyplot as plt
from params import DENA_LAT, DENA_LON, V_INIT_MEAN, V_INIT_VAR, N_BINS, N_SEASONS, N_SHIPMENTS, DISCOUNT
import numpy as np
import pickle

NUM_EPISODES = 1
NUM_WAVES = 10


def initVTable():
    # Order of axes is shipment, population, solar, wind, battery, season, storm
    v_table = np.random.normal(loc=V_INIT_MEAN, scale=V_INIT_VAR,
                               size=(N_SHIPMENTS, N_BINS+1, N_BINS+1, N_BINS+1, N_BINS+1, N_SEASONS, 2))
    return v_table


# Updates the v-table slot for state. Returns the change in the value
def updateVAndGetAction(v_table, state, reward, next_states):
    # Unpack state
    t = state["t"]
    pop = int(state["pop"] * N_BINS)
    solar = int(state["solar"] * N_BINS)
    wind = int(state["wind"] * N_BINS)
    bat = int(state["bat"] * N_BINS)
    season = state["season"]
    storm = state["storm"]

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
            n_pop = int(next_state["pop"] * N_BINS)
            n_solar = int(next_state["solar"] * N_BINS)
            n_wind = int(next_state["wind"] * N_BINS)
            n_bat = int(next_state["bat"] * N_BINS)
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
        # Probabilistically generate a new environment
        state, env = sim.generateSim(num_waves=NUM_WAVES, lat=DENA_LAT, lon=DENA_LON)
        reward = 0
        # Begin sending cargo waves
        for wave in range(NUM_WAVES):
            # Get possible next states
            next_states = sim.getNextStates()
            shipment = updateVAndGetAction(v_table, state, next_states, reward)

            # Ships the configuration and evaluates its performance
            state, reward = sim.ship(shipment, state, env)


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
            "solar": .2,
            "wind": .1,
            "bat": .4,
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
    v_table = initVTable()
    print(v_table.size)
    action = updateVAndGetAction(v_table, dummy_data[0][0], 150, dummy_data)
    save(v_table, "pickle-jar/v_table.pck")
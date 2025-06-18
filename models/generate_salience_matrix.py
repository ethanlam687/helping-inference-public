import numpy as np
from salience_analysis import compute_salience, pick_observed_center
from utils import general
import itertools

def generate_salience_matrix(configArray, goalspace, salience_metric = "euclidean"):

    # computes possible moves and drop locations for config

    # all that can be "picked up"
    moveable = general.moveable_indices(configArray)
    # all valid drop locations
    drop_locations = general.possible_drop_locations(configArray)
    # gets all legal (move, drop) combinations --- each pair is a single move
    combs = list(itertools.product(moveable, drop_locations))
    # remove moves if moveable-droppable == 18
    combs = [c for c in combs if c[0]-c[1] != 18]


    # create a zero matrix to hold salience values for move j, under goal i
    salience_matrix = np.zeros((len(combs), len(goalspace)))

    # loop over all goals 
    for i, goal in enumerate(goalspace):
        # then find the relative center for that goal
        center = pick_observed_center(goal)
        # loop over each possible (move, drop) move and assigns index j
        for j, move in enumerate(combs):
            # compute the salience for move pick-up index and fills in the salience value for the [j, i] cell
            s = compute_salience(move, center)
            salience_matrix[j, i] = s[f"{salience_metric}_salience"]

    return salience_matrix
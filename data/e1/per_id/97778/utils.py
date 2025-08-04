import numpy as np
from scipy.special import softmax
import pandas as pd
import itertools
import warnings
#warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning) 
np.set_printoptions(suppress=True)
import numpy as np
from ast import literal_eval
from scipy.special import logit, expit
import random
import math


class general:
  def run_moves(moves, configArray):
    c = configArray.copy()
    for m in moves:
      if moves.index(m)%2 == 0:
        print("architect move is", m)
      else:
        print("helper move is", m)
      c = general.update_config(c, m[0], m[1]) if m != "pass" else c
      general.display_config(c)
    
  def get_random_move(moves, w):
    r = random.choices(moves, weights = w, k = 1)[0]
    return r
    

  def display_config(configArray, latest_move = []):
    configArray_copy = configArray.copy()
    import matplotlib.pyplot as plt
    from matplotlib import colors
    import numpy as np

    # if len(latest_move)>0:
    #   configArray_copy[latest_move[0]] = 41

    data = np.array(configArray_copy).reshape((6,18))
    data[data=="white"] = 0
    data[data=="red"] = 11
    data[data=="blue"] = 21
    data[data=="green"] = 31
    
    data = data.astype(int)
    # create discrete colormap
    cmap = colors.ListedColormap(['white', 'red', 'steelblue', 'lightgreen', 'yellow'])
    bounds = [0,10,20,30, 40, 50]
    norm = colors.BoundaryNorm(bounds, cmap.N)

    fig, ax = plt.subplots()
    ax.imshow(data, cmap=cmap, norm=norm)

    # draw gridlines
    # Shift ticks to be at 0.5, 1.5, etc
    labels = ["A1", "A1", "A1", "A2","A2", "A2", "B1", "B1", "B1", "B2", "B2", "B2", "C1","C1","C1", "C2", "C2", "C2"]
    #labels = 'aaaaaabbbbbbcccccc'
    locs = np.arange(len(labels))
    for axis in [ax.xaxis]:
        axis.set_ticks(locs + 0.5, minor=True)
        axis.set(ticks=locs, ticklabels=labels)
    
    labels = '123456'
    locs = np.arange(len(labels))

    indices = np.arange(len(configArray)).reshape((6,18))

    for (i, j), z in np.ndenumerate(indices):
      ax.text(j, i, '{:0.0f}'.format(z), ha='center', va='center')

    for axis in [ax.yaxis]:
        axis.set_ticks(locs + 0.5, minor=True)
        axis.set(ticks=locs, ticklabels=labels)

    # Turn on the grid for the minor ticks
    ax.grid(True, which='minor')
    plt.rcParams["figure.figsize"] = (10,3)
    plt.show()

  def move_description_to_num(desc):
    desc = desc.replace('circle', '')
    desc = desc.replace('move a block from ', '')
    move_from, move_to = desc.split(' to ')
                              
    row_from = int(move_from[3]) 
    cell_from = int(move_from[-2::])  
    moveFromID = (row_from-1)*18 + (cell_from-1)

    row_to = int(move_to[3]) 
    cell_to = int(move_to[-2::])  
    moveToID = (row_to-1)*18 + (cell_to-1)
    
    return moveFromID,moveToID

  # need to have some way of categorizing the goal space

  def define_goalspace():
    actions = ["move",  "cover", "uncover", "clear", "fill"]
    locations = ["A", "A1", "A2",  "B", "B1", "B2",  "C", "C1", "C2" ]
    colors = ["red", "blue", "green"]

    goalspace = []
    for action in actions:
      if action in ["cover", "uncover"]:# cover/uncover goals are not dependent on location
        goals = [action + " " + color + " " + "all" for color in colors]
      elif action in ["clear", "fill"]: # clear and fill goals are not dependent on color
        if action == "clear":
          goals = [action + " " + "nocolor" + " " + location for location in locations]
        else:
          locationsub = ["A1", "A2",  "B1", "B2",  "C1", "C2" ]
          goals = [action + " " + "nocolor" + " " + location for location in locationsub]
      else:
        goals = [action + " " + color+ " " + location for color in colors for location in locations]
      
      goalspace.append(goals)
    goalspace = np.array(list(itertools.chain(*goalspace)))
    np.random.shuffle(goalspace)
    return list(goalspace)

  def compute_move_utility(configArray, move, goal):
    opt_moves_before = optimal_moves.select_optimal_moves(goal, configArray)
    #print("opt_moves_before: ", opt_moves_before)
    move_from = move[0]
    move_to =move[1]
    newConfig = general.update_config(configArray, move_from, move_to)
    opt_moves_after = optimal_moves.select_optimal_moves(goal, newConfig)
    #print("opt_moves_after: ", opt_moves_after)

    return opt_moves_before - opt_moves_after


  def generate_utility_matrix(configArray, goalspace):
      '''
      generates a matrix of utility values for each move-goal pair: dimensions are (moves, goals)
      '''
      # compute possible moves for this configuration
      moveable = general.moveable_indices(configArray)
      drop_locations = general.possible_drop_locations(configArray)
      combs = list(itertools.product(moveable, drop_locations))
      # remove moves if moveable-droppable == 18
      combs = [c for c in combs if c[0]-c[1] != 18]
      # now we compute the utility for each move-goal pair
      utility_matrix = np.zeros((len(combs), len(goalspace)))
      for i, g in enumerate(goalspace):
          for j, m in enumerate(combs):
              utility_matrix[j, i] = general.compute_move_utility(configArray, m, g)
      
      # utility_matrix = np.array([compute_move_utility(configArray, m, g) for i, g in enumerate(goalspace) for j, m in enumerate(combs)])
      # utility_matrix = utility_matrix.reshape(len(combs), len(goalspace))
      return utility_matrix, combs


  def get_initial_goal_probs(goalspace):
      goal_probs_final = np.array(softmax([1]*len(goalspace)))
      return goal_probs_final

  def softmax_t(x, tau):
    e_x = np.exp(x*tau)
    axis_sum = np.sum(e_x, axis=0)
    return e_x / axis_sum


  def moveable_indices(configArray):
    newArr = []

    for e in np.arange(len(configArray)):
      if configArray[e] != "white":
        #if the index is not in the first row
        if e > 17:
          #if the element on top is white, then it's draggable
          if configArray[e-18] == "white":
            newArr.append(e)
        else:
          newArr.append(e)  
    return newArr

  def possible_drop_locations(configArray):
    # filter to only white cells first
    filtereddropIndices = [i for i in range(len(configArray)) if configArray[i] == "white"]
    #logic for more filtering: if the color of the cell at the bottom is white too then exclude
    # x+18
    newArr = []
    for e in filtereddropIndices:
      if e < 90: # not last row
        if configArray[e+18] != "white":
          newArr.append(e)
      else:
        newArr.append(e)
    return newArr

  def update_config(configArray, move_from, move_to):
    oldConfig = configArray.copy()
    if move_from != "none":
      move_from = int(move_from)
      move_to = int(move_to)
      temp = oldConfig[move_from]
      oldConfig[move_from] = "white"
      oldConfig[move_to] = temp
    return oldConfig

  def goal_relevant_indices(goal_color, configArray):
    goal_relevant = [e for e in np.arange(108) if configArray[e] == goal_color ]
    return goal_relevant

  def goal_relevant_locations(goal_location, configArray):
    if goal_location == "A1":
      room_indices = [0,1,2,18, 19, 20, 36,37,38,54,55,56,72,73,74,90,91,92]
    elif goal_location == "A2":
      room_indices = [3,4,5,21,22,23,39,40,41,57,58,59,75,76,77,93,94,95]
    elif goal_location == "A":
      room_indices = [3,4,5,21,22,23,39,40,41,57,58,59,75,76,77,93,94,95, 0,1,2,18, 19, 20, 36,37,38,54,55,56,72,73,74,90,91,92]
    elif goal_location == "B1":
      room_indices = [6,7,8,24,25,26,42,43,44,60,61,62,78,79,80,96,97,98]
    elif goal_location == "B2":
      room_indices = [9,10,11,27,28,29,45,46,47,63,64,65,81,82,83,99,100,101]
    elif goal_location == "B":
      room_indices = [9,10,11,27,28,29,45,46,47,63,64,65,81,82,83,99,100,101, 6,7,8,24,25,26,42,43,44,60,61,62,78,79,80,96,97,98]
    elif goal_location == "C1":
      room_indices = [12,13,14,30,31,32,48,49,50,66,67,68,84,85,86,102,103,104]
    elif goal_location == "C2":
      room_indices = [15,16,17,33,34,35,51,52,53,69,70,71,87,88,89,105,106,107]
    elif goal_location == "C":
      room_indices = [15,16,17,33,34,35,51,52,53,69,70,71,87,88,89,105,106,107,12,13,14,30,31,32,48,49,50,66,67,68,84,85,86,102,103,104]
    else: #all 
      room_indices = np.arange(len(configArray))
    return room_indices
  
  def check_goal(goal, configArray):
    '''
    evaluates whether the goal has been achieved based on current configuration and ideal number of blocks
    goal is of the from ["action", "color", "location"]
    '''
    action, goal_color, goal_location = goal.split(" ")

    ## the check is different for each type of goal
    goal_location_indices = general.goal_relevant_locations(goal_location, configArray)
    configcolors = (np.take(configArray, goal_location_indices)).tolist()

    if action == "clear":
      # then we check whether everything is white 
      goal_count = configcolors.count("white")
      success = 1 if goal_count == len(goal_location_indices) else 0
    elif action == "fill":
      goal_count = configcolors.count("white")
      success = 1 if goal_count == 0 else 0
    elif action == "move":
      goal_count = configcolors.count(goal_color)
      success = 1 if goal_count == 10 else 0
    elif action == "remove":
      goal_count = configcolors.count(goal_color)
      success = 1 if goal_count == 0 else 0
    elif action == "elevate":
      floor_indices = range(90,108)
      floor_colors = (np.take(configcolors, floor_indices)).tolist()
      goal_count = floor_colors.count(goal_color)
      success = 1 if goal_count == 0 else 0
    elif action == "lower":
      # check if each configcolor is on the floor
      floor_indices = range(90,108)
      floor_colors = (np.take(configcolors, floor_indices)).tolist()
      goal_count = floor_colors.count(goal_color)
      success = 1 if goal_count == 10 else 0
      
    elif action == "surround":
      # count whitespace around the goal_color
      whitespace = optimal_moves.select_optimal_moves(goal, configArray)
      success = 1 if whitespace == 0 else 0
    elif action == "cover" or action == "uncover":
      # compute which of these are goal_color
      colorrelevant = np.array([int(i) if configArray[i]== goal_color else 999 for i in goal_location_indices])
      colorrelevant = (colorrelevant[colorrelevant != 999]).tolist()
      # compute open vs. obstructions
      moveable = general.moveable_indices(configArray)
      obstructed = list(set(colorrelevant) - set(moveable))
      open = list(set(colorrelevant) -set(obstructed))
      if action == "cover":
        success = 1 if len(open) == 0 else 0
      else:
        success = 1 if len(obstructed) == 0 else 0

    return success



class optimal_moves:
  def action_move(goal, configArray):
    action, goal_color, goal_location = goal.split(" ")
    moveable = general.moveable_indices(configArray)
    goal_relevant = general.goal_relevant_indices(goal_color, configArray)
    ## check which goal relevant indices are not in location
    location_indices = general.goal_relevant_locations(goal_location, configArray)
    not_in_location = list(set(goal_relevant)- set(location_indices))
    obstructed = list(set(not_in_location) - set(moveable))
    # get how many blocks obstructing the obstructed blocks
    blocker_indices = []
    blocker_dict = {}
    for o in obstructed:
      row = o // 18
      for row in range(1, row+1):
        index = o-(18*row)
        if(index>0):
          blocker_dict[index] = 0
          if configArray[index] != "white" and configArray[index] != goal_color:
            blocker_dict[index] = 1 if blocker_dict[index] == 0 else 0
            if configArray[index-18] == "white":
              # if the blocker is itself moveable only then is it a valid blocker
              blocker_indices.append(index)

    open = [e for e in not_in_location if e not in obstructed]
    open = list(set(open))
    obstructed = list(set(obstructed))
    blocker_indices = list(set(blocker_indices))

    sum_blockers = sum(blocker_dict.values())

    num_optimal_moves =len(open) + len(obstructed)+ sum_blockers

    final_move_candidates = {"open": open, "moveableblockers": blocker_indices, "obstructed": obstructed, "moveable": moveable}

    return num_optimal_moves
  
  def count_obstructions(obstructed, configArray, goal_color = None, countsamecolor = False):
    blocker_indices = []
    blocker_dict = {}
    for o in obstructed:
      #print(f"for obstructed {o}")
      row = o // 18
      #print("row=", row)
      for row in range(1, row+1):
        index = o-(18*row)
        #print("index=", index)
        if(index>0):
          #print("configArray[index]=",configArray[index])
          blocker_dict[index] = 0
          if countsamecolor == False:
            if configArray[index] != "white":
              #print(f"for row {row} and config index {o-(18*row)}, {configArray[index]}")
              blocker_dict[index] = 1 if blocker_dict[index] == 0 else 0
              if configArray[index-18] == "white":
                # if the blocker is itself moveable only then is it a valid blocker
                #print(f"{index} is a moveable blocker")
                blocker_indices.append(index)
          else:
            if configArray[index] != "white" and configArray[index] != goal_color:
              #print(f"for row {row} and config index {o-(18*row)}, {configArray[index]}")
              blocker_dict[index] = 1 if blocker_dict[index] == 0 else 0
              if configArray[index-18] == "white":
                # if the blocker is itself moveable only then is it a valid blocker
                #print(f"{index} is a moveable blocker")
                blocker_indices.append(index)
    #print(blocker_dict)
    sum_blockers = sum(blocker_dict.values())
    return sum_blockers
  
  def action_cover(goal, configArray):
    action, goal_color, goal_location = goal.split(" ")
    
    # there is a specific location where covering needs to occur
    locationrelevant = np.array(general.goal_relevant_locations(goal_location, configArray))  
    
    # compute which of these are goal_color
    colorrelevant = np.array([int(i) if configArray[i]== goal_color else 999 for i in locationrelevant])
    colorrelevant = (colorrelevant[colorrelevant != 999]).tolist()
    # compute open vs. obstructions
    moveable = general.moveable_indices(configArray)
    obstructed = list(set(colorrelevant) - set(moveable))
    open = list(set(colorrelevant) -set(obstructed))

    return len(open)

  def action_uncover(goal, configArray):
    action, goal_color, goal_location = goal.split(" ")
    # cover all X blocks in location N (which could be none too)
    locationrelevant = general.goal_relevant_locations(goal_location, configArray)
    
    # compute which of these are goal_color
    colorrelevant = np.array([int(i) if configArray[i]== goal_color else 999 for i in locationrelevant])
    colorrelevant = (colorrelevant[colorrelevant != 999]).tolist()
    # compute open vs. obstructions
    moveable = general.moveable_indices(configArray)
    obstructed = list(set(colorrelevant) - set(moveable))
    open = list(set(colorrelevant) -set(obstructed))
    sum_blockers = optimal_moves.count_obstructions(obstructed, configArray)
    num_optimal_moves =  sum_blockers
      
    return num_optimal_moves
  
  def action_clear(goal, configArray):
    action, goal_color, goal_location = goal.split(" ")

    locationrelevant = np.array(general.goal_relevant_locations(goal_location, configArray))
    # compute which of these are non-white, i.e. need to be removed
    occupied = np.array([int(i) if configArray[i] != "white" else 999 for i in locationrelevant])
    occupied = (occupied[occupied != 999]).tolist()
    return len(occupied)

  def action_fill(goal, configArray):
    action, goal_color, goal_location = goal.split(" ")
    locationrelevant = np.array(general.goal_relevant_locations(goal_location, configArray))
    # find #white
    empty = np.array([int(i) if configArray[i] == "white" else 999 for i in locationrelevant])
    empty = (empty[empty != 999]).tolist()
    return len(empty)

  def select_optimal_moves(goal, configArray):
    action, goal_color, goal_location = goal.split(" ")
    if action == "move":
      return optimal_moves.action_move(goal, configArray)
    elif action == "cover":
      return optimal_moves.action_cover(goal, configArray)
    elif action == "uncover":
      return optimal_moves.action_uncover(goal, configArray)
    elif action == "fill":
      return optimal_moves.action_fill(goal, configArray)
    else:
      return optimal_moves.action_clear(goal, configArray)

import numpy as np
from scipy.special import softmax
import pandas as pd
import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning) 
np.set_printoptions(suppress=True)
import numpy as np
from ast import literal_eval


from utils import *
from agents import *
from optimizer import *

import sys

class grid_search:
    def __init__(self, params) :
    # handle parameters
        self.literal_beta = float(params[0]) if len(params) > 0 else None
        self.pragmatic_beta = float(params[1]) if len(params) > 0 else None
        
        assert(self.literal_beta is not None)
        assert(self.pragmatic_beta is not None)
        
    def optimize_literal(self, moveID_df, experiment):
        '''
        '''
        IDs = moveID_df.ID.unique().tolist()
        probs_df = pd.DataFrame(columns = ["ID", "goal", "move","beta", "prob"])

        for ID in IDs:
            print(f"optimizing for ID {ID}")
            ID_df = moveID_df.loc[moveID_df['ID'] == ID]
            config = list(ID_df["config"])[0]

            initial_config = config.copy()

            goalspace = general.define_goalspace()
            
            
            for index, row in ID_df.iterrows():
                goal = row["goal"]
                #print(f"for goal {goal}")
                moveIDs = row["moveIDs"]
            
                currentConfig = initial_config.copy() # reset config for every goal                

                for i in range(0, len(moveIDs)):
                    move = moveIDs[i]
                    #print("move=", move)
                    if(experiment == "e1"):
                        if i % 2 == 0:
                            # architect move
                            move_probs, c  = architect.literal_architect_trial(currentConfig, goal, literalA_beta= self.literal_beta, goalspace = goalspace)
                            prob = move_probs[c.index(move)]
                            probs_df = pd.concat([probs_df, pd.DataFrame({'ID': [ID], 'goal': [goal], 'move': [move], 'beta': [self.beta], 'prob': [prob]})])
                            
                        else:
                            # helper move
                            prev_move = moveIDs[i-1] # previous architect move
                            # update based on architect move
                            currentConfig = general.update_config(currentConfig, prev_move[0], prev_move[1])
                            # update based on helper move 
                            if move == "pass":
                                currentConfig = general.update_config(currentConfig, "none", "none")
                            else:
                                currentConfig = general.update_config(currentConfig, move[0], move[1]) 
                    else:
                        # E2: every move is an architect move / no helper moves
                        move_probs, c  = architect.literal_architect_trial(currentConfig, goal, literalA_beta= self.beta, goalspace = goalspace)
                        prob = move_probs[c.index(move)]
                        probs_df = pd.concat([probs_df, pd.DataFrame({'ID': [ID], 'goal': [goal], 'move': [move], 'beta': [self.beta], 'prob': [prob]})])
                        currentConfig = general.update_config(currentConfig, move[0], move[1]) 

        
        return probs_df

    def optimize_pragmatic(self, moveID_df, experiment):
        '''
        '''
        IDs = moveID_df.ID.unique().tolist()
        probs_df = pd.DataFrame(columns = ["ID", "goal", "move","beta", "prob"])

        for ID in IDs:
            print(f"optimizing for ID {ID}")
            ID_df = moveID_df.loc[moveID_df['ID'] == ID]
            config = list(ID_df["config"])[0]

            initial_config = config.copy()
            goalspace = general.define_goalspace()
            goal_np_initial = general.get_initial_goal_probs(goalspace)
            goal_np = goal_np_initial.copy()

            
            
            
            for index, row in ID_df.iterrows():
                goal = row["goal"]
                #print(f"for goal {goal}")
                moveIDs = row["moveIDs"]
            
                currentConfig = initial_config.copy() # reset config for every goal                

                for i in range(0, len(moveIDs)):
                    move = moveIDs[i]
                    #print("move=", move)
                    if(experiment == "e1"):
                        if i % 2 == 0:
                            # architect move
                            move_probs, c  = architect.pragmatic_architect_trial(currentConfig, goal, goal_np, goal_noise = self.literal_beta, action_noise = self.pragmatic_beta)
                    
                            prob = move_probs[c.index(move)]
                            probs_df = pd.concat([probs_df, pd.DataFrame({'ID': [ID], 'goal': [goal], 'move': [move], 'literal_beta': [self.literal_beta],'pragmatic_beta': [self.pragmatic_beta], 'prob': [prob]})])
                            
                        else:
                            # helper move
                            prev_move = moveIDs[i-1] # previous architect move
                            # update based on architect move
                            currentConfig = general.update_config(currentConfig, prev_move[0], prev_move[1])
                            # update based on helper move 
                            if move == "pass":
                                currentConfig = general.update_config(currentConfig, "none", "none")
                            else:
                                currentConfig = general.update_config(currentConfig, move[0], move[1]) 
                    else:
                        # E2: every move is an architect move / no helper moves
                        move_probs, c  = architect.pragmatic_architect_trial(currentConfig, goal, goal_np, goal_noise = self.literal_beta, action_noise = self.pragmatic_beta)
                        prob = move_probs[c.index(move)]
                        probs_df = pd.concat([probs_df, pd.DataFrame({'ID': [ID], 'goal': [goal], 'move': [move], 'literal_beta': [self.literal_beta],'pragmatic_beta': [self.pragmatic_beta], 'prob': [prob]})])
                        currentConfig = general.update_config(currentConfig, move[0], move[1]) 

        
        return probs_df
                    
        
#exp_path = '../data/e2/'
moveID_df = pd.read_csv(f"final_move_df.csv",converters={"moveIDs": literal_eval, "config": literal_eval})


grid = grid_search(sys.argv[1:])

out = grid.optimize_pragmatic(moveID_df, experiment="e2")
out.to_csv(
f'model_prag/architect_df_{grid.literal_beta}_{grid.pragmatic_beta}_{sys.argv[3]}.csv'
)
import tensorflow as tf 
import os 
import numpy as np 
from auction import Auction
from states import State, CampaignBidderState
from pmfs import PMF



class Env():

    def __init__(self):
        pass

    def convert_to_states_tensor(self, states):
        states_tensor = []
        for state in states:
            vec = state.to_vector()
            states_tensor.append(vec)

        return np.array(states_tensor)
    
    def convert_to_actions_tensor(sef,actions):
        """
        Actions is an array of campaigns/bid_bundes, containing bid objects 
        """
        camp_array = []
        for bundle in actions:
            bid_array = []
            for bid in bundle.bid_entries:
                bid_array.append
    
    def reset(self,agents):
        state = Auction.reset(agents)
        return self.convert_to_states_tensor(state)
        
    def step(self,agents,day,my_agent):
        
        """
        One day of the auction 
        """
        state, results, is_done = Auction.run_auction(agents,day,my_agent)
        states = self.convert_to_states_tensor(state)
        results  = np.array(results)
        return states,results,is_done
        
    def play_single_episode():
        
        """
        pseudocode:
        for each day : 
            run the auction 
            intialize my RL agent 
            return states, actions, rewards for entire episode vectorized 
        """

    def train():
        """
        with tf.GradientTape() as tape:
            play_single_episode
            calculate loss
            optimize weights
            return the total_reward for the episode 
        """


         
    


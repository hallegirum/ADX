import tensorflow as tf 
import os 
import gym
import numpy as np 
import model as Model
from adx.agents import NDaysNCampaignsAgent
from adx.tier1_ndays_ncampaign_agent import Tier1NDaysNCampaignsAgent
from auction import Auction, RL_agent
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
        
    def play_single_episode(self, day, my_agent):
        
        """
        pseudocode:
        for each day : 
            run the auction 
            intialize my RL agent 
            return states, actions, rewards for entire episode vectorized 
        """

        state = self.reset()[0]
        # auction = Auction.run_auction(step, my_agent)

        states, actions, rewards = [], [], []
        max_steps = 10
        num_actions = 8 # number of different user campaigns in AdX
        my_agent = RL_agent.init

        test_agents = [NDaysNCampaignsAgent(name=f"Agent {i + 1}") for i in range(3)]+ [Tier1NDaysNCampaignsAgent(name=f"Agent {i + 1}") for i in range(6)]
        test_agents.append(my_agent)

        for step in range(max_steps):

            states.append(state)

            probability_all_actions = Model(state.reshape(-1, len(states))).numpy().reshape(-1)
            action = np.random.choice(num_actions, p= probability_all_actions)

            my_agent.set_action(action)

            states, results, is_done = self.step(test_agents, step, RL_agent)

            actions.append(action)
            rewards.append(results)
        
        states, actions, rewards = (np.array(states), np.array(actions), np.array(rewards))

        return states, actions, rewards




         
    


"""
This class is where the actor-critic model will be. 
"""

    def train(self, day):
        """
        with tf.GradientTape() as tape:
            play_single_episode
            calculate loss
            optimize weights
            return the total_reward for the episode 
        """
        tf.GradientTape()
        self.play_single_episode(day, RL_agent, len(Auction.generate_auction_item))
        total_reward = []
        # add other critic - model class, takes in a reward and starts the next bid
        return total_reward
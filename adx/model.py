from tensorflow import tf 
import numpy as np




class ReinforceWithBaseline(tf.keras.Model):
    def __init__(self, state_size, num_actions, num_sub_actions, num_dist_per_action=2):
        """
        num_actions- number of campaigns 
        num_sub_actions - market_segment per campaign (2 max)
        num_dist_per_action - the number of probability distributions per action, one for bid and one for
        limit 
        """
        super(ReinforceWithBaseline, self).__init__()
        self.num_actions = num_actions
        self.state_size = state_size

        learning_rate_schedule = tf.keras.optimizers.schedules.ExponentialDecay(
            initial_learning_rate = 0.002,
            decay_steps = 150,
            decay_rate = 0.5,
            staircase = True,
            name = "half_rate_every_150_steps")

        self.optimizer = tf.keras.optimizers.Adam(learning_rate = learning_rate_schedule)

        self.actor_size = 128
        self.actor = tf.keras.Sequential(
            layers = [
                # TODO:
                # 2 dense layers, leakyRELU as first activation function, and
                # final softmax activation
                # final output size = self.num_actions
                tf.keras.layers.Dense(self.actor_size),
                tf.keras.layers.LeakyReLU(),
                tf.keras.layers.Dense(num_sub_actions*num_dist_per_action,activation='softmax')
            ],
            name = "actor_network"
        )

        self.critic_size = 32
        self.critic = tf.keras.Sequential(
            layers = [
                # TODO:
                # 3 dense layers, leakyRELU as first and second activation
                # function, no activation on the final layer
                # final output size = 1
                tf.keras.layers.Dense(self.critic_size),
                tf.keras.layers.LeakyReLU(),
                tf.keras.layers.Dense(self.critic_size),
                tf.keras.layers.LeakyReLU(),
                tf.keras.layers.Dense(1),
            ],
            name = "critic_network"
        )

    def call(self,states):
        probabiliites = self.actor(states)
        return probabiliites

    def value_function(self, states):
        values = self.critic(states)
        return values 

    def loss(self, states, actions, discounted_rewards):
        """
        :param states: np.array (episode_length, state_size)
        :param actions: np.array (episode_length,)
        :param discounted_rewards: np.array (episode_length,)
        :return: loss, a TensorFlow scalar
        """

        probabilities_all_actions = self.call(states)
        values = self.value_function(states)

        actions = actions.reshape(-1, 1)
        probabilities_taken_actions = tf.gather_nd(probabilities_all_actions,actions, batch_dims = 1)
        advantages = tf.stop_gradient(discounted_rewards - values)

        actor_loss = (-1.0)*tf.reduce_sum(advantages*tf.math.log(probabilities_taken_actions))
        critic_loss = tf.reduce_sum((discounted_rewards - values)**2)

        total_loss = actor_loss + critic_loss

        return total_loss
    
    def discount(self, rewards):
        '''
        Takes in a list of rewards for each timestep in an episode, 
        and returns a list of the sum of discounted rewards for
        each timestep.

        :param rewards: List of rewards from an episode [r_{t0},..., r_{tN-1}]. 
        shape is [episode_length-1].
        :param discount_factor: Gamma discounting factor to use, defaults to .99.
        :return: discounted_rewards: list containing the sum of discounted 
        rewards for each timestep in the original rewards list.
        '''
        discount_factor = 0.99
        timesteps = len(rewards)
        discounted_rewards = np.zeros(timesteps)
        discounted_rewards[timesteps-1] = rewards[timesteps-1]
        for i in range(timesteps-2,-1,-1):
            discounted_rewards[i] = (discounted_rewards[i+1]*discount_factor) + rewards[i]
        return discounted_rewards


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

 






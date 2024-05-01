from adx_game_simulator import AdXGameSimulator as adx 
from agents import NDaysNCampaignsAgent
from adx.structures import Bid, Campaign, BidBundle, MarketSegment
import random
from typing import Set, Dict
from math import isfinite, atan




class RL_agent(NDaysNCampaignsAgent):

    def __init__(self):
        super().__init__()


    def on_new_game(self) -> None:
        pass
     

    def get_campaign_bids(self, campaigns_for_auction: Set[Campaign]) -> Dict[Campaign, float]:
        bids = {}
        for campaign in campaigns_for_auction:
            bid_value = campaign.reach * (random.random() * 0.9 + 0.1)
            bids[campaign] = bid_value
        return bids



    def get_ad_bids(self) -> Set[BidBundle]:
        """
        choose action from model return action -> convert from tensor to Set[Bidbundle]
        """ 

class Auction(adx):
    def __init__(self, config: Dict | None = None):
        super().__init__(config)
        self.total_profits = None

    def calculate_effective_reach(x: int, R: int) -> float:
        return (2.0 / 4.08577) * (atan(4.08577 * ((x + 0.0) / R) - 3.08577) - atan(-3.08577))
    
    def reset(self,agents:list[NDaysNCampaignsAgent]):
        self.total_profits = {agent : 0.0 for agent in agents}
        self.states = self.init_agents(agents)
        self.campaigns = dict()
        # Initialize campaigns 
        for agent in self.agents:    
            agent.current_game = 1
            agent.my_campaigns = set()
            random_campaign = self.generate_campaign(start_day=1)
            agent_state = self.states[agent]
            random_campaign.budget = random_campaign.reach
            agent_state.add_campaign(random_campaign)
            agent.my_campaigns.add(random_campaign)
            self.campaigns[random_campaign.uid] = random_campaign
        return self.states

    def run_auction(self,day,myagent):
        # Update 
        for agent in self.agents:
            agent.current_day = day

        # Generate new campaigns and filter
        if day + 1 < self.num_days + 1:
            new_campaigns = [self.generate_campaign(start_day=day + 1) for _ in range(self.campaigns_per_day)]
            new_campaigns = [c for c in new_campaigns if c.end_day <= self.num_days]
            # Solicit campaign bids and run campaign auctions
            agent_bids = dict()
            for agent in self.agents:
                agent_bids[agent] = agent.get_campaign_bids(new_campaigns)

            # Solicit ad bids from agents and run ad auctions
            ad_bids = []
            for agent in self.agents:
                ad_bids.extend(agent.get_ad_bids())
            users = self.generate_auction_items(10000)
            self.run_ad_auctions(ad_bids, users, day)

            # Update campaign states, quality scores, and profits
            for agent in self.agents:
                agent_state = self.states[agent]
                todays_profit = 0.0
                new_qs_count = 0
                new_qs_val = 0.0

                for campaign in agent_state.campaigns.values():
                    if campaign.start_day <= day <= campaign.end_day:
                        if day == campaign.end_day:
                            impressions = agent_state.impressions[campaign.uid]
                            total_cost = agent_state.spend[campaign.uid]
                            effective_reach = self.calculate_effective_reach(impressions, campaign.reach)
                            todays_profit += (effective_reach) * agent_state.budgets[campaign.uid] - total_cost

                            new_qs_count += 1
                            new_qs_val += effective_reach

                if new_qs_count > 0:
                    new_qs_val /= new_qs_count
                    self.states[agent].quality_score = (1 - self.α) * self.states[agent].quality_score + self.α * new_qs_val
                    agent.quality_score = self.states[agent].quality_score

                agent_state.profits += todays_profit
                agent.profit += todays_profit
            
            # Run campaign auctions
            self.run_campaign_auctions(agent_bids, new_campaigns)
            # Run campaign endowments
            for agent in self.agents:
                if random.random() < min(1, agent.quality_score):
                    random_campaign = self.generate_campaign(start_day=day)
                    agent_state = self.states[agent]
                    random_campaign.budget = random_campaign.reach
                    agent_state.add_campaign(random_campaign)
                    agent.my_campaigns.add(random_campaign)
                    self.campaigns[random_campaign.uid] = random_campaign
        for agent in self.agents:
            self.total_profits[agent] += self.states[agent].profits 
        
        done = False
        if day == 10:
            done = True
        return self.states,todays_profit[myagent],done
        




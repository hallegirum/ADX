# from adx.agents import NDaysNCampaignsAgent
# from adx.tier1_ndays_ncampaign_agent import Tier1NDaysNCampaignsAgent
# from adx.adx_game_simulator import AdXGameSimulator
# from adx.structures import Bid, Campaign, BidBundle, MarketSegment
from agents import NDaysNCampaignsAgent
from Agent1 import AGENT1 
from tier1_ndays_ncampaign_agent import Tier1NDaysNCampaignsAgent
from adx_game_simulator import AdXGameSimulator
from structures import Bid, Campaign, BidBundle, MarketSegment
from typing import Set, Dict
import os 
import pickle
import json
from plots import plot, plot_camp, profit_plot

class MyNDaysNCampaignsAgent(NDaysNCampaignsAgent):

    def __init__(self):
        # TODO: fill this in (if necessary)
        super().__init__()
        self.name =  "orangepeel"  
        self.market_freq = {}
        self.market_prop = {}
        self.build_freq()
        self.build_prop()
        self.total = 10000
        self.on_new_game()


    def build_freq(self):
        # building a frequqency dictionary which maps user frequencies of for all market segments 
        for segment in MarketSegment.all_segments():
            if segment == MarketSegment(("Male","Young")):
                self.market_freq[segment] = 2353
            elif segment == MarketSegment(("Male","Old")):
                self.market_freq[segment] = 2603
            elif segment == MarketSegment(("Female","Young")):
                self.market_freq[segment] = 2236
            elif segment == MarketSegment(("Female","Old")):
                self.market_freq[segment] = 2808
            elif segment == MarketSegment(("Male","LowIncome")):
                self.market_freq[segment] = 3631
            elif segment == MarketSegment(("Male","HighIncome")):
                self.market_freq[segment] = 1325
            elif segment == MarketSegment(("Female","LowIncome")):
                self.market_freq[segment] = 4381
            elif segment == MarketSegment(("Female","HighIncome")):
                self.market_freq[segment] = 663
            elif segment == MarketSegment(("Young","LowIncome")):
                self.market_freq[segment] = 3816      
            elif segment == MarketSegment(("Young","HighIncome")):
                self.market_freq[segment] = 773
            elif segment == MarketSegment(("Old","LowIncome")):
                self.market_freq[segment] = 4196
            elif segment == MarketSegment(("Old","HighIncome")):
                self.market_freq[segment] = 1215 
            elif segment == MarketSegment(("Male", "Young", "LowIncome")):
                self.market_freq[segment] = 1836
            elif segment == MarketSegment(("Male", "Young", "HighIncome")):
                self.market_freq[segment] = 517
            elif segment == MarketSegment(("Male", "Old", "LowIncome")):   
                self.market_freq[segment] = 1795
            elif segment == MarketSegment(("Male", "Old", "HighIncome")):
                self.market_freq[segment] = 808   
            elif segment == MarketSegment(("Female", "Young", "LowIncome")):
                self.market_freq[segment] = 1980
            elif segment == MarketSegment(("Female", "Young", "HighIncome")):
                self.market_freq[segment] = 256
            elif segment == MarketSegment(("Female", "Old", "LowIncome")): 
                self.market_freq[segment] = 2401
            elif segment == MarketSegment(("Female", "Old", "HighIncome")):
                self.market_freq[segment] = 407

    def build_prop(self):   
        for segment in MarketSegment.all_segments():
            if segment == MarketSegment(("Male", "Young", "LowIncome")):
                self.market_prop[segment] = 1836/(1836 + 517)
            elif segment == MarketSegment(("Male", "Young", "HighIncome")):
                self.market_prop[segment] = 517/(1836 + 517)
            elif segment == MarketSegment(("Male", "Old", "LowIncome")):   
                self.market_prop[segment] = 1795/(1795 + 808)
            elif segment == MarketSegment(("Male", "Old", "HighIncome")):
                self.market_prop[segment] = 808/(1795 + 808)   
            elif segment == MarketSegment(("Female", "Young", "LowIncome")):
                self.market_prop[segment] = 1980/(256 + 1980)   
            elif segment == MarketSegment(("Female", "Young", "HighIncome")):
                self.market_prop[segment] = 256/(256 + 1980)
            elif segment == MarketSegment(("Female", "Old", "LowIncome")): 
                self.market_prop[segment] = 2401/(407 + 2401)
            elif segment == MarketSegment(("Female", "Old", "HighIncome")):
                self.market_prop[segment] = 407/(407 + 2401)
            
    def on_new_game(self) -> None:
        self.item_bid_list = []
        self.var_list = []
        self.ef_list  = []
        self.new_var_list = []
        self.market_prop_list = []
        self.limit_list = []
        self.camp_bid_list = []
        self.market_prop_c = []
        self.similarity_score = []



    # helper function that given a campaign returns a dictionary with all the subsets of the campaigns'
    # market segment and the value being the proportion of the market segment 
    def get_market_seg(self,camp):
        seg = camp.target_segment
        market_segments = {}
        for segment in MarketSegment.all_segments():
            if seg.issubset(segment) and segment in self.market_prop.keys():
                market_segments[segment] = self.market_prop[segment]
        assert(len(market_segments.keys())<=2)
        assert(len(market_segments.keys())>0)
        return market_segments 

    def get_ad_bids(self) -> Set[BidBundle]:
        # for data plotting 

        camp_bundles = set()
        campaigns = self.get_active_campaigns()
        for camp in campaigns:
            # shadding bid based on some weighted average of effective reach and days left of campaign
            effective_reach = self.effective_reach(self.get_cumulative_reach(camp),camp.reach)
            days_left = camp.end_day - self.get_current_day()
            var = 0.8*(1.38442 - effective_reach) + 0.2*days_left 
            var = 1 if var == 0 else var
            markets = self.get_market_seg(camp)
            # defining bid bundle
            campaign_limit = camp.budget * var 
            bundle =  BidBundle(camp.uid,campaign_limit,None)
            bid_set = set()
        # bidding based on the subset market segments of the target segment 
            for seg in markets.keys():
                self.ef_list.append(effective_reach)
                self.var_list.append(var)
                new_var = 0.3* var + 0.7*(1-self.market_prop[seg])
                self.new_var_list.append(new_var)
                self.market_prop_list.append(self.market_prop[seg])
                item_bid = new_var*(camp.budget/camp.reach)
                self.item_bid_list.append(item_bid)
                limit = new_var* camp.budget 
                self.limit_list.append(limit)
                bid = Bid(self,seg,item_bid,limit)
                bid_set.add(bid)
            bundle.bid_entries = bid_set
            camp_bundles.add(bundle)
        return camp_bundles
    

    def similar_segments(self,campaigns_for_auction):
        freq_table = {}
        for c in campaigns_for_auction: # iterate through all the campaigns
            market_segment = c.target_segment 
            for seg in market_segment.all_segments(): # iterate through all the market segments
                if market_segment.issubset(seg):
                    if seg in freq_table:
                        freq_table[seg] = freq_table[seg] + 1
                    else:
                        freq_table[seg] = 1
            for my_camp in self.get_active_campaigns():
                ms = my_camp.target_segment 
                if market_segment.issubset(ms):
                    freq_table[ms] +=1 
        return freq_table


                    
            
        

    def get_campaign_bids(self, campaigns_for_auction:  Set[Campaign]) -> Dict[Campaign, float]:
        # TODO: fill this in 
        bids = {}
        for camp in campaigns_for_auction:
            market_segment = camp.target_segment # the target we are trying to reach

            #frequency table of market segments -> frequency in campaigns for auction
            freq_table = self.similar_segments(campaigns_for_auction)    
            total_camp_num = len(self.get_active_campaigns()) + len(campaigns_for_auction)
            prop_same_camp = 1 + freq_table[market_segment]/ max(1,total_camp_num)
            bid = (1-(self.market_freq[market_segment]/self.total))*camp.reach*prop_same_camp 
            self.camp_bid_list.append(bid)
            self.similarity_score.append(prop_same_camp)
            self.market_prop_c.append(self.market_freq[market_segment]/self.total)
            if not self.is_valid_campaign_bid(camp,bid):
                bid = self.clip_campaign_bid(camp,bid)
            bids.__setitem__(camp, bid)
        return bids
    


 

if __name__ == "__main__":
    # Here's an opportunity to test offline against some TA agents. Just run this file to do so.
    myagent =MyNDaysNCampaignsAgent()
    test_agents = [myagent] + [Tier1NDaysNCampaignsAgent(name=f"Agent {i + 1}") for i in range(4)] + [AGENT1(name=f"My {i + 1}") for i in range(5)]
    # Don't change this. Adapt initialization to your environment
    simulator = AdXGameSimulator()
    simulator.run_simulation(test_agents,500,myagent)
            
    # plot(myagent.item_bid_list,myagent.ef_list,myagent.var_list,myagent.new_var_list,myagent.market_prop_list)
    # plot_camp(myagent.camp_bid_list,myagent.similarity_score,myagent.market_prop_c)

    # make keys of 

    profits_per_simulation = simulator.profits
    profit_plot(profits_per_simulation)

  
    
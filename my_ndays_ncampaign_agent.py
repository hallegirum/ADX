from adx.agents import NDaysNCampaignsAgent
from adx.tier1_ndays_ncampaign_agent import Tier1NDaysNCampaignsAgent
from adx.adx_game_simulator import AdXGameSimulator
from adx.structures import Bid, Campaign, BidBundle, MarketSegment
from typing import Set, Dict
import os 
import pickle
import json

class MyNDaysNCampaignsAgent(NDaysNCampaignsAgent):

    def __init__(self):
        # TODO: fill this in (if necessary)
        super().__init__()
        self.name = "orange peel"  
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
        # TODO: fill this in (if necessary)
        self.bids = {}
        self.camp_bids = {}

    # helper function that given a campaign returns a dictionary with all the subsets of the campaigns'
    # market segment and the value being the proportion of the market segment 
    def get_market_seg(self,camp):
        seg = camp.target_segment
        market_segments = {}
        for segment in MarketSegment.all_segments():
            if segment.issubset(seg) and segment in self.market_prop.keys():
                market_segments[segment] = self.market_prop[segment]
        assert(len(market_segments.keys())<=2)
        return market_segments 



    def get_ad_bids(self) -> Set[BidBundle]:
        # TODO: fill this in
        camp_bundles = set()
        campaigns = self.get_active_campaigns()
        for camp in campaigns:
            # shadding bid based on some weighted average of effective reach and days left of campaign 
            effective_reach = self.get_cumulative_reach(camp)
            days_left = camp.end_day - self.get_current_day()
            var = 0.8*effective_reach + 0.2*days_left 
            var = 1 if var == 0 else var
            markets = self.get_market_seg(camp)
            # defining bid bundle
            campaign_limit = camp.budget * var 
            bundle =  BidBundle(camp.uid,campaign_limit,None)
            bid_set = set()
        # bidding based on the subset market segments of the target segment 
            for seg in markets.keys():
                item_bid = var*(camp.budget/camp.reach)* self.market_prop[seg]
                limit = var* camp.budget * self.market_prop[seg]
                bid = Bid(self,seg,item_bid,limit)
                bid_set.add(bid)
                self.bids[camp] = bid
            bundle.bid_entries = bid_set 
            camp_bundles.add(bundle)
        self.write(self.bids,'bids')
        return camp_bundles

    def get_campaign_bids(self, campaigns_for_auction:  Set[Campaign]) -> Dict[Campaign, float]:
        # TODO: fill this in 
        bids = {}
        for camp in campaigns_for_auction:
            market_segment = camp.target_segment # the target we are trying to reach

            #TODO: when we do market segment / total is that the appropriate total 10000? or is it total of the sub category?
            #because some subsets already return proportions... idk maybe I'm overcomplicating I'll have to think about it
            same = 0
            for my_camp in self.get_active_campaigns():
                ms = my_camp.target_segment 
                if market_segment.issubset(ms) or ms.issubset(market_segment):
                    same +=1

            prop_same_camp = same/ max(1,len(self.get_active_campaigns()))
            bid = (1-(self.market_freq[market_segment]/self.total))*camp.reach*prop_same_camp 
            if not self.is_valid_campaign_bid(camp,bid):
                bid = self.clip_campaign_bid(camp,bid)
            self.camp_bids[camp] = bid
            bids.__setitem__(camp, bid)
        self.write(self.camp_bids,'camp_bids')
        return bids

    def write(self,dataset, file_path: str):
	#Write the json dataset to a file
        json_serializable_dict = {}
        for campaign, bid in dataset.items():
            json_serializable_dict[str(campaign)] = str(bid)

        # Save the dictionary to a JSON file
        with open(file_path, 'w') as json_file:
            json.dump(json_serializable_dict, json_file)

        # # Optionally, you can also save the original dictionary to a pickle file
        # with open(file_name, 'wb') as pickle_file:
        #     pickle.dump(dataset, pickle_file)


    

if __name__ == "__main__":
    # Here's an opportunity to test offline against some TA agents. Just run this file to do so.
    test_agents = [MyNDaysNCampaignsAgent()] + [Tier1NDaysNCampaignsAgent(name=f"Agent {i + 1}") for i in range(9)]

    # Don't change this. Adapt initialization to your environment
    simulator = AdXGameSimulator()
    simulator.run_simulation(agents=test_agents, num_simulations=20)
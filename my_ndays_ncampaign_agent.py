from adx.agents import NDaysNCampaignsAgent
from adx.tier1_ndays_ncampaign_agent import Tier1NDaysNCampaignsAgent
from adx.adx_game_simulator import AdXGameSimulator
from adx.structures import Bid, Campaign, BidBundle 
from typing import Set, Dict

class MyNDaysNCampaignsAgent(NDaysNCampaignsAgent):

    def __init__(self):
        # TODO: fill this in (if necessary)
        super().__init__()
        self.name = ""  # TODO: enter a name.
        self.market_freq = {}
        self.market_prop = {}
        self.build_freq()
        self.build_prop()
        self.total = 10000


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
        pass

    def get_market_seg(self,camp->Campaign):
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
            var = 0.7*effective_reach + 0.3*days_left 
            var=1  if var==0
            markets = self.get_market_seg(camp)
            # defining bid bundle
            campaign_limit = camp.budget * var 
            bundle =  new BidBundle(camp.uid,campaign_limit,None)
            bid_set = set()
        # bidding based on the subset market segments of the target segment 
            for seg in markets.keys():
                item_bid = var*(camp.budget/camp.reach)* self.market_prop[seg]
                limit = var* camp.budget * self.market_prop[seg]
                bid = new Bid(self,seg,item_bid,limit)
                bid_set.add(bid)
            bundle.bid_entries = bid_set 
            camp_bundles.add(bundle)
        return camp_bundles

    def get_campaign_bids(self, campaigns_for_auction:  Set[Campaign]) -> Dict[Campaign, float]:
        # TODO: fill this in 
        bids = {}

        return bids
    
    def get_freq(self,marketsegment)

if __name__ == "__main__":
    # Here's an opportunity to test offline against some TA agents. Just run this file to do so.
    test_agents = [MyNDaysNCampaignsAgent()] + [Tier1NDaysNCampaignsAgent(name=f"Agent {i + 1}") for i in range(9)]

    # Don't change this. Adapt initialization to your environment
    simulator = AdXGameSimulator()
    simulator.run_simulation(agents=test_agents, num_simulations=500)
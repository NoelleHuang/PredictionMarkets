from otree.api import (
    models,
    widgets,
    BaseConstants,
    BaseSubsession,
    BaseGroup,
    BasePlayer,
    Currency as c,
    currency_range,
)

import random
import numpy as np


def calculate_price(existing_contract, new_contract,liquidity):
    new_contract = np.array(new_contract, dtype=float)
    existing_contract = np.array(existing_contract, dtype=float)
    
    new_contract += existing_contract
    price = (liquidity*np.log(np.exp(new_contract[0]/liquidity)+np.exp(new_contract[1]/liquidity))-liquidity*np.log(np.exp(existing_contract[0]/liquidity)+np.exp(existing_contract[1]/liquidity)))

    #print(existing_contract, new_contract, price)

    return price


author = 'Noelle Huang'

doc = """
This is treatment B to the study. In treatment B, one player in each group assigns order to all players within the group. In contrast to treatment A, players no longer receive order randomly assigned by system.
"""


class Constants(BaseConstants):
    name_in_url = 'Prediction_Markets_TreatmentB'
    players_per_group = 3
    characters = ['Michael','Dwight','Jim']
    round_initial_balance = 10

    # the following model parameters are now configurable in admin page
    #liquidity = 1 
    num_rounds = 10

    payoff_round = np.random.randint(low=2, high=num_rounds+1, size=1) 
    # first round is practice round, so doesn't count towards payment
    # low is inclusive, high is exclusive
    possible_states = ['Red', 'Green']
    signal_accuracy = 2/3
    random.seed (11)
    

    instructions_template = 'thesisPM/instructions.html'


class Subsession(BaseSubsession):
    true_state = models.StringField()
    signal_assignment = models.StringField()     
    
    def assign_signal(self):
        signals = []
        if self.true_state == Constants.possible_states[0]:
            signals = np.random.choice(Constants.possible_states,Constants.players_per_group,p=[1-Constants.signal_accuracy,Constants.signal_accuracy])
        else:
             signals = np.random.choice(Constants.possible_states,Constants.players_per_group,p=[Constants.signal_accuracy,1-Constants.signal_accuracy])
        
        for p in self.get_players():
            p.private_signal = signals[p.id_in_group-1]


        self.signal_assignment = ', '.join(signals)



    def creating_session(self):
        self.group_randomly()
        self.true_state = random.choice(Constants.possible_states)
        self.assign_signal()

        #for p in self.get_players():
        #    p.alias = p.role()
        # print (self.signal_assignment)
    


class Group(BaseGroup):

    alias_assignment = models.StringField
    alias_string = models.StringField
    Red_price = models.FloatField(initial=0.5) 
    Green_price = models.FloatField(initial=0.5) 

    Michael_index = models.IntegerField(choices=[1,2,3])
    Dwight_index = models.IntegerField(choices=[1,2,3])
    Jim_index = models.IntegerField(choices=[1,2,3])
    role_by_order = models.StringField()


    # New groups keep getting created even when new subsessions are not. dafuq
    def __init__(self, *args, **kwargs):
        BaseGroup.__init__(self, *args, **kwargs)
        np.random.seed(self.id_in_subsession)
        self.alias_assignment = np.random.permutation(Constants.characters)
        self.alias_string = ', '.join(self.alias_assignment)

def get_existing_contract(group):
        Red = 0
        Green = 0

        for player in group.get_players():
            Red += player.Red_share
            Green += player.Green_share
    
        #print(np.array([Red,Green]))
        return np.array([Red,Green])

class Player(BasePlayer):
    #alias = models.StringField()
    private_signal = models.StringField()
    order = models.IntegerField(initial = None)
    Red_share = models.FloatField(initial=0.0) 
    Green_share = models.FloatField(initial=0.0) 
    balance = models.FloatField(initial=Constants.round_initial_balance)
    payment = models.FloatField(initial=0.0)


    def role(self):
        return self.group.alias_assignment[self.id_in_group - 1]

    def Red_share_choices(self):
        liquidity = self.session.config['liquidity']
        options = []
        existing = get_existing_contract(self.group)
        unit = np.array([1, 0], dtype=int) 
        k = np.array(unit)   

        while calculate_price(existing, k,liquidity) < self.balance:
             options.append([sum(k),'{} for ${}'.format(sum(k), calculate_price(existing, k, liquidity))])
            # to display 3 decimal float, uncomment this line
            #options.append([sum(k),'{} for ${:.3f}'.format(sum(k), calculate_price(existing, k))])
             k+=unit

        options.insert(0, [0, 'None'])
        return options
    
    def Green_share_choices(self):
        liquidity = self.session.config['liquidity']
        options = []
        existing = get_existing_contract(self.group)
        unit = np.array([0, 1], dtype=int) 
        k = np.array(unit)   
        while calculate_price(existing, k,liquidity) < self.balance:
             options.append([sum(k),'{} for ${}'.format(sum(k), calculate_price(existing, k, liquidity))])
            # to display 3 decimal float, uncomment this line
            #options.append([sum(k),'{} for ${:.3f}'.format(sum(k), calculate_price(existing, k))])
             k+=unit
            #print("{:.2f}".format())

        options.insert(0, [0, 'None'])

        return options

    def calculate_cost(self): 
        return Constants.round_initial_balance - self.balance

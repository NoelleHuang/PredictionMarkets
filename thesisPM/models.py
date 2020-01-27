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

def calculate_price(existing_contract, new_contract):
    new_contract = np.array(new_contract, dtype=float)
    existing_contract = np.array(existing_contract, dtype=float)
    
    new_contract += existing_contract
    liquidity = Constants.liquidity
    price = (liquidity*np.log(np.exp(new_contract[0]/liquidity)+np.exp(new_contract[1]/liquidity))-liquidity*np.log(np.exp(existing_contract[0]/liquidity)+np.exp(existing_contract[1]/liquidity)))

    print(existing_contract, new_contract, price)

    return price

author = 'Your name here'

doc = """
Your app description
"""


class Constants(BaseConstants):
    name_in_url = 'Prediction_Markets'
    players_per_group = 3
    num_rounds = 2
    round_initial_balance = 10
    liquidity = 1

    instructions_template = 'thesisPM/instructions.html'


class Subsession(BaseSubsession):
    def creating_session(self):
        self.group_randomly()

class Group(BaseGroup):
    alias_assignment = models.StringField
    alias_string = models.StringField
    yes_price = models.FloatField(initial=0.5) # yes price = 0.8
    no_price = models.FloatField(initial=0.5) # no price = x, where x is the price of a unit of "no" at the time of decision

    # New groups keep getting created even when new subsessions are not. dafuq
    def __init__(self, *args, **kwargs):
        BaseGroup.__init__(self, *args, **kwargs)
        np.random.seed(self.id_in_subsession)
        self.alias_assignment = np.random.permutation(['Dwight','Michael','Jim'])
        self.alias_string = ', '.join(self.alias_assignment)

    total_yes_so_far = models.FloatField(initial = 0.0)
    totall_no_so_far = models.FloatField(initial = 0.0)

def get_existing_contract(group):
    yes = 0
    no = 0

    for player in group.get_players():
        yes += player.yes_share
        no += player.no_share
    
    print(np.array([yes,no]))
    return np.array([yes,no])

class Player(BasePlayer):
    private_signal = models.FloatField()
    trade_order = models.IntegerField()
    
    # record player's activities in the experiment; unless specified, default input in the field is "None"
    # for instance, in first session, player purchases 5 tokens of "yes" at current price of $0.8, but did not purchase any "no" tokens, this will be recorded as...
    yes_share = models.FloatField(initial=0.0) # yes share = 5.0
    no_share = models.FloatField(initial=0.0, label="# of No to purchase") # no share = 0.0
    balance = models.FloatField(initial=Constants.round_initial_balance)

    def yes_share_choices(self):
        options = []
        existing = get_existing_contract(self.group)
        unit = np.array([1, 0], dtype=int) 
        k = np.array(unit)   
        while calculate_price(existing, k) < self.balance:
            print(k)
            options.append([sum(k),'{} for ${}'.format(sum(k), calculate_price(existing, k))])
            k+=unit

        options.insert(0, [0, 'None'])

        return options

    def role(self):
        return self.group.alias_assignment[self.id_in_group - 1]

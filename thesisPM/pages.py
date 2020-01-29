from otree.api import Currency as c, currency_range
from otree import models
from ._builtin import Page, WaitPage
from .models import Constants, calculate_price, get_existing_contract
import numpy as np

def update_balances(group):
    for player in group.get_players():
        if player.balance == Constants.round_initial_balance:
            share = max(player.yes_share, player.no_share)
            if share > 0:
                their_shares = np.array([player.yes_share, player.no_share])
                old_existing_shares = get_existing_contract(group) - their_shares
                player.balance -= calculate_price(old_existing_shares, their_shares)

class Instruction_0welcome(Page):
    def is_displayed(self):
        return self.round_number==1

class Instruction_1players(Page):
   def is_displayed(self):
        return self.round_number==1

class Instruction_2payment(Page):
    def is_displayed(self):
        return self.round_number==1

class Instruction_3interface(Page):
   def is_displayed(self):
        return self.round_number==1

class Instruction_4characters(Page):
    def is_displayed(self):
        return self.round_number==1

class Instruction_5balance(Page):
    def is_displayed(self):
        return self.round_number==1

class Instruction_6prices(Page):
    def is_displayed(self):
        return self.round_number==1

class Instruction_7questionsHints(Page):
    def is_displayed(self):
        return self.round_number==1

class Instruction_8orderAssignment(Page):
    def is_displayed(self):
        return self.round_number==1

# round introduction, display only once at the beginning of each round
# reminds random group shuffling each round 
# (later when both ordered and unordered are implemented, explains ordered or unordered rules)
class Introduction_Round(Page):
    pass 

class Question_Player1 (Page):
    form_model = 'player'
    form_fields = ['yes_share','no_share']

    def is_displayed(self):
   #     update_balances(self.player.group)
       return self.player.id_in_group == 1

    def before_next_page(self):
        print('before next page')
        update_balances(self.player.group)
        

class WaitForP11 (WaitPage):

    form_fields = ['balance']

    def before_next_page(self):
       update_balances(self.player.group)



class Question_Player2 (Page):
    
    form_model = 'player'
    form_fields = ['yes_share','no_share']

    def is_displayed(self):
        update_balances(self.player.group)
        return self.player.id_in_group == 2
    def before_next_page(self):
        update_balances(self.player.group)

class WaitForP2 (WaitPage):

    form_model = 'player'
    form_fields = ['balance']

    def is_displayed(self):
        update_balances(self.player.group)
        return self.player.id_in_group != 2
    def before_next_page(self):
        print('now')
        update_balances(self.player.group)

class Question_Player3 (Page):
    
    form_model = 'player'
    form_fields = ['yes_share','no_share']

    def is_displayed(self):
        update_balances(self.player.group)
        return self.player.id_in_group == 3
    def before_next_page(self):
        update_balances(self.player.group)

class WaitForP3 (WaitPage):

    form_model = 'player'
    form_fields = ['balance']

    def is_displayed(self):
        update_balances(self.player.group)
        return self.player.id_in_group != 3
    def before_next_page(self):
        print('now')
        update_balances(self.player.group)
        
class ResultsWaitPage(WaitPage):
    def is_displayed(self):
        update_balances(self.player.group)
        return True
    def after_all_players_arrive(self):
        pass
        
wait_for_all_groups = True

class Results(Page):
    pass


page_sequence = [Instruction_0welcome, # Instruction_1players, Instruction_2payment, Instruction_3interface, Instruction_4characters, Instruction_5balance, Instruction_6prices, Instruction_7questionsHints, Instruction_8orderAssignment,
                 Question_Player1, 
                 WaitForP11, 
                 Question_Player2, 
                 WaitForP2,
                 Question_Player3, 
                 WaitForP3,
                 ResultsWaitPage, 
                 Results
                 ]

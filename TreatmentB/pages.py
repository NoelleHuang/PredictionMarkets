from otree.api import Currency as c, currency_range
from otree import models
from ._builtin import Page, WaitPage
from .models import Constants, calculate_price, get_existing_contract
import numpy as np
# import pandas as pd



def update_balances(group):
    liquidity = group.session.config['liquidity']
    for player in group.get_players():
        if player.balance == Constants.round_initial_balance:
            share = max(player.Red_share, player.Green_share)
            if share > 0:
                their_shares = np.array([player.Red_share, player.Green_share])
                old_existing_shares = get_existing_contract(group) - their_shares
                player.balance -= calculate_price(old_existing_shares, their_shares,liquidity)



# round introduction, display only once at the beginning of each round
# reminds random group shuffling each round 
# (later when both ordered and unordered are implemented, explains ordered or uGreenrdered rules)


class MyWaitPage (WaitPage):
    template_name = 'TreatmentB/MyWaitPage.html'
    def is_displayed(self):
        return self.round_number==1

class SelectOrder (Page):
    form_model = 'group'
    form_fields = ['Michael_index','Dwight_index','Jim_index']

    #print('select order')

    def is_displayed(self):
        return self.player.role() == 'Michael'

    def error_message(self,values):
        print('values is', values)
        if (values['Michael_index']+values['Dwight_index']+values['Jim_index'] != 6) | (values['Michael_index'] == values['Dwight_index']) :
            return 'Please make sure that each character is assigned to a distinct order.'
        else:
            for p in self.group.get_players():
                p.order = values[p.role()+'_index']
            
            players=self.group.get_players()
            players.sort(key=lambda p: p.order)
            
            role_by_order =[]
            for p in players:
                role_by_order.append(p.role())
                #print (', '.join(role_by_order))

            self.group.role_by_order = ', '.join(role_by_order)

class WaitForMichael (WaitPage):
    template_name = 'TreatmentB/MyWaitPage.html'
    form_model = 'player'
    form_fields = ['balance']

    def is_displayed(self):
        update_balances(self.player.group)
        return self.player.role() != 'Michael'



class Question_Player1 (Page):
    form_model = 'player'
    form_fields = ['Red_share','Green_share']
    

    def is_displayed(self):
        update_balances(self.player.group)
        return self.player.order == 1

    def before_next_page(self):
        update_balances(self.player.group)


class WaitForP1 (WaitPage):
    template_name = 'TreatmentB/MyWaitPage.html'
    form_model = 'player'
    form_fields = ['balance']

    def is_displayed(self):
        update_balances(self.player.group)
        return self.player.order != 1
    def before_next_page(self):
        update_balances(self.player.group)


class Question_Player2 (Page):
    form_model = 'player'
    form_fields = ['Red_share','Green_share']

    def is_displayed(self):
        update_balances(self.player.group)
        return self.player.order == 2
    def before_next_page(self):
        update_balances(self.player.group)

class WaitForP2 (WaitPage):
    template_name = 'TreatmentB/MyWaitPage.html'
    form_model = 'player'
    form_fields = ['balance']

    def is_displayed(self):
        update_balances(self.player.group)
        return self.player.order != 2
    def before_next_page(self):
        update_balances(self.player.group)

class Question_Player3 (Page):
    
    form_model = 'player'
    form_fields = ['Red_share','Green_share']

    def is_displayed(self):
        update_balances(self.player.group)
        return self.player.order == 3
    def before_next_page(self):
        update_balances(self.player.group)

class WaitForP3 (WaitPage):
    template_name = 'TreatmentB/MyWaitPage.html'
    form_model = 'player'
    form_fields = ['balance']

    def is_displayed(self):
        update_balances(self.player.group)
        return self.player.order != 3
    def before_next_page(self):
        update_balances(self.player.group)

class ResultsWaitPage(WaitPage):
    template_name = 'TreatmentB/MyWaitPage.html'
    def is_displayed(self):
        return True

    def after_all_players_arrive(self):
            for p in self.group.get_players():
                 p.payment = p.balance + p.Red_share*(self.subsession.true_state=="Red") + p.Green_share*(self.subsession.true_state=='Green')
                 if self.round_number == Constants.payoff_round:
                     p.payoff = p.payment
                 #print(p.balance)
                 #print(p.payment)
        
    wait_for_all_groups = False

class Results(Page):
    pass




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

page_sequence = [Instruction_0welcome, Instruction_1players, Instruction_2payment, Instruction_3interface, Instruction_4characters, Instruction_5balance, Instruction_6prices, Instruction_7questionsHints, Instruction_8orderAssignment,
                 MyWaitPage,
                 SelectOrder,
                 WaitForMichael,
                 Question_Player1,
                 WaitForP1, 
                 Question_Player2, 
                 WaitForP2,
                 Question_Player3, 
                 WaitForP3,
                 ResultsWaitPage, 
                 Results
                 ]

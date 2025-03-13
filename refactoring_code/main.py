import networkx as nx
import random
import json
import copy
from numpy import random
import itertools
from itertools import combinations
from tabulate import tabulate

import player_p
import board
#from player import Player, AI ,Monster
#from board import MARKET,Board,map_graph


########################################################################################
################################# MAIN CODE ############################################
########################################################################################

market = board.MARKET()
# print(market.deck[0].state())


# Initialize Players and Board
#P1 = Player(name='P1',current_position= 1,school="WOLF")
AI_player = player_p.AI(name='AI', current_position=12,school="BEAR")
AI_player_2 = player_p.AI(name='AI', current_position=1,school="WOLF")


## This Code sets up the Monster to play Against
Monster_1 = player_p.Monster("Hound", 10)
Monster_1.initiate_fight()

#AI_player.initiate_fight_monster(Monster_1)

# market.bank_print()
# market.buy_random(P1)
# market.bank_print()

# P1.get_combos()

board = board.Board(graph=board.map_graph, players=[AI_player_2,AI_player],market=market)
board.display()

# print("Valid Moves\n")
# cards = P1.get_valid_moves()
# for location in cards:
#     print(location)

board.start_game()
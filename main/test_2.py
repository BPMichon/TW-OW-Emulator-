import networkx as nx
import random
import json
import copy
from numpy import random
import itertools
from itertools import combinations
from tabulate import tabulate

import locations
import player_p
import board
import sampler
#from player import Player, AI ,Monster
#from board import MARKET,Board,map_graph


########################################################################################
################################# MAIN CODE ############################################
########################################################################################


# print(market.deck[0].state())


# Initialize Players and Board
P1 = player_p.Player(name='P1',current_position=1,school="WOLF")


market = board.MARKET()
AI_player = player_p.AI(name='AI_BEAR', current_position=12,school="BEAR")
board_g = board.Board(graph=locations.GAME_MAP, players=[AI_player],market=market)


AI_player_2 = player_p.AI(name='AI_WOLF', current_position=1,school="WOLF")


## This Code sets up the Monster to play Against
#Monster_1 = player_p.Monster("Hound", 10)
#Monster_1.initiate_fight()

#AI_player.initiate_fight_monster(Monster_1)

# market.bank_print()
# market.buy_random(P1)
# market.bank_print()

# P1.get_combos()


#board.display()

#board.display_monsters()
# all_possible_moves = AI_player.get_valid_moves(board)
# print(all_possible_moves)

# move = AI_player.choose_move(board)
# print(move)

# print("Valid Moves\n")
# cards = P1.get_valid_moves()
# for location in cards:
#     print(location)

##locations.visual()

#print(board_g.start_game(20,game_stats=True))

single_game = sampler.run_single_game()
#single_game = sampler.run_single_game_human()
print(single_game)
#stats_summary = sampler.sample_games(num_samples=2000)
#print(stats_summary)
#print(json.dumps(stats_summary, indent=4))


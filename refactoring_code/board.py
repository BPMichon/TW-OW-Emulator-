import networkx as nx
import random
import json
import copy
from numpy import random
import itertools
from itertools import combinations
from tabulate import tabulate
import player_p
#from player import Player, AI
from card import load_cards, Card



########################################################################################
############################### LOCATIONS CODE #########################################
########################################################################################
# We generate a graph using NetworkX library, this lets us easily define adjacency of nodes,
# aswell as quickly look up route between nodes using different graph algorithms

# Changed to using Data from json file, this means I dont need to store all the arrays in code

map_graph = nx.Graph()

with open("Game_Data/location.json", "r") as f:
    locations = json.load(f)

for location in locations:
    map_graph.add_node(location["id"], 
                       name=location["name"], 
                       terrain=location["terrain"],
                       school=location["school"],
                       ability=location["loc_ability"])

for location in locations:
    for neighbor in location["adjacents"]:
        map_graph.add_edge(location["id"], neighbor)





    


########################################################################################
########################### PLAYING BOARD CODE #########################################
########################################################################################
# Need to change this so it can handle x players

## Location Ability



class Board:
    def __init__(self, graph, players, market):
        self.graph = graph
        self.players = players
        self.market = market
    
    def display(self):
        for player in self.players:
            print(f"{player.name} is at {self.graph.nodes[player.current_position]['name']} ({self.graph.nodes[player.current_position]['terrain']})")
            
            # Creating a table for stats
            stats = [
                ["Level", player.level],
                ["Alchemy", player.Alchemy],
                ["Defense", player.Defense],
                ["Combat", player.Combat],
                ["Speciality", player.Speciality],
                ["Gold", player.gold],
                ["Cards", ", ".join(card.name for card in player.hand) if player.hand else "None"]
            ]
            
            print(tabulate(stats, tablefmt="fancy_grid"))  # Pretty table output
            print()  # Spacing
            
    def location_action(self,location_id,player :player_p.Player):
        ability = self.graph.nodes[location_id]["ability"]

        if ability == "COMBAT":
            ## Check Requirements
            if player.Combat <= player.level:
                player.UpStat("COMBAT")
                ## Raise UpStat(combat)
        elif ability == "DEFENSE":
            if player.Defense <= player.level:
                player.UpStat("DEFENSE")
                ## Raise UpStat(defense)
        elif ability == "ALCHEMY":
            if player.Alchemy <= player.level:
                player.UpStat("ALCHEMY")
                ## Raise UpStat(alchemy)
        elif ability == "SPECIALITY":
            if player.Speciality <= player.level:
                player.UpStat("SPECIALITY")
                ## Raise UpStat(speciality)
        else:
            print("location has no ability")

        

    # This is a basic adjacency moves
    # def get_valid_moves(self, player):
    #     return list(self.graph.neighbors(player.current_position))
    


    # def move(self, player, new_pos):
    #     if new_pos in player.get_valid_moves():
    #         player.current_position = new_pos
    #         return True
    #     return False

    def move(self,player : player_p.Player, move):

        for card in move[1]:
            player.discard_card(card)
        
        player.gold =- move[2]

        player.current_position = move[0]
        
    
    def start_game(self):
        while True:
            for player in self.players:

                self.display()

                if isinstance(player, player_p.AI):
                    print(f"{player.name}'s turn...")
                    print(f"AI has {len(player.hand)} cards")

                    
                    ## Movement Phase
                    ai_move = player.choose_move(self)
                    if ai_move is not None:
                        self.move(player, ai_move)

                    ## Action Phase

                    ## The player should be able to choose from a set of options at a location
                    ## Location Action
                    self.location_action(player.current_position,player)
                    ## Trail Quest
                    ## Gamble with other players??

                    ## Drawing Phase - Player Has to have 3 cards at this Step
                    if len(player.hand) >= 3:
                        pass
                    elif len(player.hand) == 0:
                        player.draw(3)
                    elif len(player.hand) == 1:
                        player.draw(2)
                    elif len(player.hand) == 2:
                        player.draw(1)
                    else:
                        #Do nothing John Snow
                        pass

                    print(f"AI has {len(player.hand)} cards")

                    ## Buying Phase
                    self.market.buy_random(player)
                    player.print_hand()

                    ## Current Win Condition
                    if player.level == 4:
                        return(1)

                elif isinstance(player, player_p.Player):
                    print(f"{player.name}'s turn! Choose a move:")

                    ## Need to see all possible moves, for all 3 possible variations
                    ## Valid Moves for spending 1 Location
                    ## Valid Moves for spending 1 Location and 1 Gold


                    moves = player.get_valid_moves(self)
                    

                    for i, move in enumerate(moves):
                        location_name = self.graph.nodes[move[0]]['name']
                        num_cards = len(move[1])
                        gold_cost = move[2]
                        
                        print(f"Move {i}:")
                        print(f"  ➜ Destination: {location_name}")
                        print(f"  ➜ Cost: {num_cards} card(s), {gold_cost} gold")
                        
                        if num_cards > 0:
                            print("  ➜ Discarded Cards:")
                            for card in move[1]:
                                print(f"    - {card}")

                        print("-" * 40)  # Separator for better readability

                    choice = 0
                    # Input loop to ensure valid move index
                    while True:
                        try:
                            choice = int(input("Enter move index: "))
                            if choice < 0 or choice >= len(moves):
                                print("Invalid index. Please enter a valid move index.")
                            else:
                                break  # Valid input, exit the loop
                        except ValueError:
                            print("Invalid input. Please enter a number.")

                    #choice = int(input("Enter move index: "))
                    self.move(player, moves[choice])




                    ## The player should be able to choose from a set of options at a location
                    ## Location Action
                    self.location_action(player.current_position,player)
                    ## Trail Quest
                    ## Gamble with other players??


                    ## Drawing Phase - Player Has to have 3 cards at this Step
                    if len(player.hand) >= 3:
                        pass
                    elif len(player.hand) == 0:
                        player.draw(3)
                    elif len(player.hand) == 1:
                        player.draw(2)
                    elif len(player.hand) == 2:
                        player.draw(1)
                    else:
                        #Do nothing John Snow
                        pass

                    ## Buying Phase
                    self.market.buy_random(player)
                    player.print_hand()

#######################################################################################
############################### Card Market ###########################################
#######################################################################################

# I need to initialise the card market, shuffle it and deal 6 cards, into the bank array
# When a card gets bought from the bank it moves up one space in the position
# There is discounts to the cards to the right of the bank

##Id rather Shuffle the deck, and persistently move the numbers around the game,
## This way its easier to keep track and limmit duplicates of cards


# with open("Game_Data/action_cards.json", "r") as f:
#     action_cards = json.load(f)

class MARKET:
    def __init__(self):
       
        self.deck = []  #Full shuffled deck
        self.bank = []  #6 cards in the bank

        self.deck = load_cards("Game_Data/action_cards.json")

        random.shuffle(self.deck)  #Shuffle deck

        #Deal 6 cards into the bank
        self.bank = [self.deck.pop() for _ in range(6)]

    def bank_print(self):
        for card in self.bank:
            print(card)
        print("")

    def buy_random(self, player: player_p.Player):
        
        random_card: Card = random.choice(self.bank)
        for _ in range(random_card.cost):
            player.discard_random()
        
        player.add_card(random_card)

        bought_index = self.bank.index(random_card)
        for i in range(bought_index, len(self.bank) - 1):
            self.bank[i] = self.bank[i + 1]
        
        if self.deck:
            self.bank[-1] = self.deck.pop()
        else:
            self.bank.pop()  # Remove last card if deck is empty
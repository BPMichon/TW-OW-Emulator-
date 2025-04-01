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
import matplotlib.pyplot as plt



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
                       ability=location["loc_ability"],
                       monster = [])

for location in locations:
    for neighbor in location["adjacents"]:
        map_graph.add_edge(location["id"], neighbor)


def visual():
    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(map_graph)  # Generates positions for the nodes

    # Determine color based on terrain
    node_colors = [
        "blue" if data["terrain"] == "SEA" else
        "green" if data["terrain"] == "FOREST" else
        "gray" if data["terrain"] == "MOUNTAIN" else
        "yellow"  # Default color for unknown terrain
        for _, data in map_graph.nodes(data=True)
    ]

    nx.draw(map_graph, pos, with_labels=True, node_color=node_colors, edge_color='gray', node_size=3000, font_size=10)
    #nx.draw_networkx_labels(map_graph, pos, labels={node: node for node in map_graph.nodes})

    plt.title("Game Map Graph (SEA = Blue, FOREST = Green, MOUNTAIN = Gray)")
    plt.show()

########################################################################################
########################### PLAYING BOARD CODE #########################################
########################################################################################
# Need to change this so it can handle x players

## Location Ability



class Board:
    def __init__(self, graph, players, market):
        self.graph = graph
        self.players = players
        self.market : MARKET = market
       
        self.monster_kills = 0

    def make_monster(self):
        monster = player_p.Monster("Hound", 10)
        return monster
        
    def randomise_monsters(self):
        terrains = ['FOREST','SEA','MOUNTAIN']
        for ter in terrains:
            self.spawn_monster(ter)
    
    def spawn_monster(self,terrain):
        forest_nodes = [x for x in self.graph.nodes if self.graph.nodes[x]["terrain"] == terrain]
        if forest_nodes:  # Ensure there's at least one valid node
            random_forest_location = random.choice(forest_nodes)
            self.graph.nodes[random_forest_location]["monster"].append(self.make_monster())

    def display_monsters(self):
        monster_data = []
        
        for node_id, node_data in self.graph.nodes.items():
            location_name = node_data.get("name", f"Unknown ({node_id})")
            monsters = node_data.get("monster", [])
            
            for monster in monsters:
                monster_data.append([monster.name, location_name, f"({node_id})"])
        
        if monster_data:
            print(tabulate(monster_data, headers=["Monster Name", "Location Name", "Node ID"], tablefmt="fancy_grid"))
        else:
            print("No monsters found in the world.")

    def is_monster(self,location_id):
        if self.graph.nodes[location_id]["monster"]:
            return True
        else:
            return False


    def display(self):
        board_stats = [
            ["Monster's Killed",self.monster_kills]
        ]

        print(tabulate(board_stats, tablefmt="fancy_grid"))

        for player in self.players:
            print(f"{player.name} is at ({player.current_position}){self.graph.nodes[player.current_position]['name']} ({self.graph.nodes[player.current_position]['terrain']})")
            
            
            stats = [
                ["Level", player.level],
                ["Alchemy", player.Alchemy],
                ["Defense", player.Defense],
                ["Combat", player.Combat],
                ["Speciality", player.Speciality],
                ["Gold", player.gold],
                ["Cards", ", ".join(card.name for card in player.hand) if player.hand else "None"],
                ["VICTORY POINTS",player.victory_points]
            ]
            
            print(tabulate(stats, tablefmt="fancy_grid")) 
            print()  
            
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
        elif ability == "TRAIL":
            player.gold += 1
            # You gain a Quest with a random location, of a specific terrain, when you visit that location
            # You gain 1 gold and get to flip a trail token (advantage for monster fight)
            pass
        elif ability == "SCHOOL":
            # Here you may pay gold to upgrade your ability, cost depends on the current level of the ability
            choices = []
            school = self.graph.nodes[location_id]["school"]
            
            if player.Alchemy != 4 and player.Alchemy + 1 <= player.gold:
                choices.append(("ALCHEMY", player.Alchemy + 1))
            
            if player.Defense != 4 and player.Defense + 1 <= player.gold:
                choices.append(("DEFENSE", player.Defense + 1))
            
            if player.Combat != 4 and player.Combat + 1 <= player.gold:
                choices.append(("COMBAT", player.Combat + 1))
            
            if player.Speciality != 4 and player.Speciality + 1 <= player.gold and player.school == school :
                choices.append(("SPECIALITY", player.Speciality + 1))
            
            ## Choose at random which one to level up,
            if choices:
                stat,cost = random.choice(choices)

                if stat == "ALCHEMY"  : player.Alchemy += 1
                elif stat == "DEFENSE": player.Defense += 1
                elif stat == "COMBAT" : player.Combat  += 1
                elif stat == "SPECIALITY" : player.Speciality += 1

                player.gold -= cost
        elif ability == "GAMBLE":
            if player.gold > 0:
                num = random.randint(0,2)
                if num == 0:
                    player.gold += 2
                else:
                    player.gold -= 1
            pass
        else:
            #print("location has no ability")
            pass

        

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
        player.visit_location(move[0])
        
    def explore(self,player:player_p.Player):

        rng = random.randint(0,8)

        if rng == 1:
            player.gold += 1
        elif rng == 2:
            player.gold += 2
        elif rng == 3: 
            player.gold += 3
        elif rng == 4:
            player.gold -= 1
        elif rng == 5:
            player.gold -= 2
        elif rng == 6:
            player.p3_draw_modifier = 1
        elif rng == 7:
            player.p3_draw_modifier = -1
        


    def generate_phase_2(self,player):
        ## Return all actions that the player can take 

        ## Can Always Explore
        valid_actions = ['explore']

        ## If a monster is on same location
        if self.is_monster(player.current_position):
            valid_actions.append('monster')

        ## If a unfought player is on same location

        ## If a skill is MAX we can meditate

        return valid_actions


    
    def start_game(self,turn_number=100,debug=False):

        ## Here I need to spawn in 3 monsters on the map
        self.randomise_monsters()


        turn = 0
        while True:
            if turn_number == turn:
                print("MAX TURN REACHED")
                self.display()
                #for player in self.players:
                    
                return

            if debug : print(f"CURRENT TURN: {turn}")
            if debug : self.display_monsters()
            turn+= 1
            for player in self.players:

                if debug : self.display()

                if isinstance(player, player_p.AI):
                    if debug: print(f"{player.name}'s turn...")
                    #print(f"AI has {len(player.hand)} cards")

                    ## Phase 1

                    ## Movement Phase -choose move might have heuristics for movement
                    ai_move = player.choose_move(self)
                    if ai_move is not None:
                        self.move(player, ai_move)
                        

                    ## Action Phase
                     ##Trigger Location Action



                    ## The player should be able to choose from a set of options at a location
                    ## Location Action
                    self.location_action(player.current_position,player)


                    ## Trail Quest
                    ## Gamble with other players??

                    ## Phase 2

                    ## Choose one of the four
                    ai_move = self.generate_phase_2(player)
                    ## Choose at Random from these, 
                    ## Future use Heuristic to determine based on future state

                    if len(ai_move) == 2:
                        ai_move_choice = ai_move[1]
                    else:
                        ai_move_choice = ai_move[0]



                    #ai_move_choice = ai_move[1]
                    if ai_move_choice == 'explore':
                        self.explore(player)
                    elif ai_move_choice == 'monster':
                        monster:player_p.Monster = self.graph.nodes[player.current_position]["monster"][0]
                        monster.initiate_fight()
                        fight = player.initiate_fight_monster(monster)
                        if fight == 1: ##Player WON
                            player.victory_points += 1
                            self.monster_kills += 1
                            ## Generate a new monster
                            self.graph.nodes[player.current_position]["monster"] = []
                            self.spawn_monster(self.graph.nodes[player.current_position]["terrain"])

                        elif fight == 2: ## Monster Won
                            #Player gains Nothing
                            pass

                

                    ## Drawing Phase - Player Has to have 3 cards at this Step
                    required_cards = 3 + player.p3_draw_modifier

                    while len(player.hand) < required_cards:
                        player.draw(1)
                    
                    ##Reset Draw Modifier
                    player.p3_draw_modifier = 0

                    #print(f"AI has {len(player.hand)} cards")

                    ## Buying Phase
                    self.market.buy_random(player)
                    #player.print_hand()

                    ## Current Win Condition
                    if player.victory_points == 4:
                        self.display()
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
class TRAIL:
    def __init__(self,player,board :Board):
        self.terrain = self.generate_terrain(player,board)

    
    def generate_terrain(self,player,board :Board):
        ## Randomly choose 0,1,2 
        rng_loc = random.randint(0,3)
        if rng_loc == 0:
            ## FILTER locations by board.graph  == "FOREST"
            ## if current location.terrain == "FOREST"
            ##      REMOVE from pool
            ## remove monster location on board.monsters[0].location
            ##
            ## pick random spot on map through this
            pass
        elif rng_loc == 1:
            pass
        elif rng_loc == 2:
            pass

        location = board.graph




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

    # def buy_random(self, player: player_p.Player):
        
    #     random_card: Card = random.choice(self.bank)
    #     for _ in range(random_card.cost):
    #         player.discard_random()
        
    #     player.add_card(random_card)

    #     bought_index = self.bank.index(random_card)
    #     for i in range(bought_index, len(self.bank) - 1):
    #         self.bank[i] = self.bank[i + 1]
        
    #     if self.deck:
    #         self.bank[-1] = self.deck.pop()
    #     else:
    #         self.bank.pop()  # Remove last card if deck is empty

    def buy_random(self, player: player_p.Player):
        # Filter the bank to only include cards the player can afford
        affordable_cards = [card for card in self.bank if len(player.hand) >= card.cost]

        if not affordable_cards:  # If no affordable cards, exit the function
            return  # Or raise an exception if needed

        # Pick a random affordable card
        random_card: Card = random.choice(affordable_cards)

        # Discard the required number of cards
        for _ in range(random_card.cost):
            player.discard_random()

        # Add the purchased card to the player's deck
        player.add_card(random_card)

        # Remove the bought card from the bank and shift remaining cards left
        bought_index = self.bank.index(random_card)
        for i in range(bought_index, len(self.bank) - 1):
            self.bank[i] = self.bank[i + 1]

        # Refill the bank from the deck if possible
        if self.deck:
            self.bank[-1] = self.deck.pop()
        else:
            self.bank.pop()  # Remove last card if the deck is empty
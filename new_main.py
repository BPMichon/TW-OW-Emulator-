import networkx as nx
import random
import json
import copy
from numpy import random
import itertools

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
    map_graph.add_node(location["id"], name=location["name"], terrain=location["terrain"])

for location in locations:
    for neighbor in location["adjacents"]:
        map_graph.add_edge(location["id"], neighbor)


########################################################################################
########################### PLAYING BOARD CODE #########################################
########################################################################################
# Need to change this so it can handle x players


class Board:
    def __init__(self, graph, players):
        self.graph = graph
        self.players = players
    
    def display(self):
        for player in self.players:
            print(f"{player.name} is at {self.graph.nodes[player.current_position]['name']} ({self.graph.nodes[player.current_position]['terrain']})")
            ##print(f"Gold: {player.gold} , Cards: {[card.name for card in player.cards]}")
            #p[player.state()
            print()
        
    
    # This is a basic adjacency moves
    # def get_valid_moves(self, player):
    #     return list(self.graph.neighbors(player.current_position))
    


    def move(self, player, new_pos):
        if new_pos in player.get_valid_moves():
            player.current_position = new_pos
            return True
        return False
    
    def start_game(self):
        while True:
            for player in self.players:

                self.display()

                if isinstance(player, AI):
                    print(f"{player.name}'s turn...")
                    ai_move = player.choose_move()
                    if ai_move is not None:
                        self.move(player, ai_move)

                elif isinstance(player, Player):
                    print(f"{player.name}'s turn! Choose a move:")

                    ## Need to see all possible moves, for all 3 possible variations
                    ## Valid Moves for spending 1 Location
                    ## Valid Moves for spending 1 Location and 1 Gold
                    ## Valid Moves for spending 2 Gold


                    moves = player.get_valid_moves()

                    for i, move in enumerate(moves):
                        print(f"{i}: Move to {self.graph.nodes[move]['name']}")

                    choice = int(input("Enter move index: "))
                    self.move(player, moves[choice])

########################################################################################
############################# CARD CODE ################################################
########################################################################################

# Do I need a class? Can i just use pointer to point where the card is?
## Loads Cards from JASON into an array


class Card:
    def __init__(self, name, colour, cost , terrain, ability,combos):
        self.name :str = name
        self.colour:str = colour
        self.cost:int = cost
        self.terrain:str = terrain
        self.ability:dict = ability
        self.combos:dict = combos

    def __repr__(self):
        return f"Card({self.name})"  # This defines how the object is printed

    #Returns list of colours that it combos with 
    def combo_colours():
        pass
    def state(self):
        # Create card details as key-value pairs
        details = [
            ("Name", self.name),
            ("Colour", self.colour),
            ("Cost", self.cost),
            ("Terrain", self.terrain),
            ("Ability", self.ability)
        ]

        # Find max width for box
        max_width = max(len(f"{key}: {value}") for key, value in details) + 2  # Padding

        # Top border
        print("+" + "-" * (max_width + 2) + "+")
        
        # Card details
        for key, value in details:
            line = f"| {key}: {value}"
            print(line.ljust(max_width + 3) + "|")  # Adjust padding
        
        # Bottom border
        print("+" + "-" * (max_width + 2) + "+")


def load_cards(path):

    card_array = []

    with open(path, "r") as f:
        cards = json.load(f)

        # Convert JSON data into Card objects
        for card_id, data in cards.items():
            card = Card(
                name=data["name"],
                colour=data["colour"],
                cost=data["cost"],
                terrain=data["terrain"],
                ability=data["ability"],
                combos=data["combos"]
            )
            card_array.append(card)

    return card_array   




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



#######################################################################################
########################### Card Combo Evaluation Class ###############################
#######################################################################################

class ItemGraph:
    def __init__(self, items, valid_pairs):
        self.graph = nx.DiGraph()  # Directed Graph
        self.graph.add_nodes_from(items)

        # Add valid edges (transitions)
        self.graph.add_edges_from(valid_pairs)

    def generate_sequences(self):
        sequences = []

        def dfs(path, visited):
            ## Adds current path to array
            sequences.append(path[:])

            ## If sequence is 7 we should return it, it cannot be longer 
            if len(path) == 7:  
                return

            ## Recursive function that finds all paths
            last = path[-1]
            for neighbor in self.graph.successors(last):
                if neighbor not in visited:
                    dfs(path + [neighbor], visited | {neighbor})

        # Start DFS from each item
        for start in self.graph.nodes:
            dfs([start], {start})

        return sequences
########################################################################################
############################    MONSTER CODE   #########################################
########################################################################################
class Monster:
    def __init__(self,name,health):
        self.name = name
        self.health = health
        self.hp_deck = []
        self.fight_deck = []
        self.alive = True

        for i in range(self.health):
            rnd_val = random.randint(3,6)
            self.hp_deck.append(rnd_val)
    
    def initiate_fight(self):
        self.fight_deck = copy.deepcopy(self.hp_deck)

    def play_top_card(self):
        if not self.fight_deck:
            return {}
        else:
            m = self.fight_deck.pop()
            return {"DMG": m}

    def is_alive(self):
        if len(self.fight_deck) < 1:
            self.alive = False
            return False
        else:
            return True



########################################################################################
#############################   PLAYER CODE    #########################################
########################################################################################

# Player Class stores all information About Player
class Player:
    def __init__(self,name, school, current_position, gold=2):
        self.name = name
        self.current_position = current_position
        self.hand = []
        self.discard = []
        self.deck = []
        self.gold = gold

        self.alive = True

        ## Create starter decks based on school
        if school == "WOLF":

            self.deck = load_cards("Game_Data/wolf_cards.json")
 
        elif school == "BEAR":

            self.deck = load_cards("Game_Data/bear_cards.json")
        
        else:
            pass

        random.shuffle(self.deck)  # Shuffle deck

        for i in range(3):
            card = self.deck.pop()
            self.hand.append(card)

    def get_valid_moves(self):
        return list(board.graph.neighbors(self.current_position))
    
    def state(self):
        for c in self.hand:
            c.state()

    def draw(self):
        pass

    def draw_in_combat(self,number_to_draw):

        ## Draw x number of cards, up to hand limmit 7
        for i in range(number_to_draw):

            if len(self.deck > 0):            
                if len(self.hand) < 7:
                    card = self.deck.pop()
                    self.hand.append(card)
                else:
                    return
            else:
                return
            
    def is_alive(self):
        if (len(self.deck) + len(self.hand)) < 1:
            self.alive = False
            return False
        else:
            return True
    


    # def initiate_fight_monster(self, monster:Monster):

    #     # Lifepool gets created, all cards get shuffled into the deck, hand stays as it is
    #     for card in self.discard:
    #         c = self.discard.pop()
    #         self.deck.append(c)

    #     random.shuffle(self.deck)
    #     # Cards in deck are treated as HP.

    #     # RN not implementing the trail, player goes first
    #     # player has to return a array of the cards he wants to play
    #     # RN we going to do this based if the player is an AI, he is going to play the maximum combo from his hand
        
    #     while (self.alive == True or monster.alive == True ):
           
    #         #We now have an array of all cnbinations
    #         combos = self.get_combos()

    #         chosen_combo = []
    #         for combo in combos:
    #             combo_vals = self.evaluate_combo_2(combo)
    #             ## This Heuristic will change depending on different AI, rn we just looking for the longest combo



    #         ## we calculate the effects and then the following occurs

    #         if monster.is_alive():
    #         # enemy turn
    #             pass

    #         if self.is_alive():
    #             pass




    ## This is too long, I want to break this up into Evaluating if a pair is valid, and then a function that given a sequence is vbalid calculates the combo
    def get_combos(self):
        combinations = list(itertools.permutations(self.hand,2 ))
        valid_pair = []
        for x in combinations:
            ##print(f"{x[0].name} and {x[1].name}")
            pair = self.is_combo_pair(x[0],x[1])
            if pair is not None:
                valid_pair.append(pair)



        # for combo in valid_pair:
        #     print("---- Combo ---")
        #     for x in combo:
        #         print(f"{x.name}")

        graph = ItemGraph(self.hand, valid_pair)
        valid_sequences = graph.generate_sequences()

        #print(valid_sequences)
        # for seq in valid_sequences:
        #     value = self.evaluate_combo_2(seq)
        #     print(seq)
        #     print(value)
        return valid_sequences
                

    def is_combo_pair(self, card_a , card_b):
        if card_b.colour in card_a.combos:
            return((card_a,card_b))
        else:
            return(None)
    
    def evaluate_combo_2(self, cards):
        if not cards:
            return {"DMG": 0, "DRAW": 0, "SHIELD": 0, "LENGTH": 0}

        damage = 0
        draw = 0
        shield = 0
        combo_length = len(cards)  # Since we know it's valid, LENGTH is just number of cards

        # Sum all card abilities
        for card in cards:
            damage += card.ability.get("DMG", 0)
            draw += card.ability.get("DRAW", 0)
            shield += card.ability.get("SHIELD", 0)

        # Sum all combo effects between adjacent cards
        for i in range(len(cards) - 1):
            combo_effects = cards[i].combos[cards[i + 1].colour]
            damage += combo_effects.get("DMG", 0)
            draw += combo_effects.get("DRAW", 0)
            shield += combo_effects.get("SHIELD", 0)

        return {"DMG": damage, "DRAW": draw, "SHIELD": shield, "LENGTH": combo_length}



    def evaluate_combo(cards: list):
        if not cards:
            return {"DMG": 0, "DRAW": 0, "SHIELD": 0, "LENGTH": 0}

        damage = 0
        draw = 0
        shield = 0
        combo_length = 1  # At least the first card is valid

        # Apply the first card's effects
        first_card = cards[0]
        damage += first_card.ability.get("DMG", 0)
        draw += first_card.ability.get("DRAW", 0)
        shield += first_card.ability.get("SHIELD", 0)

        # Iterate over the rest of the cards
        for i in range(1, len(cards)):
            prev_card = cards[i - 1]
            current_card = cards[i]

            # Check if the previous card has a valid combo with the current card
            if current_card.colour not in prev_card.combos:
                return {"DMG": 0, "DRAW": 0, "SHIELD": 0, "LENGTH": 0}  # Invalid combo

            # Apply the current card's effects
            damage += current_card.ability.get("DMG", 0)
            draw += current_card.ability.get("DRAW", 0)
            shield += current_card.ability.get("SHIELD", 0)
            combo_length += 1

            # Apply the combo effect (if valid)
            combo_effects = prev_card.combos[current_card.colour]
            damage += combo_effects.get("DMG", 0)
            draw += combo_effects.get("DRAW", 0)
            shield += combo_effects.get("SHIELD", 0)

        return {"DMG": damage, "DRAW": draw, "SHIELD": shield, "LENGTH": combo_length}
        

# Heuristic function (AI chases the player, currently only works for 1 player)
def heuristic(position, board):
    player_pos = board.players[0].current_position
    return -nx.shortest_path_length(board.graph, source=position, target=player_pos)  #Minimize distance

def discard(card):
    pass

# AI using state search
class AI(Player):
    
    def __init__(self, name, school, current_position, gold=2):
        super().__init__(name, school, current_position, gold)

        self.combat_heuristic = {
            "DMG" : 1.0,
            "SHIELD" : 0.5,
            "DRAW":  2,
            "LENGTH": 1.5,
        }

    def evaluate_combo(self, combo):
        """Calculate a weighted score for a given combo."""
        values = self.evaluate_combo_2(combo)  # Returns {"DMG": damage, "DRAW": draw, "SHIELD": shield, "LENGTH": length}
        score = sum(values[key] * self.combat_heuristic[key] for key in self.combat_heuristic)
        return score
    
    def choose_best_combo(self, combos):
        """Select the best combo based on the heuristic."""
        return max(combos, key=self.evaluate_combo)


    def choose_move(self):

        possible_moves = self.get_valid_moves()
        if not possible_moves:
            return None
        
        # Evaluate moves based on heuristic
        best_move = max(possible_moves, key=lambda pos: heuristic(pos, board))
        return best_move
    
    
    def initiate_fight_monster(self, monster:Monster):

        # Lifepool gets created, all cards get shuffled into the deck, hand stays as it is
        for card in self.discard:
            c = self.discard.pop()
            self.deck.append(c)

        random.shuffle(self.deck)
        # Cards in deck are treated as HP.

        # RN not implementing the trail, player goes first
        # player has to return a array of the cards he wants to play
        # RN we going to do this based if the player is an AI, he is going to play the maximum combo from his hand
        
        while (self.alive == True or monster.alive == True ):
           
            #We now have an array of all cnbinations
            combos = self.get_combos()

            chosen_combo = self.choose_best_combo(combos)
            print(chosen_combo)
            return




            ## we calculate the effects and then the following occurs

            if monster.is_alive():
            # enemy turn
                pass

            if self.is_alive():
                pass



########################################################################################
################################# MAIN CODE ############################################
########################################################################################

market = MARKET()
# print(market.deck[0].state())


# Initialize Players and Board
P1 = Player(name='P1',current_position= 1,school="WOLF")
AI_player = AI(name='AI', current_position=12,school="BEAR")

Monster_1 = Monster("Hound", 10)
AI_player.initiate_fight_monster(Monster_1)



P1.get_combos()

board = Board(graph=map_graph, players=[P1,AI_player])
board.start_game()
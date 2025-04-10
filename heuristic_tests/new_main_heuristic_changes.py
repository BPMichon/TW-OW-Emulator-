import networkx as nx
import random
import json
import copy
from numpy import random
import itertools
from itertools import combinations
from tabulate import tabulate



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
        return f"{self.colour} -> {', '.join(map(str, self.combos.keys()))}"
    
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
            return {"DMG":0}
        else:
            m = self.fight_deck.pop()
            return {"DMG": m}

    def take_dmg(self,number):
        for i in range(number):
            self.fight_deck.pop()

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
        self.school = school

        ## Attributes Used for Leveling
        self.level = 1

        self.Combat = 1
        self.Defense = 1
        self.Alchemy = 1
        self.Speciality = 1



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

    def UpStat(self,stat):
        if stat == "COMBAT":
            self.Combat +=1
        elif stat == "DEFENSE":#
            self.Defense +=1
        elif stat == "ALCHEMY":
            self.Alchemy +=1
        elif stat == "SPECIALITY":
            self.Speciality +=1
        elif stat == "SCHOOL":
            ## Here you pay GOLD to level up STATS
            ## Can only level up SPECIALITY if its your matching SCHOOL
            pass

        else:
            print("Incorect Stat")

        ## Check if LevelUp Occured (this should handle most cases, should not be possibl to level up twice with one stat increase)
        if self.level < min(self.Alchemy, self.Defense, self.Combat, self.Speciality):
            self.level += 1
        

    def terrain_hand(self):
        terrains = []
        card :Card
        for card  in self.hand:
            terrains.append(card.terrain)

        return terrains

    def print_hand(self):
        for card in self.hand:
            print(card)
        print("")

    def get_valid_moves(self):

        valid_moves = []
        neighbors = list(board.graph.neighbors(self.current_position))

        # Option 1: Move by discarding a matching terrain card (consider all valid terrain cards)
        for neighbor in neighbors:
            required_terrain = board.graph.nodes[neighbor]["terrain"]

            valid_terrain_cards = [card for card in self.hand if card.terrain == required_terrain]
            for card in valid_terrain_cards:
                valid_moves.append((neighbor, [card], 0))

        # Option 2: Move by discarding any two cards ( consider all 2-card combinations)
        # Sometimes we could get 2 of the same cards ( needs checking )
        if len(self.hand) >= 2:
            for card1, card2 in combinations(self.hand, 2):
                valid_moves.append((neighbor, [card1, card2], 0))   

        # Option 3: Move by discarding 1 card + 1 gold (consider all cards)
        if self.gold >= 1:
            for card in self.hand:
                for neighbor in neighbors:
                    valid_moves.append((neighbor, [card], 1))

        return sorted(valid_moves, key=lambda move: self.hand_strength_after(move[1]))
    
    def hand_strength_after(self, discarded_cards):
        """Heuristic: Measures hand strength after discarding specific cards"""
        remaining_hand = [card for card in self.hand if card not in discarded_cards]
        return sum(card.ability.get("DMG", 0) + card.ability.get("DRAW", 0) + card.ability.get("SHIELD", 0) for card in remaining_hand)
    
    def state(self):
        for c in self.hand:
            c.state()

    def add_card(self,card : Card):
        self.hand.append(card)
     

    ## We make sure deck cannot be under the certain amount and that it can be darwn from
    def draw(self, number=1):
        for i in range(number):

            # If deck is empty, shuffle the discard pile into the deck
            if not self.deck:
                # If the discard pile is also empty, stop drawing
                if not self.discard:
                    break

                # Shuffle the discard pile into the deck
                self.deck = self.discard[:]
                random.shuffle(self.deck)
                self.discard.clear()  # Clear the discard pile

            # Draw a card from the deck (if any cards are left)
            if self.deck:
                card = self.deck.pop()
                self.hand.append(card)

    def take_dmg(self, number):
        for i in range(number):
            if self.deck:
                # Discard from the deck if there are cards
                card = self.deck.pop()
                self.discard.append(card)
            elif self.hand:
                # If deck is empty, discard from hand if there are cards
                card = self.hand.pop()
                self.discard.append(card)
            else:
                # If both deck and hand are empty, the game is lost
                return 
    

    def move_to_discard(self, combo):
        # Iterate through each card in the combo
        for card in combo:
            if card in self.hand: 
                self.hand.remove(card)  
                self.discard.append(card)  
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
    
    # def card_strength(self,card):
    #     return sum(card.ability.get(effect, 0) for effect in ["DMG", "DRAW", "SHIELD"])

    def weakest_card(self, cards : list, terrain = "NONE"):

        def card_strength(card):
            return sum(card.ability.get(effect, 0) for effect in ["DMG", "DRAW", "SHIELD"])

        if terrain != "NONE":
            filtered_cards = [card for card in cards if card.terrain == terrain]
            if not filtered_cards:
                return None  # No matching terrain card found
        else:
            filtered_cards = cards

    # Return the weakest card based on its ability effects
        return min(filtered_cards, key=card_strength, default=None)

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

    def discard_card(self,card):
        self.hand.remove(card)  
        self.discard.append(card)  

    def discard_random(self):
        random_card :Card = random.choice(self.hand)
        self.discard_card(random_card)


   # Heuristic function (AI chases the player, currently only works for 1 player)
def heuristic(position, board):
    player_pos = board.players[0].current_position
    return -nx.shortest_path_length(board.graph, source=position, target=player_pos)  #Minimize distance

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

    ## We are changing this
    # def choose_move(self):

    #     possible_moves = self.get_valid_moves()
    #     if not possible_moves:
    #         return None
        
    #     # Evaluate moves based on heuristic
    #     best_move = max(possible_moves, key=lambda pos: heuristic(pos, board))
    #     return best_move
    
    def choose_move(self):
        ## tHIS WILL BE MY HEURISTICS CODE FOR CHOOSING FORM THE LIST OF POSSIBLE MOVES
        possible_moves = self.get_valid_moves()

        ## RN THE LIST GETS ORDERED WITH BEST MOVE ATOP, SO I JUST SELECT ONE MOVE
        if possible_moves:
            return possible_moves[0]
        else:
            return 

    def player_fight_turn(self,monster):

        print("Player Turn")
        combos = self.get_combos()

        # Choose best combo is based on the ai heuristic that is defined in the class
        chosen_combo = self.choose_best_combo(combos)
        chosen_combo_values = self.evaluate_combo_2(chosen_combo)
        # Apply card effects to enemy (currently just damage)
        # Take cards from hand to discard
        monster.take_dmg(chosen_combo_values["DMG"])
        self.move_to_discard(chosen_combo)
        self.draw(chosen_combo_values["DRAW"])

    def monster_fight_turn(self,monster):
        print("Monster Turn")

        card = monster.play_top_card()
        self.take_dmg(card["DMG"])

    def check_fight_status(self,monster):
        print(f"Current Player HP: {len(self.deck) + len(self.hand)}")
        print(f"Current Monster HP: {len(monster.fight_deck)}")

        if not monster.is_alive():
            print("Monster Lost")
            return True
        if not self.is_alive():
            print("Player Lost")
            return True
        return False

    
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
        
        while self.alive and monster.alive:
            self.player_fight_turn(monster)
            if self.check_fight_status(monster):
                break

            self.monster_fight_turn(monster)
            if self.check_fight_status(monster):
                break

########################################################################################
########################### PLAYING BOARD CODE #########################################
########################################################################################
# Need to change this so it can handle x players

## Location Ability



class Board:
    def __init__(self, graph, players):
        self.graph = graph
        self.players = players
    
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
            
    def location_action(self,location_id,player :Player):
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

    def move(self,player : Player, move):

        for card in move[1]:
            player.discard_card(card)
        
        player.gold =- move[2]

        player.current_position = move[0]
        
    
    def start_game(self):
        while True:
            for player in self.players:

                self.display()

                if isinstance(player, AI):
                    print(f"{player.name}'s turn...")
                    print(f"AI has {len(player.hand)} cards")

                    
                    ## Movement Phase
                    ai_move = player.choose_move()
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
                    market.buy_random(player)
                    player.print_hand()

                elif isinstance(player, Player):
                    print(f"{player.name}'s turn! Choose a move:")

                    ## Need to see all possible moves, for all 3 possible variations
                    ## Valid Moves for spending 1 Location
                    ## Valid Moves for spending 1 Location and 1 Gold


                    moves = player.get_valid_moves()
                    

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
                    market.buy_random(player)
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

    def buy_random(self, player: Player):
        
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

        
########################################################################################
################################# MAIN CODE ############################################
########################################################################################

market = MARKET()
# print(market.deck[0].state())


# Initialize Players and Board
#P1 = Player(name='P1',current_position= 1,school="WOLF")
AI_player = AI(name='AI', current_position=12,school="BEAR")
AI_player_2 = AI(name='AI', current_position=1,school="WOLF")


## This Code sets up the Monster to play Against
Monster_1 = Monster("Hound", 10)
Monster_1.initiate_fight()

#AI_player.initiate_fight_monster(Monster_1)

# market.bank_print()
# market.buy_random(P1)
# market.bank_print()

# P1.get_combos()

board = Board(graph=map_graph, players=[AI_player_2,AI_player])
board.display()

# print("Valid Moves\n")
# cards = P1.get_valid_moves()
# for location in cards:
#     print(location)

board.start_game()
import networkx as nx
import random
import json
import copy
from numpy import random
import itertools
from itertools import combinations
from tabulate import tabulate
from card import load_cards , Card, ItemGraph
#from main import 


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

    def get_valid_moves(self,board):

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
    
    def choose_move(self,board):
        ## tHIS WILL BE MY HEURISTICS CODE FOR CHOOSING FORM THE LIST OF POSSIBLE MOVES
        possible_moves = self.get_valid_moves(board)

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
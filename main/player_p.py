import networkx as nx
import random
import json
import copy
from numpy import random
import itertools
from itertools import combinations
from tabulate import tabulate
from card import load_cards , Card, ItemGraph
from collections import defaultdict

############################    MONSTER CODE   #########################################

class Monster:
    def __init__(self,name, difficulty):
        self.name = name
        #self.health = health
        self.hp_deck = []
        self.fight_deck = []
        self.alive = True
        self.difficulty = difficulty

        self.easy_hp =   [4,4, 3,3, 4,4, 5,5, 6,6,  5,5] #12
        self.medium_hp = [4,4, 3,3, 4,4, 5,5, 6,6,  5,5, 5,5, 3,3] #16
        self.hard_hp =   [4,4, 3,3, 4,4, 5,5, 6,6,  5,5, 5,5, 3,3,  6,6, 4,4] #20
    
    def initiate_fight(self):
        self.fight_deck = []

        if self.difficulty == "easy":
            self.fight_deck = copy.deepcopy(self.easy_hp)
        elif self.difficulty == "medium":
            self.fight_deck = copy.deepcopy(self.medium_hp)
        elif self.difficulty == "hard":
           self.fight_deck = copy.deepcopy(self.hard_hp)

        random.shuffle(self.fight_deck)

    def play_top_card(self):
        if not self.fight_deck:
            return {"DMG":0}
        else:
            m = self.fight_deck.pop()
            return {"DMG": m}

    def take_dmg(self, number):
        for i in range(number):
            if self.fight_deck:  # Check if the deck is not empty
                self.fight_deck.pop()
            else:
                break  # Stop if the deck is empty

    def is_alive(self):
        if len(self.fight_deck) < 1:
            self.alive = False
            return False
        else:
            return True

#############################   PLAYER CODE    #########################################

# Player Class stores all information About Player
class Player:
    def __init__(self,name, school, current_position, gold=2):
        ## Heuristic Measures
        self.visited_nodes = {}

        self.school = school
        self.name = name
        self.current_position = current_position
        self.hand = []
        self.discard = []
        self.deck = []
        self.gold = gold
        ## Win Condition 
        self.victory_points = 0
        ## Attributes Used for Leveling
        self.level = 1
        self.shield = 0
        self.alchemyCards = 0

        self.Combat = 1
        self.Defense = 1
        self.Alchemy = 1
        self.Speciality = 1

        self.CombatVP = False
        self.DefenseVP = False
        self.AlchemyVP = False
        self.SpecialityVP = False

        self.monster_wins = 0
        self.monster_attempts = 0

        self.won = False


        self.SpecialityUsed = False
        self.SpecialityNumber = 0

        self.alive = True

        self.p3_draw_modifier = 0

        ## Create starter decks based on school
        if school == "WOLF":

            self.deck = load_cards("Game_Data/wolf_cards.json")
 
        elif school == "BEAR":

            self.deck = load_cards("Game_Data/bear_cards.json")
        
        else:
            pass
        

        # random.shuffle(self.deck)  # Shuffle deck

        # ## On Game Start, player draws 3 cards.
        # for i in range(3):
        #     card = self.deck.pop()
        #     self.hand.append(card)

    def prepare_decks(self):
        random.shuffle(self.deck)  # Shuffle deck

        ## On Game Start, player draws 3 cards.
        for i in range(3):
            card = self.deck.pop()
            self.hand.append(card)


    def monster_fight_turn(self,monster:Monster):
        #print("Monster Turn")

        card = monster.play_top_card()
        self.take_dmg(card["DMG"])

    def check_fight_status(self,monster:Monster, debug = False):
        if debug: 
            print(" ")
            print(f"Current Player HP: {len(self.deck) + len(self.hand)}")
            print(f"Currnet Discard: {len(self.discard)}")
            print(f"Current Monster HP: {len(monster.fight_deck)}")

        if not monster.is_alive():
            #print("Monster Lost")
            return 1
        if not self.is_alive():
            #print("Player Lost")
            return 2
        
        return 0

    def valid_combo(self,cards):
        if not cards:
            return False

        # Iterate over the rest of the cards
        for i in range(1, len(cards)):
            prev_card = cards[i - 1]
            current_card = cards[i]

            # Check if the current card's colour is in the previous card's combo list
            if current_card.colour not in prev_card.combos:
                return False  # Invalid combo

        return True  # All pairs are valid combos
    def player_fight_turn_human(self,monster:Monster):
        ## Speciality Checks - Bear Speciality should be checked at the start of player turn.

        if self.school == "Bear" and self.shield == 0 and self.SpecialityUsed == False:
            
            #Progresiion for each speciality Level
            bear_progression = [ [0,0], [0,1], [1,1], [1,2], [2,2], [2,2] ]
            ## Bear Draws cards depending on his speciality level
            #self.draw(bear_progression[self.Speciality][1])
            self.draw_in_combat(bear_progression[self.Speciality][1])
            self.UpShield(bear_progression[self.Speciality][0])


            self.SpecialityUsed = True

        print("Your hand:")
        for i, card in enumerate(self.hand):
            print(f"{i}: {card}")

        # Ask for input
        #user_input = input("Enter the indices of the cards you want to play, separated by commas (e.g. 0,2,3): ")

        while True:

            try:
                # Prompt the user for input
                user_input = input("Enter the indices of the cards you want to play, separated by commas (e.g. 0,2,3) or nothing to skip: ")
                
                if user_input == "":
                    print("You played no cards")
                    selected_cards = None
                    break
                # Parse the indices
                indices = [int(i.strip()) for i in user_input.split(",")]

                

                # Construct the card combo from the hand using the indices
                selected_cards = [self.hand[i] for i in indices]

                # Check if the selected combo is valid
                # if not user_input:
                #     print("You played no cards")
                #     selected_cards = None
                #     break

                if self.valid_combo(selected_cards):
                    print("You played a valid combo:", selected_cards)
                    # Remove cards from hand or process as needed
                    break  # Exit the loop since the combo is valid
                else:
                    print("Invalid combination of cards. Please try again.")

            except ValueError:
                print("Invalid input format. Please enter a comma-separated list of numbers.")
            except IndexError:
                print("One or more indices are out of range. Please try again.")
       
        
        chosen_combo_values = self.evaluate_combo_2(selected_cards)
        # Apply card effects to enemy (currently just damage)
        # Take cards from hand to discard

        ## Simple implementation of alchemy
        ## cards, when you get one it adds damage to your next attack.

        if self.alchemyCards > 0:

            monster.take_dmg(chosen_combo_values["DMG"] + self.alchemyCards)
            self.alchemyCards = 0

        else:
            monster.take_dmg(chosen_combo_values["DMG"])


        ## Wolf Speciality
        if self.school == "Wolf" and len(selected_cards) > 3  and self.SpecialityUsed == False:
            #Progresiion for each speciality Level
            wolf_progression = [ [0,0], [1,0], [1,1], [1,2], [2,2], [2,2] ]
            ## Wolf deals damage based on Speciality.
            self.draw_in_combat(wolf_progression[self.Speciality][1])
            monster.take_dmg(wolf_progression[self.Speciality][0])

            self.SpecialityUsed = True
            
        # monster.take_dmg(chosen_combo_values["DMG"])

        if selected_cards : self.move_to_discard(selected_cards)
        self.UpShield(chosen_combo_values["SHIELD"])
        self.draw_in_combat(chosen_combo_values["DRAW"] + self.Combat)

    def initiate_fight_monster_human(self, monster:Monster, debug = False):

        # Reset Speciality (One speciality can be used per combat)
        self.SpecialityUsed = False
        ## Make Sure player is alive in combat
        self.alive = True
        monster.alive = True

        # Lifepool gets created, all cards get shuffled into the deck, hand stays as it is
        for card in reversed(self.discard):
            c = self.discard.pop()
            self.deck.append(c)

        random.shuffle(self.deck)

        monster.initiate_fight()
        # Cards in deck are treated as HP.

        # RN not implementing the trail, player goes first
        # player has to return a array of the cards he wants to play
        # RN we going to do this based if the player is an AI, he is going to play the maximum combo from his hand
        
        while self.alive and monster.alive:

            fight_status = 0
            fight_status = self.check_fight_status(monster,debug)

            self.monster_fight_turn(monster)
            fight_status = self.check_fight_status(monster,debug)
            
            if fight_status != 0:
                return fight_status

            self.player_fight_turn_human(monster)
            fight_status = self.check_fight_status(monster,debug)

            if fight_status != 0:
                return fight_status

    def hand_strength(self,hand):
        return sum(card.ability.get("DMG", 0) + card.ability.get("DRAW", 0) + card.ability.get("SHIELD", 0) for card in hand)
    
    def visit_location(self, location):
        if location in self.visited_nodes:
            self.visited_nodes[location] += 1  # Increment count if already visited
        else:
            self.visited_nodes[location] = 1   # First visit
            
    # Increases player shield, up to their Defense level
    def UpShield(self, amount):
        for _ in range(amount):
            if self.shield < self.Defense:
                self.shield += 1
            else:
                break  # Stop if shield is already at max

    def UpStat(self,stat):
        if stat == "COMBAT":
            ## Only Level up to 5
            if self.Combat == 5:
                #print("Max Combat")
                return
            self.Combat +=1
        elif stat == "DEFENSE":
            if self.Defense == 5:
                #print("Max Defence")
                return
            self.Defense +=1
            self.UpShield(1)
            
        elif stat == "ALCHEMY":
            if self.Alchemy == 5:
                #print("Max Alchemy")
                return
            self.Alchemy +=1

            if self.alchemyCards < 4:
                self.alchemyCards += 1

        elif stat == "SPECIALITY":
            if self.Speciality == 5:
                #print("Max Spelciality")
                return
            self.Speciality +=1
        else:
            print("Incorect Stat")

        ## Check if LevelUp Occured (this should handle most cases, should not be possibl to level up twice with one stat increase)
        if self.level < min(self.Alchemy, self.Defense, self.Combat, self.Speciality):
            self.level += 1
        
    ## Returns all terrains in hand
    def terrain_hand(self):
        terrains = []
        card :Card
        for card  in self.hand:
            terrains.append(card.terrain)

        return terrains


    ## Get all valid moves for the player, and returns a array
    def get_valid_moves_all(self,board):

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

        return valid_moves
    
    def get_valid_moves(self, board):
        valid_moves = []
        neighbors = list(board.graph.neighbors(self.current_position))

        # Store moves by destination
        moves_by_destination = defaultdict(list)

        # Option 1: Move by discarding a matching terrain card (1 card, 0 gold)
        for neighbor in neighbors:
            required_terrain = board.graph.nodes[neighbor]["terrain"]
            valid_terrain_cards = [card for card in self.hand if card.terrain == required_terrain]
            for card in valid_terrain_cards:
                moves_by_destination[neighbor].append((neighbor, [card], 0))

        # Option 2: Move by discarding any two cards (2 cards, 0 gold)
        if len(self.hand) >= 2:
            for neighbor in neighbors:
                for card1, card2 in combinations(self.hand, 2):
                    # Check if either card individually allows a move to this neighbor
                    can_card1_move = any(move[0] == neighbor and len(move[1]) == 1 and move[1][0] == card1 and move[2] == 0 for move in moves_by_destination[neighbor])
                    can_card2_move = any(move[0] == neighbor and len(move[1]) == 1 and move[1][0] == card2 and move[2] == 0 for move in moves_by_destination[neighbor])

                    if not can_card1_move and not can_card2_move:
                        moves_by_destination[neighbor].append((neighbor, [card1, card2], 0))

        # Option 3: Move by discarding 1 card + 1 gold (1 card, 1 gold)
        if self.gold >= 1:
            for neighbor in neighbors:
                for card in self.hand:
                    has_cheaper_card_move = any(m[0] == neighbor and len(m[1]) == 1 and m[1][0] == card and m[2] == 0 for m in moves_by_destination[neighbor])
                    if not has_cheaper_card_move:
                        moves_by_destination[neighbor].append((neighbor, [card], 1))

        # Flatten the dictionary of moves into a single list
        final_moves = []
        for _, moves in moves_by_destination.items():
            final_moves.extend(moves)

        return final_moves
        #return sorted(valid_moves, key=lambda move: self.hand_strength_after(move[1]))
    
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
        ## Make sure we take shield damage first before card damage. 
        for i in range(number):
            if self.shield > 0:
                self.shield -= 1

            elif self.deck:
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
    
    # This specifically moves all cards from hand e.g (you played the combo from your hand)
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

            if len(self.deck) > 0:            
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


    # Old Evaluation Function
    # def evaluate_combo(cards: list):
    #     if not cards:
    #         return {"DMG": 0, "DRAW": 0, "SHIELD": 0, "LENGTH": 0}

    #     damage = 0
    #     draw = 0
    #     shield = 0
    #     combo_length = 1  # At least the first card is valid

    #     # Apply the first card's effects
    #     first_card = cards[0]
    #     damage += first_card.ability.get("DMG", 0)
    #     draw += first_card.ability.get("DRAW", 0)
    #     shield += first_card.ability.get("SHIELD", 0)

    #     # Iterate over the rest of the cards
    #     for i in range(1, len(cards)):
    #         prev_card = cards[i - 1]
    #         current_card = cards[i]

    #         # Check if the previous card has a valid combo with the current card
    #         if current_card.colour not in prev_card.combos:
    #             return {"DMG": 0, "DRAW": 0, "SHIELD": 0, "LENGTH": 0}  # Invalid combo

    #         # Apply the current card's effects
    #         damage += current_card.ability.get("DMG", 0)
    #         draw += current_card.ability.get("DRAW", 0)
    #         shield += current_card.ability.get("SHIELD", 0)
    #         combo_length += 1

    #         # Apply the combo effect (if valid)
    #         combo_effects = prev_card.combos[current_card.colour]
    #         damage += combo_effects.get("DMG", 0)
    #         draw += combo_effects.get("DRAW", 0)
    #         shield += combo_effects.get("SHIELD", 0)

    #     return {"DMG": damage, "DRAW": draw, "SHIELD": shield, "LENGTH": combo_length}

    ## Similar to move_to_discrd function
    # def discard_card(self,card):
    #     self.hand.remove(card)  
    #     self.discard.append(card)  

    def discard_card(self, card : Card):
    # Find the card with the same ID in self.hand
        if self.hand:
            c : Card = None
            #print(self.hand)
            for c in self.hand:
                #print(c)
                if c.id == card.id:  # Assuming Card has a 'card_id' attribute
                    self.hand.remove(c)
                    self.discard.append(c)
                    return  # Exit once the card is found and removed
            raise ValueError(f"Card with ID {card.id} not found in hand")
        else:
            print("Empty?")

    def discard_random(self):
        if self.hand:
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
        if not combos:
            return None
        return max(combos, key=self.evaluate_combo)

    ## We are changing this
    # def choose_move(self):

    #     possible_moves = self.get_valid_moves()
    #     if not possible_moves:
    #         return None
        
    #     # Evaluate moves based on heuristic
    #     best_move = max(possible_moves, key=lambda pos: heuristic(pos, board))
    #     return best_move
    def basic_heuristic(self,move,board):
        location, cards_to_discard, gold_cost = move

        # 1. Prioritize unvisited locations
        visit_score = 1 if location not in self.visited_nodes else 0

        # 2. Simulate new hand after discarding cards
        future_hand = [card for card in self.hand if card not in cards_to_discard]

        #Test Hand Strength
        future_hand_score = self.hand_strength(future_hand)

        # 4. Penalize moves that reduce hand strength too much
        hand_penalty = -future_hand_score * 0.1  # Tune penalty weight

        # 5. Penalize expensive moves
        gold_penalty = -gold_cost * 0.1  # Tune cost weight

        # 6. Prioritize Monster Location 
        has_monster = board.graph.nodes[location]["monster"]
        monster_bonus = 2 if has_monster else 0

        return visit_score + hand_penalty + gold_penalty + monster_bonus
    
    ## This Heuristic Evaluated the current Player State, this will make it
    ##  so it is easier for us to evaluate how the player moves around the board

    # ## Finall Heuristic
    # def PlayerStateHeuristic(self, board):
    #     # Data-Colected Heuristics
    #     gold = 0.8 * self.gold
    #     hand = 1.2 * self.hand_strength(self.hand)
    #     victory_points = 3.0 * self.victory_points

    #     # Player - Stats
    #     stats = (
    #         (self.Alchemy    * 0.8) +
    #         (self.Combat     * 1.5) +
    #         (self.Defense    * 1.1) +
    #         (self.Speciality * 1.5)
    #     )

    #     # Monster Oriented Heuristic
    #     has_monster = board.graph.nodes[self.current_position]["monster"]
    #     monster = (2.0 * stats) if has_monster else 0.0

    #     # Reward for exploration of new nodes
    #     visit_score = 2.0 if self.current_position not in self.visited_nodes else 0.0
            
    #     # We clear visits if enough nodes were visited
    #     if len(self.visited_nodes) == 10:
    #         self.visited_nodes.clear()

    #     # Final Heuristic Score
    #     FinalScore = (
    #         gold +
    #         hand +
    #         monster +
    #         visit_score +
    #         victory_points
    #     )

    #     return FinalScore


    def PlayerStateHeuristic(self, board):

        # Data-Colected Heuristics
        gold = 0.9 * self.gold
        hand = 1 * self.hand_strength(self.hand)
        victory_points = 3.0 * self.victory_points

        # Player Stats
        stats = ((self.Alchemy    * 0.8) + (self.Combat     * 1.5) +
                 (self.Defense    * 1.1) + (self.Speciality * 1.5) )

        # Monster Oriented Heuristic
        has_monster = board.graph.nodes[self.current_position]["monster"]
        monster = (8) if has_monster else 0.0

        Score = gold + hand + victory_points + monster + stats
        return Score

    # def PlayerStateHeuristic(self, board):
    #     # Data-Colected Heuristics
    #     gold = 0.9 * self.gold
    #     hand = 1 * self.hand_strength(self.hand)
    #     victory_points = 3.0 * self.victory_points

    #     stats = (
    #         (self.Alchemy    * 0.8) + (self.Combat     * 1.5) +
    #         (self.Defense    * 1.1) + (self.Speciality * 1.5))

    #     # Monster Oriented Heuristic
    #     has_monster = board.graph.nodes[self.current_position]["monster"]
    #     monster = (3 * stats) if has_monster else 0.0
       
    #     Score = gold + hand + victory_points + monster
    #     return Score


    # def PlayerStateHeuristic(self,board):
    #     ## Different pouints should be weighted differently (GOLD IS IMPORTANT)

    #     gold        = 1.2 * self.gold 
    #     hand        = 1 * self.hand_strength(self.hand)
    #     #potions     = 0.5 * self.alchemyCards
    #     #shield      = 0.5 * self.shield

    #     has_monster = board.graph.nodes[self.current_position]["monster"]
    #     monster    = 2 if has_monster else 0

    #     #stats = (self.Alchemy * 0.1) + (self.Combat * 1) + (self.Defense * 1) + (self.Speciality * 0.2)
    #     #level = self.level * 3 #Level up is more important the higher you go

    #     visit_score = 3 if self.current_position not in self.visited_nodes else 0
    #     if len(self.visited_nodes) == 10 : self.visited_nodes.clear()

        

    #     FinalScore = gold + hand + monster + visit_score #+ stats #+ level #+ stats + level + visit_score + potions + shield
    #     return FinalScore


    ## This Will be
    def choose_move(self,board):

        best_move = None
        best_score = float('-inf')  # Higher is better

        ## THIS WILL BE MY HEURISTICS CODE FOR CHOOSING FORM THE LIST OF POSSIBLE MOVES
        possible_moves = self.get_valid_moves_all(board)

        ## RN THE LIST GETS ORDERED WITH BEST MOVE ATOP, SO I JUST SELECT ONE MOVE
        ## Lets Create a Heuristic for movement.
        
        if possible_moves:
             for move in possible_moves:
                score = self.basic_heuristic(move,board)
                if score > best_score:
                    best_score = score
                    best_move = move

                return best_move
        else:
            return 

    def player_fight_turn(self,monster:Monster):
        
        ## Speciality Checks - Bear Speciality should be checked at the start of player turn.

        if self.school == "BEAR" and self.shield == 0 and self.SpecialityUsed == False:
            
            #Progresiion for each speciality Level
            bear_progression = [ [0,0], [0,1], [1,1], [1,2], [2,2], [2,2] ]
            ## Bear Draws cards depending on his speciality level
            #self.draw(bear_progression[self.Speciality][1])
            self.draw_in_combat(bear_progression[self.Speciality][1])
            self.UpShield(bear_progression[self.Speciality][0])


            self.SpecialityUsed = True
            self.SpecialityNumber += 1


        #print("Player Turn")
        combos = self.get_combos()

        # Choose best combo is based on the ai heuristic that is defined in the class
        chosen_combo = self.choose_best_combo(combos)
        if chosen_combo == None:
            #print("No Cards Played")
            return
        
        chosen_combo_values = self.evaluate_combo_2(chosen_combo)
        # Apply card effects to enemy (currently just damage)
        # Take cards from hand to discard

        ## Simple implementation of alchemy
        ## cards, when you get one it adds damage to your next attack.

        if self.alchemyCards > 0:

            monster.take_dmg(chosen_combo_values["DMG"] + self.alchemyCards)
            self.alchemyCards = 0

        else:
            monster.take_dmg(chosen_combo_values["DMG"])


        ## Wolf Speciality
        if (self.school == "WOLF") and ( len(chosen_combo) > 2 )  and  (self.SpecialityUsed == False ):
            #Progresiion for each speciality Level
            wolf_progression = [ [0,0], [1,0], [1,1], [1,2], [2,2], [2,2] ]
            ## Wolf deals damage based on Speciality.
            self.draw_in_combat(wolf_progression[self.Speciality][1])
            monster.take_dmg(wolf_progression[self.Speciality][0])

            self.SpecialityUsed = True
            self.SpecialityNumber += 1
            
        # monster.take_dmg(chosen_combo_values["DMG"])

        self.move_to_discard(chosen_combo)
        self.UpShield(chosen_combo_values["SHIELD"])
        self.draw_in_combat(chosen_combo_values["DRAW"] + self.Combat)

    def initiate_fight_monster(self, monster:Monster, debug = False):

        # Reset Speciality (One speciality can be used per combat)
        self.SpecialityUsed = False
        ## Make Sure player is alive in combat
        self.alive = True
        monster.alive = True

        # Lifepool gets created, all cards get shuffled into the deck, hand stays as it is
        for card in self.discard:
            c = self.discard.pop()
            self.deck.append(c)

        random.shuffle(self.deck)
        monster.initiate_fight()
        # Cards in deck are treated as HP.

        # RN not implementing the trail, player goes first
        # player has to return a array of the cards he wants to play
        # RN we going to do this based if the player is an AI, he is going to play the maximum combo from his hand
        
        while self.alive and monster.alive:

            fight_status = 0
            fight_status = self.check_fight_status(monster,debug)

            self.monster_fight_turn(monster)
            fight_status = self.check_fight_status(monster,debug)
            
            if fight_status != 0:
                return fight_status

            self.player_fight_turn(monster)
            fight_status = self.check_fight_status(monster,debug)

            if fight_status != 0:
                return fight_status
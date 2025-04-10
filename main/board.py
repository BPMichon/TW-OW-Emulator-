import networkx as nx
import random
from numpy import random
from tabulate import tabulate
import player_p
from card import load_cards, Card
import copy


########################################################################################
########################### PLAYING BOARD CODE #########################################
########################################################################################

## Main Class which handles players, where they move around the map


class Board:
    def __init__(self, graph, players, market):
        self.graph = graph
        self.players = players
        self.market : MARKET = market
       
        self.monster_kills = 0
        self.stats = {"GameWon" : 0, "MonstersKilled" : 0, "TurnTaken" : 0}

    # Returns a Monster to generate, UPDATE to have 3 dificulties of monsters
    def make_monster(self):
        monster = player_p.Monster("Hound", 10)
        return monster
    
    # Randomise the Spawns of Monsters
    def randomise_monsters(self):
        terrains = ['FOREST','SEA','MOUNTAIN']
        for ter in terrains:
            self.spawn_monster(ter)

    # Creates a monster in a specific terrain
    def spawn_monster(self,terrain):
        forest_nodes = [x for x in self.graph.nodes if self.graph.nodes[x]["terrain"] == terrain]
        if forest_nodes:  # Ensure there's at least one valid node
            random_forest_location = random.choice(forest_nodes)
            self.graph.nodes[random_forest_location]["monster"].append(self.make_monster())

    # DisplaYS ALL alive monsters
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

    # Checks if a location has a monster
    def is_monster(self,location_id):
        if self.graph.nodes[location_id]["monster"]:
            return True
        else:
            return False

    # Prints out GAME_STATE this lets us see game stats aswell
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
    
    # Each Location has a specific Ability that could be desireable
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
        elif ability == "POTION":

            if player.alchemyCards < 4:
                player.alchemyCards += 1

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

    # Moves the player to new location, discards cards 
    def move(self,player : player_p.Player, move,debug=False):
        
        ##There is no valid moves
        if move == None:
            return
        
        #print('cardss')
        #print(move[1])
        for card in move[1]:
            player.discard_card(card)
        
        player.gold =- move[2]

        ##Update visited locations after we have left them
        player.visit_location(player.current_position)
        player.current_position = move[0]
        if debug : print(f"AI Moved to ({move[0]}) {self.graph.nodes[move[0]]['name']} ")
        # player.visit_location(move[0])

    ## Uses the explore functionality of the boardgame  
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
        
    # Generates all valid action for phase 2
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

    # def simulate_move(self, player, max_depth, current_depth=0):
    #     # Base case: if we've reached the maximum depth, return the heuristic score
    #     if current_depth == max_depth:
    #         return player.PlayerStateHeuristic(board=self), None

    #     # List of all valid moves at the current state
    #     AI_MOVES = player.get_valid_moves_all(board=self)

    #     best_score = float('-inf')
    #     best_move = None

    #     for move in AI_MOVES:
    #         # Copy the current player state to simulate the move
    #         player_copy : player_p.AI = copy.deepcopy(player)
    #         # Make the move and evaluate
    #         self.move(player_copy, move)

    #         # Now take a location action (or perform any other action you want to simulate)
    #         # (You can add logic for a location action here if needed, for example)
    #         player_copy.visit_location(player_copy.current_position)

    #         # Simulate the next move (if depth allows)
    #         score, _ = self.simulate_move(player_copy, max_depth, current_depth + 1)

    #         if score > best_score:
    #             best_score = score
    #             best_move = move

    #     return best_score, best_move

    # def get_best_move(self, player, max_depth=1):
    #     best_score, best_move = self.simulate_move(player, max_depth)

    #     # Execute the best move
    #     if best_move:
    #         self.move(player, best_move, True)

    #     return best_move




    ## The Board Game starts
    def start_game(self,turn_number=100,debug=False,game_stats = False):

        ## Here I need to spawn in 3 monsters on the map
        self.randomise_monsters()


        turn = 0
        while True:
            if turn_number == turn:
                #print("MAX TURN REACHED")
                if debug: self.display()
                #for player in self.players:
                
                if game_stats:
                    #self.stats = {"GameWon" : 0, "MonstersKilled" : 0, "TurnTaken" : 0}
                    self.stats["MonstersKilled"] = self.monster_kills
                    self.stats["TurnTaken"] = turn
                    return self.stats
                else:
                    return (0)

            if debug : print(f"CURRENT TURN: {turn}")
            if debug : self.display_monsters()
            turn += 1
            for player in self.players:

                if debug : self.display()

                if isinstance(player, player_p.AI):
                    if debug: print(f"{player.name}'s turn...")
                    #print(f"AI has {len(player.hand)} cards")

                    ## Phase 1

                    ## Movement Phase -choose move might have heuristics for movement
                    # ai_move = player.choose_move(self)
                    # if ai_move is not None:
                    #     self.move(player, ai_move)

                    ## Heuristic Multiple Step Search Approach
                    ## I will simulate the action of going to a location and taking a location action
                    ## Then returning back to see the highest result

                    # ## List of all valid Moves
                    def simulate_move(player :player_p.Player, depth, current_depth):
                        
                        if current_depth == depth:
                            return 0, None  
                        # Return score and chosen_move when depth is reached
                        
                        chosen_move = None
                        move_score = -float('inf')  
                        # Start with the worst possible score
                        
                        AI_MOVES = player.get_valid_moves_all(board=self)
                        if AI_MOVES:
                            for move in AI_MOVES:
                                # Copy the current Player State
                                player_copy = copy.deepcopy(player)

                                # Apply the move and execute the action
                                self.move(player_copy, move)
                                self.location_action(player_copy.current_position, player_copy)

                                # Evaluate the resulting board state (heuristic evaluation)
                                score = player_copy.PlayerStateHeuristic(board=self)
                                
                                # Recurse into the next level
                                next_score, _ = simulate_move(player_copy, depth, current_depth + 1)
                                
                                # Combine the current move's score with the result from deeper levels
                                total_score = score + next_score

                                # If this move gives a better score, update chosen_move
                                if total_score > move_score:
                                    move_score = total_score
                                    chosen_move = move

                            return move_score, chosen_move
                        else:
                            return 0 , None
                    # def simulate_move(player,depth,currentdepth):
                        
                    #     if currentdepth == depth:
                    #         return
                        

                    #     chosen_move = None
                    #     move_score = 0
                        

                    #     AI_MOVES = player.get_valid_moves_all(board=self)
                    #     for move in AI_MOVES:
                    #         ## I will Copy the current Player State,

                    #         playerCopy = copy.deepcopy(player)

                    #         #print("Player Hand")
                    #         #print(playerCopy.hand)
                            
                    #         self.move(playerCopy,move)
                    #         self.location_action(playerCopy.current_position,playerCopy)

                    #         score = playerCopy.PlayerStateHeuristic(board=self)
                            
                    #         ##At this point we go one more deep into choices, 
                            

                    #         if score > move_score:
                    #             move_score = score
                    #             chosen_move = move

                    #         return move_score , chosen_move

                    # Simple Logick taht make sthe player always use their hand to move

                    ## A flag that will let us determine, if we wnat to fight the enemy
                    ## Based on current player Strength + Cards
                    FIGHT = False

                    while len(player.hand) > 0:
                        
                        ## First Check if the Monster is Here

                        if self.is_monster(player.current_position):
                            playerStrength = (len(player.hand) * 3) + ( len(player.discard) + len(player.deck) )
                            ## Arbitary Value RN, but it lets us decide if a monster is on the section
                            if playerStrength > 20:
                                FIGHT = True
                                break

                        move_score,chosen_move = simulate_move(player,3,0)
                        ##Finaly we have a correct move to make
                        # chosen_move = self.get_best_move(player,1)
                        #print("Actual Move")
                        #print(chosen_move)
                        if chosen_move == None:
                            break

                        self.move(player,chosen_move,False)
                        self.location_action(player.current_position,player)
                    
                    #print("Finished Moving")

                    ## Action Phase
                     ##Trigger Location Action



                    ## The player should be able to choose from a set of options at a location
                    ## Location Action
                    


                    ## Trail Quest
                    ## Gamble with other players??

                    ## Phase 2

                    ## Choose one of the four
                    ai_move = self.generate_phase_2(player)
                    ## Choose at Random from these, 
                    ## Future use Heuristic to determine based on future state

                    if len(ai_move) == 2 and FIGHT == True:
                        ai_move_choice = ai_move[1]
                        #print("FIGHT MONSTER")
                    else:
                        ai_move_choice = ai_move[0]
                        #print("EXPLORE")



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

                
                    ## Need to reset cards at this step, if a card is weak at a certain threshhold, it should instead be replaced
                    while len(player.hand) > 3:
                        player.discard_card(player.weakest_card(player.hand))

                    ## Drawing Phase - Player Has to have 3 cards at this Step
                    required_cards = 3 + player.p3_draw_modifier

                    while len(player.hand) < required_cards:
                        player.draw(1)
                    
                    ## Reset Draw Modifier
                    player.p3_draw_modifier = 0

                    #print(f"AI has {len(player.hand)} cards")

                    ## Buying Phase
                    self.market.buy_random(player)
                    #player.print_hand()

                    ## Current Win Condition
                    if player.victory_points == 5:
                        if debug : self.display()
                        if game_stats:

                            #self.stats = {"GameWon" : 0, "MonstersKilled" : 0, "TurnTaken" : 0}
                            self.stats["MonstersKilled"] = self.monster_kills
                            self.stats["TurnTaken"] = turn
                            self.stats["GameWon"] = 1

                            return self.stats
                        else:
                            return(1)

                elif isinstance(player, player_p.Player):
                    print(f"{player.name}'s turn! Choose a move:")

                    PHASE_1 = False
                    PHASE_2 = False
                    PHASE_3 = False

                    PHASE_1 = True
                    while PHASE_1:

                        #"Does the player want to keep moving"
                        while True:
                            player_input = input("MOVE? (Y/N): ").strip().lower()
                            if player_input == "n":
                                PHASE_1 = False
                                break  # Exit the loop as a valid input is received
                            elif player_input == "y":
                                break  # Exit the loop as a valid input is received
                            else:
                                print("Invalid input. Please enter 'Y' or 'N'.")

                        if not PHASE_1:
                            break
                        moves = player.get_valid_moves(self)

                        # for i, move in enumerate(moves):
                        #     location_name = self.graph.nodes[move[0]]['name']
                        #     num_cards = len(move[1])
                        #     gold_cost = move[2]
                            
                        #     print(f"Move {i}:")
                        #     print(f"  ➜ Destination: {location_name}")
                        #     print(f"  ➜ Cost: {num_cards} card(s), {gold_cost} gold")
                            
                        #     if num_cards > 0:
                        #         print("  ➜ Discarded Cards:")
                        #         for card in move[1]:
                        #             print(f"    - {card}")

                        #     print("-" * 40)  # Separator for better readability

                        print(f"\n{player.name}'s Hand:")
                        if player.hand:
                            for card in player.hand:
                                print(f"  - {card}")  # Assuming card has a __str__ method
                        else:
                            print("  - (No cards in hand)")
                            break

                        grouped_moves = {}
                        card_width = 20  # Adjust this width as needed to accommodate your longest card string
                        gold_width = 5   # Width for the Gold column
                        index_width = 3  # Width for the move index

                        for i, move in enumerate(moves):
                            location_id = move[0]
                            location_name = self.graph.nodes[location_id]['name']
                            num_cards = len(move[1])
                            gold_cost = move[2]
                            discarded_cards_str = ", ".join(map(str, move[1])) if num_cards > 0 else ""

                            if location_name not in grouped_moves:
                                grouped_moves[location_name] = []

                            move_info = f"{str(i).rjust(index_width)}: Gold: {str(gold_cost).ljust(gold_width)}, Cards: {{{discarded_cards_str.ljust(card_width)}}}"
                            grouped_moves[location_name].append(move_info)

                        for location, move_options in grouped_moves.items():
                            print(f"{location.upper()}:")
                            for option in move_options:
                                print(option)
                            print("-" * (index_width + 2 + gold_width + 8 + card_width + 2)) # Adjusted separator width

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

                    ## PHASE 2


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

########################################################################
########################### TRAIL ######################################
########################################################################
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
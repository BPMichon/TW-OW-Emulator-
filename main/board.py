import networkx as nx
import random 
#from numpy import random
from tabulate import tabulate
import player_p 
from card import load_cards, Card
import copy


########################################################################################
########################### PLAYING BOARD CODE #########################################
########################################################################################

## Main class which handles player objects
class Board:
    def __init__(self, graph, players, market):
        self.graph = graph
        self.players = players
        self.market : MARKET = market
       
        self.monster_kills = 0
        #self.stats = {"GameWon" : 0, "MonstersKilled" : 0, "TurnTaken" : 0}
        self.stats = []

    ## Generates a Monster at a Specific Difficulty
    def make_monster(self,difficulty):
        monster = player_p.Monster(f"{difficulty} Monster",difficulty=difficulty)
        return monster
    
    ## Randomise the Spawns of Monsters
    def randomise_monsters(self):
        terrains = ['FOREST','SEA','MOUNTAIN']
        for ter in terrains:
            self.spawn_monster(ter,"easy")

    ## Creates a monster in a specific terrain
    def spawn_monster(self,terrain,difficulty):
        forest_nodes = [x for x in self.graph.nodes if self.graph.nodes[x]["terrain"] == terrain]
        if forest_nodes:  # Ensure there's at least one valid node
            random_forest_location = random.choice(forest_nodes)
            self.graph.nodes[random_forest_location]["monster"].append(self.make_monster(difficulty=difficulty))

    ## DisplaYS ALL alive monsters
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

    ## Checks if a location has a monster
    def is_monster(self,location_id):
        if self.graph.nodes[location_id]["monster"]:
            return True
        else:
            return False

    ## Prints out GAME_STATE this lets us see game stats aswell
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
                ["VICTORY POINTS", player.victory_points],
                ["HP ()", len(player.hand) + len(player.deck) + len(player.discard)]
            ]
            
            print(tabulate(stats, tablefmt="fancy_grid")) 
            print()  
    
    ## Location actions that can be taken when visiting locations
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

                if stat == "ALCHEMY"  :
                    player.Alchemy += 1
                    #print("Leveled up Alchemy!")
                elif stat == "DEFENSE":
                    player.Defense += 1
                    #print("Leveled up Defense!")
                elif stat == "COMBAT" :
                    player.Combat  += 1
                    #print("Leveled up Combat!")
                elif stat == "SPECIALITY" :
                    player.Speciality += 1
                    #print("Leveled up Speciality!")

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


    # Moves the player to new location
    def move(self,player : player_p.Player, move, debug=False):
        
        ## There is no valid moves
        if move == None:
            return False
        
        for card in move[1]:
            player.discard_card(card)
        
        player.gold =- move[2]

        ## Update visited locations after we have left them
        player.visit_location(player.current_position)

        player.current_position = move[0]
        if debug : print(f"{player.name} Moved to ({move[0]}) {self.graph.nodes[move[0]]['name']} ")
        

    ## Uses the explore functionality of the boardgame  
    def explore(self, player:player_p.Player, RNG= True, choice = 0):
        if RNG:
            rng = random.randint(1,10)
        else:
            rng = choice

        ## The following effects alter the player gold amounts 
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

        ## The following effects alter the amount cards drawn in phase 3
        elif rng == 6:
            player.p3_draw_modifier = 1
        elif rng == 7:
            player.p3_draw_modifier = -1

        ## The following may raise your attribute by 1

        elif rng == 8:
            ## How the game logick works, if you have to pay a cost, 
            ## and you do not have the required amount you still get the bonus
            player.discard_random()
            player.Alchemy += 1

        elif rng == 9:
            player.Alchemy -= 1

    # We take the current player state, for each possible outrcome in the explore actions we then 
    def explore_evaluation(self, player):

        score = 0

        ## This way we go through each possibility of the random roll, and weight it by its proibability
        ## With 10 items the weighting is P = 0.1.

        for i in range(0,10):

            player_copy: player_p.AI = copy.deepcopy(player)
            self.explore(player_copy,RNG=False,choice=i)
            
            state_score = player_copy.PlayerStateHeuristic(self)
            score += ( state_score/9 )

        #print(f"Exploration: {score}")
        return score
    

    # We use this to evaluate if player combat is possible at this section
    def combat_evaluation(self, player, difficulty):

        ### Need to calculate the win ratio simulation for the player 
        player_won = 0
        player_lost = 0
        
        for i in range(0,100):

            ## This makes the monster ready to fight.
            monster = player_p.Monster("SampleMonster",difficulty=difficulty)
            monster.initiate_fight()
            player_copy :player_p.AI = copy.deepcopy(player)
            fight = player_copy.initiate_fight_monster(monster)
        
            if fight == 1: ## Player WON
                player_won += 1

            elif fight == 2: ## Monster Won
               player_lost += 1

        ## Evaluate the Winning State
        player_copy:player_p.AI = copy.deepcopy(player)

        player_copy.victory_points += 1
        player_copy.gold += 2

        PlayerWon = player_copy.PlayerStateHeuristic(self)

        ## Evaluate the Losing State

        PlayerLost = player.PlayerStateHeuristic(self)

        ## Combine the Scores
        
        #print(f"PlayerWon: {player_won}, PlayerLost: {player_lost}")
        FinalScore = ( PlayerWon * (player_won / (player_won + player_lost))) + ( PlayerLost * (player_lost / (player_lost + player_won)))
        #print(f"Combat Score: {FinalScore}")
        return FinalScore

    def meditate_evaluation(self, player : player_p.AI):

        player_copy = copy.deepcopy(player)

        if( 
        (player.Combat == 5 and not player.CombatVP) or
        (player.Defense == 5 and not player.DefenseVP ) or 
        (player.Alchemy == 5 and not player.AlchemyVP) or 
        (player.Speciality == 5 and not player.SpecialityVP) ):

            player_copy.victory_points += 1
            score = player_copy.PlayerStateHeuristic(self)
            return score
            
        else:
            return 0
        

    def simulate_move(self, player :player_p.Player, depth, current_depth):
                        
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
                player_copy : player_p.AI = copy.deepcopy(player)

                # Apply the move and execute the action
                self.move(player_copy, move)
                self.location_action(player_copy.current_position, player_copy)

                # Evaluate the resulting board state (heuristic evaluation)
                score = player_copy.PlayerStateHeuristic(board=self)
                
                # Recurse into the next level
                next_score, _ = self.simulate_move(player_copy, depth, current_depth + 1)
                
                # Combine the current move's score with the result from deeper levels
                total_score = score + next_score

                # If this move gives a better score, update chosen_move
                if total_score > move_score:
                    move_score = total_score
                    chosen_move = move

            return move_score, chosen_move
        else:
            return 0 , None


    ## The Board Game starts
    def start_game(self,turn_number=100,debug=False,game_stats = False):

        ## Populates the game board with 3 monsters
        self.randomise_monsters()

        for player_ in self.players:
            player_.prepare_decks()

        turn = 0
        while True:
            if turn_number == turn:
                #print("MAX TURN REACHED")
                if debug: self.display()
                #for player in self.players:
                
                if game_stats:

                    for _player in self.players:

                        n_stats = {

                            "Player"         : _player,
                            "GameWon"        : _player.won,
                            "MonsterKills"   : _player.monster_wins,
                            "MonsterAttempts": _player.monster_attempts,
                            "Victorypoints"  : _player.victory_points,
                            "Turn"           : turn,
                            "Combat"         : _player.Combat,
                            "Alchemy"        : _player.Alchemy,
                            "Defence"        : _player.Defense,
                            "Speciality"     : _player.Speciality,
                            "SpecialityCount": _player.SpecialityNumber
                        }
            
                        self.stats.append(n_stats)
                        #print("Number: ", _player.SpecialityNumber)
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
                    

                    ai_move_choice = None

                    while len(player.hand) > 0:
                        
                        if self.is_monster(player.current_position):
                            
                            monster:player_p.Monster = self.graph.nodes[player.current_position]["monster"][0]

                            combat_score = self.combat_evaluation(player, monster.difficulty)
                            explore_score = self.explore_evaluation( player )
                            meditate_score = self.meditate_evaluation( player )

                            if combat_score > explore_score and combat_score > meditate_score:
                                ai_move_choice = "monster"
                                break
                            else:
                                pass


                        move_score,chosen_move = self.simulate_move(player, 3, 0)
                        if chosen_move == None:
                            break

                        self.move(player,chosen_move,False)
                        self.location_action(player.current_position,player)
                        
                        explore_score = self.explore_evaluation( player )
                        meditate_score = self.meditate_evaluation( player )

                        if explore_score > meditate_score:
                            ai_move_choice = "explore"
                        else:
                            ai_move_choice = "meditate"
                    
                    
                    if ai_move_choice == 'explore':

                        self.explore(player)

                    elif ai_move_choice == 'monster':
                        monster:player_p.Monster = self.graph.nodes[player.current_position]["monster"][0]
                        monster.initiate_fight()
                        new_difficulty = None

                        if monster.difficulty == "easy":
                            new_difficulty = "medium"

                        elif monster.difficulty == "medium":
                            new_difficulty = "hard"

                        elif monster.difficulty == "hard":
                            new_difficulty = "hard"


                        fight = player.initiate_fight_monster(monster,debug = debug)
                        player.monster_attempts += 1

                        if fight == 1: ##Player WON
                            player.victory_points += 1
                            player.gold += 2
                            self.monster_kills += 1
                            player.monster_wins += 1
                            ## Generate a new monster
                            self.graph.nodes[player.current_position]["monster"] = []
                            self.spawn_monster(self.graph.nodes[player.current_position]["terrain"],new_difficulty)

                        elif fight == 2: ## Monster Won
                            #Player gains Nothing
                            pass
                    
                    elif ai_move_choice == 'meditate':
                        
                        if player.Combat == 5 and not player.CombatVP:
                            player.victory_points += 1
                            player.CombatVP = True

                        elif player.Defense == 5 and not player.DefenseVP:
                            player.victory_points += 1
                            player.DefenseVP = True

                        elif player.Alchemy == 5 and not player.AlchemyVP:
                            player.victory_points += 1
                            player.AlchemyVP = True

                        elif player.Speciality == 5 and not player.SpecialityVP:
                            player.victory_points += 1
                            player.SpecialityVP = True

                        else:
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
                        player.won = True
                        if debug : self.display()
                        if game_stats:

                            for _player in self.players:

                                n_stats = {

                                    "Player"         : _player,
                                    "GameWon"        : _player.won,
                                    "MonsterKills"   : _player.monster_wins,
                                    "MonsterAttempts": _player.monster_attempts,
                                    "Victorypoints"  : _player.victory_points,
                                    "Turn"           : turn,
                                    "Combat"         : _player.Combat,
                                    "Alchemy"        : _player.Alchemy,
                                    "Defence"        : _player.Defense,
                                    "Speciality"     : _player.Speciality,
                                    "SpecialityCount": _player.SpecialityNumber
                                }

                                #print("Number: ", _player.SpecialityNumber)
                                self.stats.append(n_stats)

                            return self.stats
                        else:
                            return(1)

                elif isinstance(player, player_p.Player):
                    print(f"{player.name}'s turn! Choose a move:")

                    PHASE_1 = False
                    #PHASE_2 = False
                    #PHASE_3 = False

                    PHASE_1 = True
                    while PHASE_1:

                        ## "Does the player want to keep moving"
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
                                choice = int(input("Enter move index: . (-1 to skip Phase 1)"))
                                if choice == -1:
                                    break
                                if choice < 0 or choice >= len(moves):
                                    print("Invalid index. Please enter a valid move index.")
                                else:
                                    break  # Valid input, exit the loop
                            except ValueError:
                                print("Invalid input. Please enter a number. (-1 to skip Phase 1)")

                        #choice = int(input("Enter move index: "))
                        if choice == -1:
                            print("Skipping Phase 1")
                        else:
                            self.move(player, moves[choice])
                            self.location_action(player.current_position,player)



                    ## PHASE 2
                    phase_2 = ['explore']

                    if self.is_monster(player.current_position):
                        phase_2.append('fight')

                    if player.Combat == 4 and player.CombatVP == False:
                        phase_2.append('C_Meditate')

                    if player.Defense == 4 and player.DefenseVP == False:
                        phase_2.append('D_Meditate')
                    
                    if player.Alchemy == 4 and player.AlchemyVP == False:
                        phase_2.append('A_Meditate')

                    if player.Speciality == 4 and player.SpecialityVP == False:
                        phase_2.append('S_Meditate')

                    

                    


                    for index, x in enumerate(phase_2):
                        print(f"{index}. {x}")

                    while True:
                        try:
                            choice = int(input("Enter move index: "))
                            if choice < 0 or choice >= len(phase_2):
                                print("Invalid Index. Please enter a valid move index. ")
                            else:
                                break

                        except ValueError:
                            print("Invalid input. Please enter a number.")

                   

                    selected_action = phase_2[choice]
                    if selected_action == 'explore':
                        self.explore(player)

                    elif selected_action == 'fight':

                        monster:player_p.Monster = self.graph.nodes[player.current_position]["monster"][0]
                        monster.initiate_fight()
                        new_difficulty = None

                        if monster.difficulty == "easy":
                            new_difficulty = "medium"

                        elif monster.difficulty == "medium":
                            new_difficulty = "hard"

                        elif monster.difficulty == "hard":
                            new_difficulty = "hard"


                        fight = player.initiate_fight_monster_human(monster,debug = debug)
                        player.monster_attempts += 1

                        if fight == 1: ## Player WON

                            player.victory_points += 1
                            player.gold += 2
                            player.monster_wins += 1

                            ## Generate a new monster
                            self.graph.nodes[player.current_position]["monster"] = []
                            self.spawn_monster(self.graph.nodes[player.current_position]["terrain"],new_difficulty)

                        elif fight == 2: ## Monster Won
                            #Player gains Nothing
                            #Player gets a extra card
                            pass


                    elif selected_action == 'C_Meditate':
                        player.CombatVP = True
                        player.victory_points += 1

                    elif selected_action == 'D_Meditate':
                        player.DefenseVP = True
                        player.victory_points += 1

                    elif selected_action == 'A_Meditate':
                        player.AlchemyVP = True
                        player.victory_points += 1

                    elif selected_action == 'S_Meditate':
                        player.SpecialityVP = True
                        player.victory_points += 1

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
                        player.won = True
                        if debug : self.display()
                        if game_stats:

                            for _player in self.players:

                                n_stats = {

                                    "Player"         : _player,
                                    "GameWon"        : _player.won,
                                    "MonsterKills"   : _player.monster_wins,
                                    "MonsterAttempts": _player.monster_attempts,
                                    "Victorypoints"  : _player.victory_points,
                                    "Turn"           : turn,
                                    "Combat"         : _player.Combat,
                                    "Alchemy"        : _player.Alchemy,
                                    "Defence"        : _player.Defense,
                                    "Speciality"     : _player.Speciality,
                                    "SpecialityCount": _player.SpecialityNumber
                                }
                    
                                self.stats.append(n_stats)

                            return self.stats
                        else:
                            return(1)


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
        #print(f"Before Random Card Aquired {len(player.hand)}")
        player.add_card(random_card)
        #print(f"Random Card Aquired {len(player.hand)}")

        # Remove the bought card from the bank and shift remaining cards left
        bought_index = self.bank.index(random_card)
        for i in range(bought_index, len(self.bank) - 1):
            self.bank[i] = self.bank[i + 1]

        # Refill the bank from the deck if possible
        if self.deck:
            self.bank[-1] = self.deck.pop()
        else:
            self.bank.pop()  # Remove last card if the deck is empty

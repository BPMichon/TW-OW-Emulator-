import networkx as nx
import random
import json

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
            print(f"Gold: {player.gold} , Cards: {[card.name for card in player.cards]}")
            print()
        print()
    
    def get_valid_moves(self, player):
        return list(self.graph.neighbors(player.current_position))
    
    def move(self, player, new_pos):
        if new_pos in self.get_valid_moves(player):
            player.current_position = new_pos
            return True
        return False
    
    def start_game(self):
        while True:
            for player in self.players:

                self.display()

                if isinstance(player, AI):
                    print(f"{player.name}'s turn...")
                    ai_move = player.choose_move(self)
                    if ai_move is not None:
                        self.move(player, ai_move)

                elif isinstance(player, Player):
                    print(f"{player.name}'s turn! Choose a move:")

                    ## Need to see all possible moves, for all 3 possible variations
                    ## Valid Moves for spending 1 Location
                    ## Valid Moves for spending 1 Location and 1 Gold
                    ## Valid Moves for spending 2 Gold


                    moves = self.get_valid_moves(player)

                    for i, move in enumerate(moves):
                        print(f"{i}: Move to {self.graph.nodes[move]['name']}")

                    choice = int(input("Enter move index: "))
                    self.move(player, moves[choice])

########################################################################################
############################# CARD CODE ################################################
########################################################################################

# I will create similar components for the cards here, 
with open("Game_Data/action_cards.json", "r") as f:
    action_cards = json.load(f)
print("\n Card \n")

print(action_cards.get("1", "Card not found."))






class Card:
    def __init__(self, name, terrain, cost , colour):
        self.name = name
        self.terrain = terrain
        self.cost = cost
        self.colour = colour



########################################################################################
############################# PLAYER CODE ##############################################
########################################################################################

# Player Class stores all information About Player
class Player:
    def __init__(self,name,current_position,starter_cards, gold=2):
        self.name = name
        self.current_position = current_position
        self.cards = starter_cards
        self.discard = []
        self.gold = gold

# Heuristic function (AI chases the player, currently only works for 1 player)
def heuristic(position, board):
    player_pos = board.players[0].current_position
    return -nx.shortest_path_length(board.graph, source=position, target=player_pos)  # Minimize distance

def discard(card):
    pass

# AI using state search
class AI(Player):
    def choose_move(self, board):
        possible_moves = board.get_valid_moves(self)
        if not possible_moves:
            return None
        
        # Evaluate moves based on heuristic
        best_move = max(possible_moves, key=lambda pos: heuristic(pos, board))
        return best_move



########################################################################################
################################# MAIN CODE ############################################
########################################################################################

C1 = Card('Card1','SEA',1,"Blue")
C2 = Card('Card2','FOREST',2,"Red")
C3 = Card('Card3','MOUNTAIN',3,"Green")

SampleHand = [C1,C2,C3]

# Initialize Players and Board
P1 = Player('P1', 1, SampleHand)
AI_player = AI('AI', 12, SampleHand)

board = Board(graph=map_graph, players=[P1,AI_player])
board.start_game()
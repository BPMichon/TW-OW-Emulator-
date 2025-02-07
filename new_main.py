import networkx as nx
import random

########################################################################################
############################### LOCATIONS CODE #########################################
########################################################################################
# We generate a graph using NetworkX library, this lets us easily define adjacency of nodes,
# aswell as quickly look up route between nodes using different graph algorithms

map_graph = nx.Graph()

# Location Names
LocationNames = [
  'Behelt Nar','Kaer Seren','Hengfors','Kaer Morhen','Ban Ard',
  'Cidaris','Novigrad','Vizima','Vengerberg','Cintra',
  'Haern Caduch','Beauclair','Glenmore','Doldeth','Loc Ichaer',
  'Gorthur Guaed','Dhuwod','Stygga','Ard Modron'
]

# Adjacency Matrix
LocMatrix = [
  [4,8,11,12], [2,5,6,9], [1,3,6,7], [2,4,7], [3,7,8,0],
  [1,6,9], [1,2,5,7,9], [2,3,4,6,8,9,10,11], [4,7,11,0], [1,5,6,7,10,13],
  [7,9,11,13,15], [7,8,10,12,15,16,0], [11,16,0], [9,10,14,15], [13,15,17],
  [10,11,13,14,16,17,18], [11,12,15,18], [14,15,18], [15,16,17]
]

LocationTerrains = [
  'ALL','SEA','MOUNTAIN','MOUNTAIN','SEA','SEA','FOREST','FOREST','FOREST','MOUNTAIN',
  'FOREST','MOUNTAIN','SEA','MOUNTAIN','SEA','SEA','FOREST','FOREST','MOUNTAIN'
]

# Add nodes with Location attributes
# Should I pass by adress or value??
for idx, name in enumerate(LocationNames):
    map_graph.add_node(idx, name=name, terrain=LocationTerrains[idx])

# Add edges from adjacency matrix
for idx, adjacents in enumerate(LocMatrix):
    for neighbor in adjacents:
        map_graph.add_edge(idx, neighbor)



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
                    moves = self.get_valid_moves(player)

                    for i, move in enumerate(moves):
                        print(f"{i}: Move to {self.graph.nodes[move]['name']}")

                    choice = int(input("Enter move index: "))
                    self.move(player, moves[choice])

########################################################################################
############################# CARD CODE #################################################
########################################################################################

class Card:
    def __init__(self, name, terrain):
        self.name = name
        self.terrain = terrain


########################################################################################
############################# PLAYER CODE ##############################################
########################################################################################

# Player Class stores all information About Player
class Player:
    def __init__(self,name,current_position):
        self.name = name
        self.current_position = current_position

# Heuristic function (AI chases the player, currently only works for 1 player)
def heuristic(position, board):
    player_pos = board.players[0].current_position
    return -nx.shortest_path_length(board.graph, source=position, target=player_pos)  # Minimize distance

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

# Initialize Players and Board
P1 = Player('P1', 1)
AI_player = AI('AI', 12)
board = Board(graph=map_graph, players=[P1,AI_player])
board.start_game()
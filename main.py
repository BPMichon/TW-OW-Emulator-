import networkx as nx
import matplotlib.pyplot as plt
import random

## Begining Implementation of the Witcher: Old World

## To Do:

## Location Matrix 
LocMatrix = [
  [4,8,11,12], #0
  [2,5,6,9], #1
  [1,3,6,7], #2
  [2,4,7], #3
  [3,7,8,0], #4
  [1,6,9], #5
  [1,2,5,7,9], #6
  [2,3,4,6,8,9,10,11], #7
  [4,7,11,0], #8
  [1,5,6,7,10,13], #9
  [7,9,11,13,15], #10
  [7,8,10,12,15,16,0], #11
  [11,16,0], #12
  [9,10,14,15], #13
  [13,15,17], #14
  [10,11,13,14,16,17,18], #15
  [11,12,15,18], #16
  [14,15,18], #17
  [15,16,17], #18
]

## Location Class? 
## Uses Location Matrix to determine location Adjacency 
## Class Defines Terrain Type, Vendors and Quests
LocationNames = [
  'Behelt Nar','Kaer Seren','Hengfors','Kaer Morhen','Ban Ard',
  'Cidaris','Novigrad','Vizima','Vengerberg','Cintra',
  'Haern Caduch','Beauclair','Glenmore','Doldeth','Loc Ichaer',
  'Gorthur Guaed','Dhuwod','Stygga','Ard Modron'
]

LocationTerrains = [
  'ALL',
  'SEA',
  'MOUNTAIN',
  'MOUNTAIN',
  'SEA',
  'SEA',
  'FOREST',
  'FOREST',
  'FOREST',
  'MOUNTAIN',
  'FOREST',
  'MOUNTAIN',
  'SEA',
  'MOUNTAIN',
  'SEA',
  'SEA',
  'FOREST',
  'FOREST',
  'MOUNTAIN'
]

class Location:
    def __init__(self, id, name, terrain, adjacent_locations):
        self.id = id
        self.name = name
        self.terrain = terrain
        self.adjacent_locations = adjacent_locations
        self.vendors = []  
        self.quests  = []   

    def add_vendor(self, vendor):
        """Add a vendor to this location."""
        self.vendors.append(vendor)

    def add_quest(self, quest):
        """Add a quest to this location."""
        self.quests.append(quest)

    def state(self):
        print(f"Location(id={self.id}, name='{self.name}', terrain='{self.terrain}', "
              f"adjacent_locations={self.adjacent_locations}, vendors={self.vendors}, quests={self.quests})")


# Map Data Setup
locations = []
for idx, (name, terrain, adjacents) in enumerate(zip(LocationNames, LocationTerrains, LocMatrix)):
    location = Location(id=idx, name=name, terrain=terrain, adjacent_locations=adjacents)
    locations.append(location)


# Add a vendor and quest to a location
# locations[0].add_vendor("Blacksmith")
# locations[0].add_quest("Find the Lost Relic")


## Cards are what the player uses for its movement, hp, and to fight
##
## Effects -  These are explained under Card Icons:
## Damage: Inflict Damage (Resolves First)
## Shield: Raise Shield Level
## DiscardDraw: Draw the top card from the discard pile
## DiscardSearch: Look at one card from discard and take it
## Return: Return this Card to the players Hand
## DrawMore: After fight turn, draw more cards
## DrawLess: After fight turn, draw less cards

class Card:
    def __init__(self, color, effect, terrain):
        self.color = color
        self.effect = effect
        self.terrain = terrain

    def state(self):
        print(f"Card(color={self.color}, effect={self.effect})")

card_1 = Card('Damage','Red','FOREST')
card_2 = Card('Damage','Blue','MOUNTAIN')
card_3 = Card('Damage','Green','SEA')


## Player Class
## Need to be able to store current deck and stats such as Gold,Items and Level
class Player:
    def __init__(self, name, gold, current_location):
        self.name = name
        self.gold = gold
        self.current_location = current_location
        self.hand = [card_1, card_1, card_2]
        self.discard = []


    def discard_card(self,card):
        """discards a card to your discard pile"""
        if card in self.hand:
            self.hand.remove(card)
            self.discard.append(card)  

    def state(self):
        """prints the whole player state"""
        print("\n")
        print("Player:", self.name ," ")
        print("Current Location:", self.current_location.name)
        print("\n")

    def move_location(self,location : Location):
        self.current_location = location

    def avaiable_terrain(self):
        forest_count = 0
        sea_count = 0
        mountain_count = 0
        wild_count = 0

        for card in self.hand:
            print("Terrain:",card.terrain,"")
            if card.terrain == "FOREST":
                forest_count +=1
            elif card.terrain == "MOUNTAIN":
                mountain_count +=1
            elif card.terrain == "SEA":
                sea_count += 1
            else:
                wild_count += 1

        return {
            'FOREST': forest_count,
            'MOUNTAIN':mountain_count,
            'SEA':sea_count,
            'WILD':wild_count
            }
  
    def evaluate_hand_strength(self):
        # Evaluate Hand Combo Strength
        pass
    def worst_card_in_hand(self,terrain):
        #Look at your hand and given a terrain, find the worst card in the hand 
        # (minimizes hand strength loss)
        pass

    def move(self):
        #
        #
        #
        pass



# View the data
##for loc in locations:
##    loc.state()

## Here I just want to be able to pass in a array of Loacation ID's
## i.e [0,1,4,5]
## thsi should calculate the terrain cost of the path
## return ['FOREST':1,'SEA':2,'MOUNTAIN':0,'ALL':0]

def evaluate_path_cost(path):
    pass


Player1 = Player("Wolf", 2, locations[3])
Player2 = Player("Bear", 2, locations[10])

##Player1.state()
##Player2.state()

Players = [Player1, Player2]

## def GameStart(array_of_players)
## Player Should be showned all valid moves for moving on the map, so then he can choose where to move
## A function which shows all valid moves?

# Create a directed/undirected graph
map_graph = nx.Graph()

# Add nodes with Location attributes
for loc in locations:
    map_graph.add_node(loc.id, 
                       name=loc.name, 
                       terrain=loc.terrain, 
                       vendors=loc.vendors, 
                       quests=loc.quests)

# Add edges from adjacency matrix
for idx, adjacents in enumerate(LocMatrix):
    for neighbor in adjacents:
        map_graph.add_edge(idx, neighbor)



plt.figure(figsize=(10, 8))  # Set figure size
nx.draw(map_graph, with_labels=True, node_color="lightblue", edge_color="gray", node_size=600, font_size=10)

# Show the plot
##plt.show()

source = 0  # Replace with your starting location ID
target = 5  # Replace with your destination location ID

shortest_path = nx.shortest_path(map_graph, source=source, target=target)
##print("Shortest Path:", shortest_path)

all_shortest_paths = list(nx.all_shortest_paths(map_graph, source=source, target=target))
##print("All Shortest Paths:", all_shortest_paths)



class AIPlayer(Player):
    def __init__(self, name, speed, location, strategy="random", goal=None):
        super().__init__(name, speed, location)
        self.strategy = strategy
        self.memory = []
        self.goal = goal

    def choose_move(self, game_map, locations,players):
        current_location_id = self.current_location.id
        
        # Choose movement strategy
        if self.strategy == "random":
            new_location_id = self.random_move(game_map)
        elif self.strategy == "goal":
            new_location_id = self.goal_move(game_map)
        elif self.strategy == "exploration":
            new_location_id = self.exploration_move(game_map)
        elif self.strategy == "safe":
            new_location_id = self.safe_move(game_map)
        elif self.strategy == "chaser":
            new_location_id = self.chaser_move(game_map, players)
        else:
            new_location_id = self.random_move(game_map)  # Default

        # Update memory (for exploration AI)
        self.memory.append(new_location_id)

        return locations[new_location_id]

    # Add movement strategies here:
    def random_move(self, game_map):
        neighbors = list(game_map.neighbors(self.current_location.id))
        return random.choice(neighbors) if neighbors else self.current_location.id

    def goal_move(self, game_map):
        if self.goal:
            path = nx.shortest_path(game_map, self.current_location.id, self.goal.id)
            return path[1] if len(path) > 1 else self.current_location.id
        return self.random_move(game_map)

    def exploration_move(self, game_map):
        neighbors = list(game_map.neighbors(self.current_location.id))
        unvisited = [n for n in neighbors if n not in self.memory]
        return random.choice(unvisited) if unvisited else self.random_move(game_map)

    def chaser_move(self, game_map, players):
        """
        Moves the AI one step closer to the nearest player.
        
        Args:
            game_map (nx.Graph): The game map graph.
            players (list): List of player objects.

        Returns:
            int: The ID of the new location the AI moves to.
        """
        current_location_id = self.current_location.id
        closest_player = None
        shortest_path = None

        # Find the nearest player
        for player in players:
            if player == self:
                continue  # Skip self
            
            try:
                path = nx.shortest_path(game_map, current_location_id, player.current_location.id)
                if shortest_path is None or len(path) < len(shortest_path):
                    closest_player = player
                    shortest_path = path
            except nx.NetworkXNoPath:
                continue  # If no path exists, ignore this player

        # If a player is found, move one step toward them
        if closest_player and shortest_path and len(shortest_path) > 1:
            return shortest_path[1]  # Move one step along the path

        return self.random_move(game_map)  # If no players are reachable, move randomly





def play_game(players, game_map):
    """
    Handles a turn-based player movement system (Human + AI).
    """
    while True:
        for player in players:
            print(f"\n{player.name}'s turn! You are currently at {player.current_location.name}.")
            
            if isinstance(player, AIPlayer):
                # AI chooses where to move
                new_location = player.choose_move(game_map, locations,players)
                player.current_location = new_location
                print(f"{player.name} (AI) moves to {new_location.name}({new_location.id}).")
            
            else:
                # Human player chooses where to move
                current_location_id = player.current_location.id
                neighbors = list(game_map.neighbors(current_location_id))

                print("You can move to:")
                for i, neighbor_id in enumerate(neighbors):
                    neighbor = locations[neighbor_id]
                    print(f"{i + 1}. {neighbor.name} (Terrain: {neighbor.terrain})")
                
                while True:
                    try:
                        choice = int(input("Enter the number of your destination (or 0 to stay): "))
                        if choice == 0:
                            print(f"{player.name} stays at {player.current_location.name}.")
                            break
                        if 1 <= choice <= len(neighbors):
                            new_location = locations[neighbors[choice - 1]]
                            player.current_location = new_location
                            print(f"{player.name} moves to {new_location.name}.")
                            break
                        else:
                            print("Invalid choice. Please enter a valid number.")
                    except ValueError:
                        print("Please enter a valid number.")

        # Ask if players want to continue
        cont = input("\nContinue playing? (y/n): ").strip().lower()
        if cont != 'y':
            print("Game over!")
            break


##play_game(Players,map_graph)

AI1 = AIPlayer("Wolf AI", 2, locations[3], strategy="random")  

AI2 = AIPlayer("Bear AI", 2, locations[10], strategy="goal")  
AI2.goal = locations[5]  # AI2 wants to reach location 5

ChaserAI = AIPlayer("Hunter", 2, locations[3], strategy="chaser")


Players = [AI2, ChaserAI]  # Add AI to the game
play_game(Players, map_graph)




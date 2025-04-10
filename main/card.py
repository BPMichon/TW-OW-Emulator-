import networkx as nx
import random
import json
import copy
from numpy import random
import itertools
from itertools import combinations
from tabulate import tabulate


########################################################################################
############################# CARD CODE ################################################
########################################################################################

# Do I need a class? Can i just use pointer to point where the card is?
## Loads Cards from JASON into an array


class Card:
    def __init__(self, name, colour, cost , terrain, ability,combos,id):
        self.id     :str    = id
        self.name   :str    = name
        self.colour :str    = colour
        self.cost   :int    = cost
        self.terrain:str    = terrain
        self.ability:dict   = ability
        self.combos :dict   = combos

    # def __repr__(self):
    #     return f"{self.colour} -> {', '.join(map(str, self.combos.keys()))}"
    def __repr__(self):
        colour_code = ""
        reset_code = "\033[0m"
        colour_circle = ""

        if self.colour.lower() == "red":
            colour_code = "\033[91m"  # Bright Red
            colour_circle = "🔴"
        elif self.colour.lower() == "blue":
            colour_code = "\033[94m"  # Bright Blue
            colour_circle = "🔵"
        elif self.colour.lower() == "yellow":
            colour_code = "\033[93m"  # Bright Yellow
            colour_circle = "🟡"
        elif self.colour.lower() == "purple":
            colour_code = "\033[95m"  # Bright Magenta (often used for purple)
            colour_circle = "🟣"
        elif self.colour.lower() == "green":
            colour_code = "\033[92m"  # Bright Green
            colour_circle = "🟢"

        combo_str_parts = []
        for key in self.combos.keys():
            combo_colour_code = ""
            combo_shape = ""
            if key.lower() == "red":
                combo_colour_code = "\033[91m"
                combo_shape = "🟥"
            elif key.lower() == "blue":
                combo_colour_code = "\033[94m"
                combo_shape = "🟦"
            elif key.lower() == "yellow":
                combo_colour_code = "\033[93m"
                combo_shape = "🟨"
            elif key.lower() == "purple":
                combo_colour_code = "\033[95m"
                combo_shape = "🟪"
            elif key.lower() == "green":
                combo_colour_code = "\033[92m"
                combo_shape = "🟩"
            combo_str_parts.append(f"{combo_colour_code}{combo_shape}{reset_code}")

        combo_str = ", ".join(combo_str_parts)

        return f"{colour_code}{colour_circle}{reset_code} -> {combo_str}"
    
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
                name    =data["name"],
                colour  =data["colour"],
                cost    =data["cost"],
                terrain =data["terrain"],
                ability =data["ability"],
                combos  =data["combos"],
                id      =card_id
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
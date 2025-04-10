import matplotlib.pyplot as plt
import networkx as nx
import json

########################################################################################
############################### LOCATIONS CODE #########################################
########################################################################################
# We generate a graph using NetworkX library, this lets us easily define adjacency of nodes,
# aswell as quickly look up route between nodes using different graph algorithms

# Changed to using Data from json file, this means I dont need to store all the arrays in code

GAME_MAP = nx.Graph()

with open("Game_Data/location.json", "r") as f:
    locations = json.load(f)

for location in locations:
    GAME_MAP.add_node(location["id"], 
                       name=location["name"], 
                       terrain=location["terrain"],
                       school=location["school"],
                       ability=location["loc_ability"],
                       monster = [])

for location in locations:
    for neighbor in location["adjacents"]:
        GAME_MAP.add_edge(location["id"], neighbor)

## This lets us picture the map
def visual():
    plt.figure(figsize=(10, 6))
    pos = nx.spring_layout(GAME_MAP)

    # Determine color based on terrain
    node_colors = [
        "blue" if data["terrain"] == "SEA" else
        "green" if data["terrain"] == "FOREST" else
        "gray" if data["terrain"] == "MOUNTAIN" else
        "yellow"  # Default color for unknown terrain
        for _, data in GAME_MAP.nodes(data=True)
    ]

    nx.draw(GAME_MAP, pos, with_labels=True, node_color=node_colors, edge_color='gray', node_size=3000, font_size=10)

    plt.title("Game Map Graph (SEA = Blue, FOREST = Green, MOUNTAIN = Gray)")
    plt.show()


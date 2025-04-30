# game_map.py
import json
import networkx as nx
import matplotlib.pyplot as plt

class GameMap:
    def __init__(self):
        self.graph = nx.Graph()

    def load_from_file(self, filepath):
        with open(filepath, "r") as f:
            locations = json.load(f)
        self._build_graph(locations)

    def load_from_data(self, locations):
        """Alternative to load from file - useful for testing"""
        self._build_graph(locations)

    def start(self):
        self.load_from_file("Game_Data/location.json")

    def _build_graph(self, locations):
        for location in locations:
            self.graph.add_node(location["id"],
                                name=location["name"],
                                terrain=location["terrain"],
                                school=location["school"],
                                ability=location["loc_ability"],
                                monster=[])

        for location in locations:
            for neighbor in location["adjacents"]:
                self.graph.add_edge(location["id"], neighbor)

    def visual(self):
        plt.figure(figsize=(10, 6))
        pos = nx.spring_layout(self.graph)

        node_colors = [
            "blue" if data["terrain"] == "SEA" else
            "green" if data["terrain"] == "FOREST" else
            "gray" if data["terrain"] == "MOUNTAIN" else
            "yellow"
            for _, data in self.graph.nodes(data=True)
        ]

        nx.draw(self.graph, pos, with_labels=True, node_color=node_colors, edge_color='gray', node_size=3000, font_size=10)
        plt.title("Game Map Graph")
        plt.show()

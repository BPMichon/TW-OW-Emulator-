import networkx as nx

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




# Example usage:
items = [1,2,3,4,5,6,7]
valid_pairs = [(1,2),(2,3),(1,4),(3,4),(2,5),(2,6)]  

graph = ItemGraph(items, valid_pairs)
valid_sequences = graph.generate_sequences()

for seq in valid_sequences:
    print(seq)



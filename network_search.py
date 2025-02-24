# import networkx as nx
# import matplotlib.pyplot as plt

# # Create an empty graph (or you can start with any graph you want)
# Graph = nx.Graph()
# edges = [[0,1],[1,2],[2,3],[3,4],[2,4],[1,4]]

# # Add custom edges (transitions)
# for edge in edges:
#     Graph.add_edge(edge[0],edge[1])

# ##print(list(nx.dfs_edges(Graph,source=0)))

# # Find DFS paths starting from node 1
# dfs_paths = list(nx.dfs_edges(Graph, source=1))
# edge_dfs = nx.edge_dfs(Graph)
# # Print the DFS paths
# print("DFS paths:", dfs_paths)
# print(f"DFS Edges: hi")
# for i in edge_dfs:
#     print(i)

# T = nx.dfs_tree(Graph, source=1)

# nx.draw(T,with_labels=True)
# #nx.draw(Graph,with_labels=True)
# plt.show()




import networkx as nx
import matplotlib.pyplot as plt

# Create a graph
Graph = nx.Graph()

# Add custom edges
Graph.add_edge(1, 2)
Graph.add_edge(1, 4)
Graph.add_edge(2, 3)
Graph.add_edge(3, 4)

# Function to generate all paths with length 1 to 5 and no repeated nodes
def generate_paths(graph, max_length=5):
    paths = []
    
    def backtrack(node, path):
        # If the path length is between 1 and 5, store it as a string
        if 1 <= len(path) <= max_length:
            paths.append(''.join(map(str, path)))
        
        # If the path exceeds the maximum length, stop further exploration
        if len(path) == max_length:
            return
        
        # Explore neighbors
        for neighbor in graph[node]:
            if neighbor not in path:  # Avoid repeated nodes
                backtrack(neighbor, path + [neighbor])

    # Start DFS traversal from every node in the graph
    for start_node in graph.nodes:
        backtrack(start_node, [start_node])
    
    return paths

# Generate all valid paths
paths = generate_paths(Graph)

# Print the generated paths
print("Generated paths:", paths)

# Draw the graph
nx.draw(Graph, with_labels=True)

# Show the plot
plt.show()

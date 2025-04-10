import networkx as nx

Graph = nx.DiGraph()

# Add custom edges
Graph.add_edge(1, 2)
Graph.add_edge(1, 4)
Graph.add_edge(2, 3)
Graph.add_edge(3, 4)

def find_paths(G, start=0, path=None, seen=None):
    if path is None:
        path = [start]
    if seen is None:
        seen = {start}
    
    # get direct descendants
    desc = nx.descendants_at_distance(G, start, 1)
    if not desc:          # no descendants: STOP
        yield path
    else:
        for n in desc:
            if n in seen: # we already visited this node: STOP
                yield path
            else:
                yield from find_paths(G, n, path+[n], seen.union([n]))

array = (find_paths(Graph,1))
for x in array:
    print(x)
    #print("\n")

array = (find_paths(Graph,2))
for x in array:
    print(x)
    #print("\n")

array = (find_paths(Graph,3))
for x in array:
    print(x)
    #print("\n")

array = (find_paths(Graph,4))
for x in array:
    print(x)
    #print("\n")
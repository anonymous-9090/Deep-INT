import networkx as nx

def path_plan_dfs(G, v, is_first):
    global path, Q
    if is_first:
        path = []
        path.append(v)

    flag = False

    for j in list(G.neighbors(v)):
        if G.has_edge(v, j):
            G.remove_edge(v, j)  # label the edge as visited

            if flag:
                path.append(v)
                path.append(j)
            else:
                path.append(j)

            flag = path_plan_dfs(G, j, False)

    if path:
        Q.append(path.copy())
        path = []

    return True

def main(g):
    # Read the graph from the graphml file
    G = nx.read_graphml(g)

    # Initialize variables
    global path, Q
    path = []
    Q = []

    # Start the path planning from the first node
    start_node = list(G.nodes())[0]
    path_plan_dfs(G, start_node, True)

    int_Q = [[int(element) for element in sublist] for sublist in Q]

    return int_Q

def get_dfs_path(G):
    probe = main(G)
    return probe



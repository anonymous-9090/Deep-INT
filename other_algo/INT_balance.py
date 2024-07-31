import networkx as nx
from itertools import combinations
import random

def remove_isolated_nodes(graph):
    """Removes isolated nodes from the graph."""
    isolated_nodes = list(nx.isolates(graph))
    graph.remove_nodes_from(isolated_nodes)
    return isolated_nodes

def get_subgraphs(graph):
    """Returns a list of subgraphs from the connected components of the graph."""
    return [graph.subgraph(c).copy() for c in nx.connected_components(graph)]

def split_eulerian_cycle(eulerian_cycle, removed_nodes, current_graph_nodes):
    """Splits an Eulerian cycle into segments based on removed nodes and edges."""
    split_cycles = []
    current_cycle = []

    for node in eulerian_cycle:
        current_cycle.append(node)
        if node in removed_nodes and node in current_graph_nodes and len(current_cycle) > 1:
            split_cycles.append(current_cycle)
            current_cycle = [node]

    if len(current_cycle) > 1:
        split_cycles.append(current_cycle)

    return split_cycles

def reconnect_cycles(split_cycles, chosen_paths):
    """Reconnects split cycles using chosen paths only."""
    reconnected_cycles = []
    current_cycle = []
    unconnected_paths = []  # Store paths that couldn't be reconnected

    while split_cycles or current_cycle:
        if not current_cycle:
            current_cycle = split_cycles.pop(0)
        else:
            last_node = current_cycle[-1]
            connected = False

            for path in chosen_paths:
                if path[0] == last_node:
                    current_cycle.extend(path[1:])
                    chosen_paths.remove(path)
                    connected = True
                    break
                elif path[-1] == last_node:
                    current_cycle.extend(reversed(path[:-1]))
                    chosen_paths.remove(path)
                    connected = True
                    break

            if not connected:
                reconnected_cycles.append(current_cycle)
                current_cycle = []

    if current_cycle:
        reconnected_cycles.append(current_cycle)

    if chosen_paths:
        unconnected_paths.extend(chosen_paths)

    return reconnected_cycles, unconnected_paths

def merge_shortest_segments(cycles, unconnected_paths, k):
    """Merge the shortest segments until the number of segments is k, including unconnected paths."""
    all_segments = cycles + unconnected_paths

    while len(all_segments) > k:
        all_segments.sort(key=len)
        merged = False

        for i in range(len(all_segments) - 1):
            for j in range(i + 1, len(all_segments)):
                if all_segments[i][-1] == all_segments[j][0]:
                    all_segments[i].extend(all_segments[j][1:])
                    del all_segments[j]
                    merged = True
                    break
                elif all_segments[i][0] == all_segments[j][-1]:
                    all_segments[j].extend(all_segments[i][1:])
                    del all_segments[i]
                    merged = True
                    break
                elif all_segments[i][0] == all_segments[j][0]:
                    all_segments[j].reverse()
                    all_segments[j].extend(all_segments[i][1:])
                    del all_segments[i]
                    merged = True
                    break
                elif all_segments[i][-1] == all_segments[j][-1]:
                    all_segments[j].reverse()
                    all_segments[i].extend(all_segments[j][1:])
                    del all_segments[j]
                    merged = True
                    break
            if merged:
                break

        if not merged:
            break

    return all_segments

# Main function
def main(G):
    # Read the GraphML file
    graph = nx.read_graphml(G)
    removed_edges = []
    removed_nodes = set()
    eulerian_cycles = []
    chosen_paths = []  # List to store all chosen paths

    # Find all nodes with odd degrees in the original graph
    original_odd_degree_nodes = [node for node in graph.nodes() if graph.degree(node) % 2 == 1]
    L = 0
    while True:
        odd_degree_nodes = [node for node in graph.nodes() if graph.degree(node) % 2 == 1]

        # print(f"Number of odd degree nodes: {len(odd_degree_nodes)}")

        if len(odd_degree_nodes) == 0:
            subgraphs = get_subgraphs(graph)
            eulerian_cycles = []
            for subgraph in subgraphs:
                if nx.is_eulerian(subgraph):
                    start_node = next((node for node in original_odd_degree_nodes if node in subgraph), None)
                    if start_node:
                        eulerian_cycle = [u for u, v in nx.eulerian_circuit(subgraph, source=start_node)]
                    else:
                        eulerian_cycle = [u for u, v in nx.eulerian_circuit(subgraph)]
                    eulerian_cycle.append(eulerian_cycle[0])
                    eulerian_cycles.append(eulerian_cycle)
                    # print(f"Eulerian cycle found in a subgraph starting from {start_node if start_node else 'default node'}:")
                    # print(eulerian_cycle)

            if eulerian_cycles:
                break
            else:
                # print("No Eulerian cycle found in any subgraph.")
                break
        else:
            shortest_paths = {}
            for (u, v) in combinations(odd_degree_nodes, 2):
                try:
                    path = nx.shortest_path(graph, source=u, target=v)
                    shortest_paths[(u, v)] = path
                except nx.NetworkXNoPath:
                    shortest_paths[(u, v)] = None

            # print("Shortest paths between each pair of odd degree nodes:")
            # for (u, v), path in shortest_paths.items():
            #     if path:
            #         print(f"Shortest path from {u} to {v}: {path}")
            #     else:
            #         print(f"No path between {u} and {v}.")

            valid_paths = [path for path in shortest_paths.values() if path]
            if not valid_paths:
                # print("No valid paths between odd degree nodes.")
                break

            chosen_path = random.choice(valid_paths)
            chosen_paths.append(chosen_path)  # Store the chosen path
            # print(f"The randomly chosen path among all shortest paths: {chosen_path}")
            for i in range(len(chosen_path) - 1):
                edge = (chosen_path[i], chosen_path[i + 1])
                graph.remove_edge(*edge)
                removed_edges.append(edge)

            removed_nodes.add(chosen_path[0])
            removed_nodes.add(chosen_path[-1])

            isolated_nodes = remove_isolated_nodes(graph)
            # if isolated_nodes:
            #     print(f"Removed isolated nodes: {isolated_nodes}")

    if len(eulerian_cycles) == 1:
        current_graph_nodes = set(graph.nodes())

        # print(f"Removed nodes: {removed_nodes}")
        # print(f"Current graph nodes: {current_graph_nodes}")

        for i, cycle in enumerate(eulerian_cycles):
            start_node = next((node for node in cycle if node in original_odd_degree_nodes), cycle[0])
            while cycle[0] != start_node:
                cycle.append(cycle.pop(0))

            split_cycles = split_eulerian_cycle(cycle, removed_nodes, current_graph_nodes)
            # print(f"Split Eulerian cycles for subgraph {i + 1}:")
            # for j, split_cycle in enumerate(split_cycles):
            #     print(f"Segment {j + 1}: {split_cycle}")

            split_cycles.sort(key=len)
            # print(f"Sorted split cycles for subgraph {i + 1}:")
            # for j, split_cycle in enumerate(split_cycles):
            #     print(f"Segment {j + 1}: {split_cycle}")

            # print(f"Chosen paths: {chosen_paths}")
            reconnected_cycles, unconnected_paths = reconnect_cycles(split_cycles, chosen_paths)

            # print(f"Reconnected Eulerian cycles for subgraph {i + 1}:")
            # for reconnected_cycle in reconnected_cycles:
            #     print(reconnected_cycle)

            k = len(original_odd_degree_nodes) // 2
            final_segments = merge_shortest_segments(reconnected_cycles, unconnected_paths, k)
            # print(f"Final merged segments (k={k}) for subgraph {i + 1}:")
            # for segment in final_segments:
            #     print(segment)

    elif len(eulerian_cycles) > 1:
        current_graph_nodes = set(graph.nodes())

        split_cycles_all = []
        for i, cycle in enumerate(eulerian_cycles):
            start_node = next((node for node in cycle if node in original_odd_degree_nodes), cycle[0])
            while cycle[0] != start_node:
                cycle.append(cycle.pop(0))

            split_cycles = split_eulerian_cycle(cycle, removed_nodes, current_graph_nodes)
            # print(f"Split Eulerian cycles for subgraph {i + 1}:")
            # for j, split_cycle in enumerate(split_cycles):
            #     print(f"Segment {j + 1}: {split_cycle}")
            
            split_cycles_all += split_cycles
        
        split_cycles_all.sort(key=len)
        # print(f"Sorted split cycles for subgraph {i + 1}:")
        # for j, split_cycle in enumerate(split_cycles_all):
        #     print(f"Segment {j + 1}: {split_cycle}")

        # print(f"Chosen paths: {chosen_paths}")
        reconnected_cycles, unconnected_paths = reconnect_cycles(split_cycles_all, chosen_paths)

        # print(f"Reconnected Eulerian cycles for subgraph {i + 1}:")
        # for reconnected_cycle in reconnected_cycles:
        #     print(reconnected_cycle)

        k = len(original_odd_degree_nodes) // 2
        final_segments = merge_shortest_segments(reconnected_cycles, unconnected_paths, k)
        # print(f"Final merged segments (k={k}) for subgraph {i + 1}:")
        # for segment in final_segments:
        #     print(segment)

    else:
        print("No Eulerian cycle was found in the graph.")

    # Output all chosen paths
    if not eulerian_cycles:
        # for path in chosen_paths:
        #     print(path)
        int_list_of_lists = [[int(item) for item in sublist] for sublist in chosen_paths]
        print(int_list_of_lists)
    else:
        int_list_of_lists = [[int(item) for item in sublist] for sublist in final_segments]
        print(int_list_of_lists)
    
    return int_list_of_lists

def get_intbalance_path(G):
    path = main(G=G)
    return path

if __name__ == "__main__":
    main(G='topo/PionierL3.graphml')

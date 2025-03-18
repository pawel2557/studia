import heapq
import pandas as pd
import networkx as nx


# Definition of the graph
graph = {
    'A': {'D': 2, 'M': 9},
    'D': {'G': 3, 'M': 2},
    'G': {'K': 9, 'J': 5},
    'J': {'S': 8, 'P': 4, 'N': 7},
    'K': {'L': 2, 'J': 4},
    'L': {'Z': 1, 'D': 10},
    'M': {'G': 1, 'W': 1},
    'N': {'M': 2, 'G': 1},
    'P': {'Z': 5, 'S': 3, 'N': 9},
    'S': {'K': 2, 'Z': 6},
    'W': {'A': 3, 'M': 4, 'N': 9, 'Z': 7},
    'Z': {'S': 4, 'N': 3}
}

# Dijkstra's Algorithm
def dijkstra(graph, start):
    pq = []
    heapq.heappush(pq, (0, start))
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    predecessors = {node: None for node in graph}

    while pq:
        current_distance, current_node = heapq.heappop(pq)

        if current_distance > distances[current_node]:
            continue

        for neighbor, weight in graph[current_node].items():
            distance = current_distance + weight

            if distance < distances[neighbor]:
                distances[neighbor] = distance
                predecessors[neighbor] = current_node
                heapq.heappush(pq, (distance, neighbor))

    return distances, predecessors

# Function to reconstruct the path from Dijkstra's results
def reconstruct_path(predecessors, start, end):
    path = []
    while end is not None:
        path.insert(0, end)
        end = predecessors[end]
    return path if path and path[0] == start else []

# Running Dijkstra's algorithm from vertex 'P'
start_node = 'P'
distances, predecessors = dijkstra(graph, start_node)

# Reconstructing paths for each vertex
full_paths = {node: reconstruct_path(predecessors, start_node, node) for node in graph}

# Displaying results in a table
df_full_paths = pd.DataFrame({
    "Vertex": list(graph.keys()),
    "Shortest Distance": [distances[node] for node in graph.keys()],
    "Shortest Path": [" -> ".join(full_paths[node]) if full_paths[node] else "No path" for node in graph.keys()]
})

print(df_full_paths)

# Algorithm to traverse the entire graph at the lowest cost (displaying all steps)
def find_cheapest_tour_with_steps(graph, start):
    G = nx.DiGraph()
    for node, edges in graph.items():
        for neighbor, weight in edges.items():
            G.add_edge(node, neighbor, weight=weight)

    path = []
    total_cost = 0
    detailed_path = []
    unvisited = set(graph.keys())
    current_node = start

    while unvisited:
        path.append(current_node)
        unvisited.remove(current_node)

        neighbors = [(neighbor, G[current_node][neighbor]['weight']) for neighbor in G.successors(current_node) if
                     neighbor in unvisited]

        if not neighbors:
            if unvisited:
                # If we cannot proceed to remaining vertices, use Dijkstra to find a new path
                remaining_nodes = list(unvisited)
                distances, predecessors = dijkstra(graph, current_node)
                next_node = min(remaining_nodes, key=lambda node: distances[node])

                # Reconstruct the full path to the new vertex
                sub_path = reconstruct_path(predecessors, current_node, next_node)

                # Add the full path to the detailed tour
                for i in range(1, len(sub_path)):
                    detailed_path.append((sub_path[i - 1], sub_path[i], G[sub_path[i - 1]][sub_path[i]]['weight']))
                    total_cost += G[sub_path[i - 1]][sub_path[i]]['weight']

                current_node = next_node
            else:
                break
        else:
            next_node, cost = min(neighbors, key=lambda x: x[1])
            detailed_path.append((current_node, next_node, cost))
            total_cost += cost
            current_node = next_node

    return detailed_path, total_cost

# Finding the cheapest tour covering the entire graph with step-by-step transitions
start_node = 'P'
detailed_path, cost = find_cheapest_tour_with_steps(graph, start_node)

# Preparing a table for display
df_detailed_path = pd.DataFrame({
    "Step": list(range(1, len(detailed_path) + 1)),
    "From": [step[0] for step in detailed_path],
    "To": [step[1] for step in detailed_path],
    "Cost": [step[2] for step in detailed_path]
})

# Displaying the table without indexing
print("Detailed path traversing the entire graph from P:")
print(df_detailed_path.to_string(index=False, header=True))
print(f"Total traversal cost: {cost}")

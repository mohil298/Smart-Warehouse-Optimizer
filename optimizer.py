from heapq import heappush, heappop
from math import inf

class WarehouseGraph:
    """Weighted undirected graph: adjacency list => O(V + E) storage."""
    def __init__(self):
        self.adj = {}
        # Small demo aisle map; edge weights represent metres.
        edges = [
            ("PACK","A1",4), ("A1","A2",6), ("A2","A3",6),
            ("A1","B1",5), ("B1","B2",6), ("B2","B3",6),
            ("B1","C1",5), ("C1","C2",6), ("C2","C3",6),
            ("A2","B2",4), ("B2","C2",4),
            ("A3","PACK",18), ("B3","PACK",20), ("C3","PACK",22)
        ]
        for u, v, w in edges:
            self.add_edge(u, v, w)

    def add_edge(self, u, v, weight):
        if weight <= 0:
            raise ValueError("Edge weights must be positive.")
        self.adj.setdefault(u, []).append((v, float(weight)))
        self.adj.setdefault(v, []).append((u, float(weight)))

def shortest_path(graph, source, target):
    """Dijkstra with binary heap: O((V+E) log V)."""
    if source not in graph.adj or target not in graph.adj:
        raise ValueError("Start or destination is not in the warehouse map.")
    distances = {node: inf for node in graph.adj}
    previous = {}
    distances[source] = 0
    heap = [(0, source)]
    while heap:
        dist, node = heappop(heap)
        if dist != distances[node]:
            continue
        if node == target:
            break
        for neighbor, weight in graph.adj[node]:
            candidate = dist + weight
            if candidate < distances[neighbor]:
                distances[neighbor] = candidate
                previous[neighbor] = node
                heappush(heap, (candidate, neighbor))
    if distances[target] == inf:
        raise ValueError(f"No path from {source} to {target}.")
    path = [target]
    while path[-1] != source:
        path.append(previous[path[-1]])
    path.reverse()
    return path, distances[target]

def optimize_pick_route(graph, start, stops, packing_node):
    """Nearest-next-stop heuristic over Dijkstra shortest paths."""
    remaining = list(dict.fromkeys(stops))
    route = [start]
    total = 0.0
    current = start
    while remaining:
        candidates = [(shortest_path(graph, current, stop)[1], stop) for stop in remaining]
        distance, next_stop = min(candidates)
        segment, _ = shortest_path(graph, current, next_stop)
        route.extend(segment[1:])
        total += distance
        current = next_stop
        remaining.remove(next_stop)
    segment, distance = shortest_path(graph, current, packing_node)
    route.extend(segment[1:])
    total += distance
    return route, total

def pack_orders(items, capacity):
    """Exact 0/1 knapsack using 1D DP; discretize weights to 0.1 kg."""
    scale = 10
    cap = int(round(capacity * scale))
    dp = [0.0] * (cap + 1)
    take = [[False] * (cap + 1) for _ in range(len(items))]
    for i, item in enumerate(items):
        weight = int(round(float(item["weight"]) * scale))
        value = float(item["value"])
        if weight <= 0 or value < 0:
            raise ValueError("Weights must be positive and values non-negative.")
        for c in range(cap, weight - 1, -1):
            candidate = dp[c - weight] + value
            if candidate > dp[c]:
                dp[c] = candidate
                take[i][c] = True
    chosen = []
    c = cap
    for i in range(len(items) - 1, -1, -1):
        weight = int(round(float(items[i]["weight"]) * scale))
        if take[i][c]:
            chosen.append(items[i])
            c -= weight
    chosen.reverse()
    return chosen, sum(float(x["weight"]) for x in chosen), sum(float(x["value"]) for x in chosen)

def assign_vehicles(customer_loads, capacities):
    """First-fit decreasing bin packing heuristic. O(n log n + n*m)."""
    if any(x <= 0 for x in customer_loads) or any(x <= 0 for x in capacities):
        raise ValueError("Loads and capacities must be positive.")
    vehicles = [{"vehicle": i + 1, "capacity": cap, "remaining": cap, "customers": []}
                for i, cap in enumerate(capacities)]
    for customer_id, load in sorted(enumerate(customer_loads, 1), key=lambda x: x[1], reverse=True):
        eligible = [v for v in vehicles if v["remaining"] >= load]
        if not eligible:
            raise ValueError(f"No vehicle has capacity for customer {customer_id} ({load} kg).")
        vehicle = min(eligible, key=lambda v: v["remaining"] - load)
        vehicle["customers"].append({"customer": customer_id, "load": load})
        vehicle["remaining"] -= load
    return vehicles

def forecast_demand(history, horizon=1, window=3):
    """Transparent moving-average baseline; recursive multi-step forecast."""
    if not history or any(x < 0 for x in history):
        raise ValueError("Provide non-negative historical sales.")
    series = [float(x) for x in history]
    result = []
    for _ in range(horizon):
        pred = sum(series[-window:]) / min(window, len(series))
        result.append(pred)
        series.append(pred)
    return result

"""
Infrastructure Network Topology and Graph Analysis
===================================================
Models the topological interconnectedness of civil infrastructure assets,
evaluates network flow capacity, calculates graph centrality, and evaluates
redundancy / detour path vulnerability.
"""

from typing import Dict, List, Set, Tuple
import math
from core.models import InfrastructureAsset


class InfrastructureGraphNetwork:
    """
    Graph representation of the regional infrastructure network.
    Assets can function as links (corridors, bridges, pipelines) or nodes (substations, junctions).
    """

    def __init__(self, assets: List[InfrastructureAsset]):
        self.assets_map: Dict[str, InfrastructureAsset] = {a.id: a for a in assets}
        self.adjacency: Dict[str, List[str]] = {}
        self._build_graph()

    def _build_graph(self):
        for asset in self.assets_map.values():
            if asset.id not in self.adjacency:
                self.adjacency[asset.id] = []
            for neighbor_id in asset.connected_nodes:
                if neighbor_id not in self.adjacency[asset.id]:
                    self.adjacency[asset.id].append(neighbor_id)
                # Ensure bidirectional connectivity
                if neighbor_id not in self.adjacency:
                    self.adjacency[neighbor_id] = []
                if asset.id not in self.adjacency[neighbor_id]:
                    self.adjacency[neighbor_id].append(asset.id)

    def calculate_betweenness_centrality(self) -> Dict[str, float]:
        """
        Calculates network betweenness centrality using Brandes' algorithm
        to determine the criticality of an asset as a bridge or routing bottleneck.
        """
        nodes = list(self.adjacency.keys())
        cb = {node: 0.0 for node in nodes}

        for s in nodes:
            stack: List[str] = []
            pred: Dict[str, List[str]] = {w: [] for w in nodes}
            sigma: Dict[str, int] = {w: 0 for w in nodes}
            sigma[s] = 1
            dist: Dict[str, int] = {w: -1 for w in nodes}
            dist[s] = 0
            queue: List[str] = [s]

            while queue:
                v = queue.pop(0)
                stack.append(v)
                for w in self.adjacency.get(v, []):
                    # Path discovery
                    if dist[w] < 0:
                        dist[w] = dist[v] + 1
                        queue.append(w)
                    # Path counting
                    if dist[w] == dist[v] + 1:
                        sigma[w] += sigma[v]
                        pred[w].append(v)

            delta: Dict[str, float] = {w: 0.0 for w in nodes}
            while stack:
                w = stack.pop()
                for v in pred[w]:
                    delta[v] += (sigma[v] / (sigma[w] if sigma[w] != 0 else 1.0)) * (1.0 + delta[w])
                if w != s:
                    cb[w] += delta[w]

        # Normalize centrality to 0.0 - 1.0 range
        n = len(nodes)
        scale = 1.0 / ((n - 1) * (n - 2) / 2.0) if n > 2 else 1.0
        return {node: round(min(1.0, val * scale), 4) for node, val in cb.items()}

    def get_network_redundancy_factor(self, asset_id: str) -> float:
        """
        Evaluates how easily an asset can be bypassed if taken out of service.
        Returns a score in [0.1, 1.0]. A lower redundancy factor means the asset
        is an isolated single-point-of-failure (high criticality).
        """
        neighbors = self.adjacency.get(asset_id, [])
        if len(neighbors) <= 1:
            return 0.15  # Dead-end or critical bottleneck

        # Check if alternate paths exist between neighbors without using asset_id
        u = neighbors[0]
        v = neighbors[1]

        # BFS to find shortest path without asset_id
        visited: Set[str] = {asset_id, u}
        queue: List[Tuple[str, int]] = [(u, 0)]
        found_path_len = -1

        while queue:
            curr, d = queue.pop(0)
            if curr == v:
                found_path_len = d
                break
            for nxt in self.adjacency.get(curr, []):
                if nxt not in visited:
                    visited.add(nxt)
                    queue.append((nxt, d + 1))

        if found_path_len == -1:
            return 0.20  # Network partitioned without this link!
        elif found_path_len <= 3:
            return 0.85  # Strong redundancy (nearby bypass route available)
        else:
            return 0.45  # Weak redundancy (long circuitous detour required)

    def calculate_asset_criticality_index(self, asset_id: str) -> float:
        """
        Combines betweenness centrality, connectivity degree, and redundancy
        into a composite network topological criticality score in [0.0, 1.0].
        """
        centrality = self.calculate_betweenness_centrality().get(asset_id, 0.2)
        redundancy = self.get_network_redundancy_factor(asset_id)
        degree = len(self.adjacency.get(asset_id, []))
        normalized_degree = min(1.0, degree / 4.0)

        # High centrality + low redundancy = high criticality
        criticality = 0.50 * centrality + 0.30 * (1.0 - redundancy) + 0.20 * normalized_degree
        return round(max(0.1, min(1.0, criticality)), 4)

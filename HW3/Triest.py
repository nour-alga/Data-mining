from typing import Set, FrozenSet, DefaultDict
from collections import defaultdict
import random


def _get_edge(line: str) -> FrozenSet[int]:
    parts = line.strip().split()
    if len(parts) >= 2:
        return frozenset([int(parts[0]), int(parts[1])])
    return frozenset()


class TriestBase:
    def __init__(self, file: str, M: int, verbose: bool = True, skip_duplicates: bool = True):
        self.file: str = file
        self.M: int = M
        self.verbose: bool = verbose
        self.skip_duplicates: bool = skip_duplicates
        self.S: Set[FrozenSet[int]] = set()
        self.t: int = 0
        self.tau: int = 0
        self.tau_vertices: DefaultDict[int, int] = defaultdict(int)
        self.seen_edges: Set[FrozenSet[int]] = set() if skip_duplicates else None

    def xi(self) -> float:
        if self.t <= self.M:
            return 1.0
        numerator = self.t * (self.t - 1) * (self.t - 2)
        denominator = self.M * (self.M - 1) * (self.M - 2)
        return max(1.0, numerator / denominator)

    def _sample_edge(self, edge: FrozenSet[int]) -> bool:
        if self.t <= self.M:
            return True
        if random.random() < (self.M / self.t):
            edge_to_remove = random.choice(list(self.S))
            self.S.remove(edge_to_remove)
            self._update_counters(edge_to_remove, increment=False)
            return True
        return False

    def _update_counters(self, edge: FrozenSet[int], increment: bool = True):
        u, v = tuple(edge)
        N_u = {node for link in self.S if u in link for node in link if node != u}
        N_v = {node for link in self.S if v in link for node in link if node != v}
        shared_neighborhood = N_u & N_v
        
        for c in shared_neighborhood:
            if increment:
                self.tau += 1
                self.tau_vertices[u] += 1
                self.tau_vertices[v] += 1
                self.tau_vertices[c] += 1
            else:
                self.tau -= 1
                self.tau_vertices[u] -= 1
                self.tau_vertices[v] -= 1
                self.tau_vertices[c] -= 1
                if self.tau_vertices[u] == 0:
                    del self.tau_vertices[u]
                if self.tau_vertices[v] == 0:
                    del self.tau_vertices[v]
                if self.tau_vertices[c] == 0:
                    del self.tau_vertices[c]

    def run(self) -> float:
        if self.verbose:
            print(f"Running TRIÈST-BASE with M = {self.M}")
            print(f"Reading from file: {self.file}")
            print(f"Skip duplicates: {self.skip_duplicates}\n")

        skipped_count = 0
        
        with open(self.file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                edge = _get_edge(line)
                if len(edge) != 2:
                    continue
                
                u, v = tuple(edge)
                if u == v:
                    continue
                
                if self.skip_duplicates:
                    if edge in self.seen_edges:
                        skipped_count += 1
                        continue
                    self.seen_edges.add(edge)
                
                self.t += 1

                if self.verbose and self.t % 10000 == 0:
                    current_estimate = self.xi() * self.tau
                    print(f"Processed {self.t} edges | Skipped {skipped_count} | "
                          f"Sample: {len(self.S)} | Estimate: {current_estimate:.2f}")

                if self._sample_edge(edge):
                    self.S.add(edge)
                    self._update_counters(edge, increment=True)

        final_estimate = self.xi() * self.tau
        
        if self.verbose:
            print(f"\n{'='*60}")
            print(f"Total unique edges: {self.t}")
            print(f"Duplicates skipped: {skipped_count}")
            print(f"Sample size: {len(self.S)}")
            print(f"Raw triangles in sample: {self.tau}")
            print(f"Scaling factor ξ(t): {self.xi():.4f}")
            print(f"FINAL ESTIMATE: {final_estimate:.2f} triangles")
            print(f"{'='*60}")

        return final_estimate

    def get_local_estimate(self, vertex: int) -> float:
        return self.xi() * self.tau_vertices.get(vertex, 0)

class TriestImpr(TriestBase):
    def xi(self) -> float:
        """Return the weight factor η(t) for TRIÈST-IMPR."""
        if self.t < 3:  # Less than 3 edges => no triangles possible
            return 1.0
        return max(1.0, (self.t - 1) * (self.t - 2) / (self.M * (self.M - 1)))

    def _update_counters(self, edge: FrozenSet[int], increment: bool = True):
        """Update counters with weight η(t). TRIÈST-IMPR never decrements."""
        u, v = tuple(edge)
        N_u = {node for link in self.S if u in link for node in link if node != u}
        N_v = {node for link in self.S if v in link for node in link if node != v}
        shared_neighborhood = N_u & N_v
        weight = self.xi() if increment else 0  # No decrement in TRIÈST-IMPR

        for c in shared_neighborhood:
            self.tau += weight
            self.tau_vertices[u] += weight
            self.tau_vertices[v] += weight
            self.tau_vertices[c] += weight

    def _sample_edge(self, edge: FrozenSet[int]) -> bool:
        """Reservoir sampling logic for TRIÈST-IMPR (same as TRIÈST-BASE)."""
        if self.t <= self.M:
            return True
        if random.random() < (self.M / self.t):
            edge_to_remove = random.choice(list(self.S))
            self.S.remove(edge_to_remove)
            return True
        return False

    def run(self) -> float:
        """Process the edge stream using TRIÈST-IMPR."""
        if self.verbose:
            print(f"Running TRIÈST-IMPR with M = {self.M}")
            print(f"Reading from file: {self.file}")
            print(f"Skip duplicates: {self.skip_duplicates}\n")

        skipped_count = 0
        
        with open(self.file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                edge = _get_edge(line)
                if len(edge) != 2:
                    continue
                
                u, v = tuple(edge)
                if u == v:
                    continue
                
                if self.skip_duplicates:
                    if edge in self.seen_edges:
                        skipped_count += 1
                        continue
                    self.seen_edges.add(edge)
                
                self.t += 1

                # Update counters unconditionally
                self._update_counters(edge, increment=True)

                # Sample edge using reservoir logic
                if self._sample_edge(edge):
                    self.S.add(edge)

                if self.verbose and self.t % 10000 == 0:
                    current_estimate = self.tau
                    print(f"Processed {self.t} edges | Skipped {skipped_count} | "
                          f"Sample: {len(self.S)} | Estimate: {current_estimate:.2f}")

        final_estimate = self.tau

        if self.verbose:
            print(f"\n{'='*60}")
            print(f"Total unique edges: {self.t}")
            print(f"Duplicates skipped: {skipped_count}")
            print(f"Sample size: {len(self.S)}")
            print(f"Raw triangles estimate: {final_estimate:.2f}")
            print(f"{'='*60}")

        return final_estimate


if __name__ == "__main__":
    FILE_PATH = 'web-Google.txt'
    MEMORY_SIZE = 10000
    
    triest = TriestBase(
        file=FILE_PATH,
        M=MEMORY_SIZE,
        verbose=True,
        skip_duplicates=True
    )

    estimated_triangles = triest.run()

    print("\nSample local estimates:")
    sample_vertices = list(triest.tau_vertices.keys())[:5]
    for vertex in sample_vertices:
        local_estimate = triest.get_local_estimate(vertex)
        print(f"  Vertex {vertex}: ~{local_estimate:.2f} triangles")
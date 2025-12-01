from collections import defaultdict
from scipy.stats import bernoulli
import random
from typing import Set, FrozenSet, Callable, DefaultDict
from functools import reduce


def parse_edge_line(text: str) -> FrozenSet[int]:
    #firstly we extract edge information from our data 
    # Parse text, split by spaces, convert to integers, return as frozenset
    vertices = [int(v) for v in text.split()]
    return frozenset(vertices)


class TriangleCounter:
   #the base implemantation of our algorithme 
   
    def __init__(self, filepath: str, memory_size: int, print_logs: bool = True):
         # we initialise our variables 
        # File location for reading edges
        self.filepath: str = filepath
        # Maximum capacity of our edge reservoir
        self.memory_size: int = memory_size
        # Control flag for console output
        self.print_logs: bool = print_logs
        # Edge reservoir  stores our sampled edges
        self.edge_reservoir: Set[FrozenSet[int]] = set()
        # Total edges processed from stream
        self.edges_processed: int = 0
        # Per-vertex triangle counts
        self.vertex_triangle_counts: DefaultDict[int, int] = defaultdict(int)
        # Total triangle count in our sample
        self.sample_triangle_count: int = 0

    @property
    def scaling_factor(self) -> float:
        """
        Compute scaling factor for extrapolating from sample to full graph.
        
        Formula: max(1, C(edges_processed, 3) / C(memory_size, 3))
        where C(n, k) is binomial coefficient "n choose k"
        :return: multiplication factor for final estimate
        """
        # Calculate binomial coefficient ratio
        n = self.edges_processed
        m = self.memory_size
        # then we return the max to ensure we never scale down
        return max(1.0, (n * (n - 1) * (n - 2)) / (m * (m - 1) * (m - 2)))

    def should_add_to_reservoir(self, position: int) -> bool:
        # we fill reservoir with first memory_size edges
        if position <= self.memory_size:
            return True
        
        #  Probabilistic replacement with probability memory_size/position
        elif bernoulli.rvs(p=self.memory_size / position):
            # Select random edge for eviction
            evicted_edge: FrozenSet[int] = random.choice(list(self.edge_reservoir))
            self.edge_reservoir.remove(evicted_edge)
            self.modify_triangle_counts(lambda current, delta: current - delta, evicted_edge)
            
            return True
        else:
            # Skip this edge
            return False

    def modify_triangle_counts(self, operation: Callable[[int, int], int], edge: FrozenSet[int]) -> None:
        # Build neighbor lists for each endpoint
        endpoint_neighbors = []
        for endpoint in edge:
            # Find all neighbors of this endpoint in reservoir
            neighbors = set()
            for existing_edge in self.edge_reservoir:
                if endpoint in existing_edge:
                    # Add the other vertex from this edge
                    for vertex in existing_edge:
                        if vertex != endpoint:
                            neighbors.add(vertex)
            endpoint_neighbors.append(neighbors)
        
        # just for safety check: need exactly 2 endpoints
        if len(endpoint_neighbors) < 2:
            return
        
        # Find common neighbors (vertices connected to both endpoints)
        shared_neighbors: Set[int] = reduce(
            lambda set1, set2: set1 & set2,
            endpoint_neighbors
        )

        # here we update counters for each triangle found
        for shared_vertex in shared_neighbors:
            # global triangle count
            self.sample_triangle_count = operation(self.sample_triangle_count, 1)
            
            #count for our  shared vertex
            self.vertex_triangle_counts[shared_vertex] = operation(
                self.vertex_triangle_counts[shared_vertex], 1
            )

            #  counts for both edge endpoints
            for endpoint in edge:
                self.vertex_triangle_counts[endpoint] = operation(
                    self.vertex_triangle_counts[endpoint], 1
                )


class BaseTriestAlgorithm(TriangleCounter):
    """
    TRIÈST-BASE algorithm implementation.
    
    Reference: De Stefani et al., "TRIÈST: Counting Local and Global Triangles 
    in Fully-Dynamic Streams with Fixed Memory Size", KDD 2016
    
    Estimates global triangle count by scaling sample count at the end.
    """

    def execute(self) -> float:
        
       # Run the BASE algorithm on the edge stream and retur estimated number of triangles in full graph

        if self.print_logs:
            print(f"Executing TRIÈST-BASE with memory_size = {self.memory_size}")

        with open(self.filepath, 'r') as file_stream:
            if self.print_logs:
                print("Stream processing started...")

            for line in file_stream:
                # Parse current edge
                current_edge = parse_edge_line(line)
                
                # Increment stream position
                self.edges_processed += 1

                # Progress update
                if self.print_logs and self.edges_processed % 1000 == 0:
                    print(f"Processing edge {self.edges_processed}...")

                # Reservoir sampling decision
                if self.should_add_to_reservoir(self.edges_processed):
                    # Update counts BEFORE adding to reservoir
                    self.modify_triangle_counts(lambda x, y: x + y, current_edge)
                    
                    # Add to reservoir
                    self.edge_reservoir.add(current_edge)

                # Periodic estimate display
                if self.print_logs and self.edges_processed % 1000 == 0:
                    current_estimate = self.scaling_factor * self.sample_triangle_count
                    print(f"Current triangle estimate: {current_estimate}")

            # Final result: scale sample count
            return self.scaling_factor * self.sample_triangle_count


class ImprovedTriestAlgorithm(TriangleCounter):
    """
    TRIÈST-IMPR (Improved) algorithm implementation.
    Estimates global and local triangle counts in a streaming graph
    with fixed memory and reduced variance using weighted updates.
    """

    @property
    def incremental_scale(self) -> float:
        # Compute eta(t): scaling factor for triangles to ensure unbiased count
        # M(M−1) -> number of ways the first 2 edges of a triangle could be in the sample of size M. (t−1)(t−2) -> total ways the first 2 edges appeared in the stream.
        n = self.edges_processed - 1  # number of edges seen before current
        m = self.memory_size          # reservoir size
        return max(1.0, (n * (n - 1)) / (m * (m - 1)))  # scale ≥ 1

    def modify_triangle_counts(self, operation: Callable[[int, int], int], edge: FrozenSet[int]) -> None:
        """
        Update triangle counts for the current edge using eta(t) scaling.
        Always called before sampling decision.
        """
        # Build neighbor sets from current edge reservoir
        endpoint_neighbors = []
        for endpoint in edge:
            neighbors = {
                vertex
                for existing_edge in self.edge_reservoir if endpoint in existing_edge
                for vertex in existing_edge if vertex != endpoint
            }
            endpoint_neighbors.append(neighbors)
        
        if len(endpoint_neighbors) < 2:
            return  # Not enough neighbors to form a triangle
        
        # Find shared neighbors → vertices completing triangles with this edge
        shared_neighbors: Set[int] = reduce(
            lambda a, b: a & b,
            endpoint_neighbors
        )

        # Increment global and local triangle counters with scale
        for shared_vertex in shared_neighbors:
            self.sample_triangle_count += self.incremental_scale  # global count
            self.vertex_triangle_counts[shared_vertex] += self.incremental_scale  # local count

            for endpoint in edge:
                self.vertex_triangle_counts[endpoint] += self.incremental_scale  # endpoints local count

    def should_add_to_reservoir(self, position: int) -> bool:
        """
        Decide whether to include the current edge in the reservoir.
        Implements standard reservoir sampling: probability = M / t
        """
        if position <= self.memory_size:
            return True
        elif bernoulli.rvs(p=self.memory_size / position):
            # Reservoir full: evict random edge to maintain size
            evicted = random.choice(list(self.edge_reservoir))
            self.edge_reservoir.remove(evicted)
            return True
        else:
            return False  # Do not add this edge

    def execute(self) -> float:
        """
        Run TRIÈST-IMPR on the edge stream.
        Returns the global triangle estimate (already scaled by eta).
        """
        if self.print_logs:
            print(f"Executing TRIÈST-IMPR with memory_size = {self.memory_size}")

        with open(self.filepath, 'r') as file_stream:
            if self.print_logs:
                print("Stream processing started...")

            for line in file_stream:
                current_edge = parse_edge_line(line)
                self.edges_processed += 1

                # Log progress every 1000 edges
                if self.print_logs and self.edges_processed % 1000 == 0:
                    print(f"Processing edge {self.edges_processed}...")

                # Update counters BEFORE deciding to sample
                self.modify_triangle_counts(lambda x, y: x + y, current_edge)

                # Reservoir sampling decision
                if self.should_add_to_reservoir(self.edges_processed):
                    self.edge_reservoir.add(current_edge)

                # Log current triangle estimate
                if self.print_logs and self.edges_processed % 1000 == 0:
                    print(f"Current triangle estimate: {self.sample_triangle_count}")

            # Return final estimate
            return self.sample_triangle_count



# Entry point
if __name__ == "__main__":
    # Run improved variant
    estimator = ImprovedTriestAlgorithm(
        filepath='facebook_combined.txt',
        memory_size=100000,
        print_logs=True
    )
    
    result = estimator.execute()
    print(f"\n{'='*60}")
    print(f"FINAL ESTIMATE: {result:.0f} triangles")
    print(f"{'='*60}")
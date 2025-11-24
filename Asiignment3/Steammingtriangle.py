from collections import defaultdict
from scipy.stats import bernoulli
import random
from typing import Set, FrozenSet, Callable, DefaultDict
from functools import reduce


def _get_edge(line: str) -> FrozenSet[int]:
    """
    Parse a line from the file and extract an edge.
    An edge is represented as a frozenset (immutable set) of two vertex IDs.
    
    Example: "5 10" becomes frozenset({5, 10})
    
    :param line: text line containing two vertex numbers
    :return: frozenset containing the two vertices
    """
    # Split the line by whitespace and convert each part to an integer
    # Then create a frozenset from those integers (frozenset is hashable, can be stored in sets)
    return frozenset([int(vertex) for vertex in line.split()])


class Triest:
    """
    Blueprint for triest triangle estimation method.
    Base class containing shared functionality.
    """

    def __init__(self, file: str, M: int, verbose: bool = True):
        """
        This function initializes the class with all counters set to zero. Moreover, it initializes the file path
        to file and the memory size to M.

        :param file: the path to the file to be read
        :param M: the size of the memory for the algorithm (max edges we can keep)
        :param verbose: if true, prints information on screen
        """
        # Store the path to the file containing the edge stream
        self.file: str = file
        
        # M: Maximum number of edges we can store in memory (our sample size)
        self.M: int = M
        
        # Flag to control printing progress messages
        self.verbose = verbose
        
        # S: The set of sampled edges (our "bucket" or reservoir)
        # Each edge is a frozenset of two vertex IDs
        self.S: Set[FrozenSet[int]] = set()
        
        # t: Counter for total number of edges seen in the stream so far
        self.t: int = 0
        
        # tau_vertices: Dictionary tracking number of triangles each vertex participates in
        # defaultdict means accessing a non-existent key returns 0 automatically
        self.tau_vertices: DefaultDict[int, int] = defaultdict(int)
        
        # tau: Total count of triangles found in our sample S
        self.tau: int = 0

    @property
    def xi(self) -> float:
        """
        Calculate the scaling factor xi (ξ) to estimate total triangles from sample.
        
        This is a property, so we can access it like: self.xi (no parentheses needed)
        
        Formula: max(1, (t choose 3) / (M choose 3))
        = max(1, [t(t-1)(t-2)] / [M(M-1)(M-2)])
        
        :return: the scaling/correction factor
        """
        # Return the maximum of 1.0 or the ratio of binomial coefficients
        # This ratio tells us how much to scale up our sample count
        return max(
            1.0,  # Never scale down below 1
            (self.t * (self.t - 1) * (self.t - 2)) /  # Ways to choose 3 from t edges
            (self.M * (self.M - 1) * (self.M - 2))    # Ways to choose 3 from M edges
        )

    def _sample_edge(self, t: int) -> bool:
        """
        This function determines if the new edge can be inserted in memory. If yes and if the memory if full,
        the function proceeds to remove a random edge from the memory to make space.
        
        This implements reservoir sampling to maintain a uniform random sample.

        :param t: the number of observed samples in the stream (current edge number)
        :return: true if the new edge can be inserted in the memory, false otherwise
        """
        # CASE 1: Memory not full yet (t <= M)
        # Always keep the edge when we haven't reached memory limit
        if t <= self.M:
            return True
        
        # CASE 2: Memory is full (t > M)
        # Use probabilistic sampling: keep with probability M/t
        elif bernoulli.rvs(p=self.M / t):  # Flip a weighted coin with probability M/t
            # Coin said YES - we want to keep this edge
            # But memory is full, so we must evict a random edge first
            
            # Convert our set S to a list and randomly choose one edge to remove
            edge_to_remove: FrozenSet[int] = random.choice(list(self.S))
            
            # Remove the chosen edge from our sample
            self.S.remove(edge_to_remove)
            
            # Update counters: subtract any triangles that involved the removed edge
            # lambda x, y: x - y is a function that subtracts y from x
            self._update_counters(lambda x, y: x - y, edge_to_remove)
            
            # Return True because we made space for the new edge
            return True
        else:
            # Coin said NO - skip this edge, don't add it to sample
            return False

    def _update_counters(self, operator: Callable[[int, int], int], edge: FrozenSet[int]) -> None:
        """
        This function updates the counters related to estimating the number of triangles. The update happens through
        the operator lambda and involves the edge and its neighbours.
        
        A triangle is formed when edge connects two vertices that share a common neighbor.

        :param operator: the lambda used to update the counters (either add or subtract)
        :param edge: the edge interested in the update
        :return: nothing
        """
        # STEP 1: Find the common neighborhood of the edge's two vertices
        # Common neighborhood = vertices connected to BOTH endpoints of this edge
        
        # Build list of neighbor sets for each vertex in the edge
        neighbor_sets = [
            # For each vertex in the edge, build its set of neighbors
            {
                node  # Include this node in the neighbor set
                for link in self.S if vertex in link  # For each edge in S that contains vertex
                for node in link if node != vertex     # Get the other endpoint(s)
            }
            for vertex in edge  # Do this for both vertices in the edge
        ]
        
        # IMPORTANT FIX: Check if we have neighbor sets before using reduce
        # If the list is empty or has only one set, we can't find common neighbors
        if len(neighbor_sets) < 2:
            return  # No triangles possible, exit early
        
        # Now safely use reduce to find intersection of all neighbor sets
        common_neighbourhood: Set[int] = reduce(
            # reduce applies a function cumulatively: combines results with & (intersection)
            lambda a, b: a & b,  # Set intersection operator
            neighbor_sets
        )
        # After reduce, common_neighbourhood contains vertices connected to BOTH edge endpoints

        # STEP 2: For each common neighbor, we found a triangle!
        # Triangle is: edge's two vertices + the common neighbor
        for vertex in common_neighbourhood:
            # Update the global triangle counter using the operator
            # operator is either (x + y) for adding, or (x - y) for removing
            self.tau = operator(self.tau, 1)
            
            # Increment/decrement triangle count for this common neighbor vertex
            self.tau_vertices[vertex] = operator(self.tau_vertices[vertex], 1)

            # Increment/decrement triangle count for both vertices in the edge
            for node in edge:
                self.tau_vertices[node] = operator(self.tau_vertices[node], 1)


class TriestBase(Triest):
    """
    This class implements the algorithm Triest base presented in the paper

    'L. De Stefani, A. Epasto, M. Riondato, and E. Upfal, TRIÈST: Counting Local and Global Triangles in Fully-Dynamic
    Streams with Fixed Memory Size, KDD'16.'

    The algorithm provides an estimate of the number of triangles in a graph in a streaming environment,
    where the stream represent a series of edges.
    """

    def run(self) -> float:
        """
        Runs the algorithm from the stream on the file.
        
        Process: Read edges line-by-line, sample them, update triangle counts,
        and return the final estimate.

        :return: the estimated number of triangles
        """

        # Print starting message if verbose mode enabled
        if self.verbose:
            print("Running the algorithm with M = {}.".format(self.M))

        # Open the file containing the edge stream
        with open(self.file, 'r') as f:
            if self.verbose:
                print("File opened, processing the stream...")

            # Process each line in the file (each line is one edge)
            for line in f:
                # Parse the line to extract the edge as a frozenset
                edge = _get_edge(line)
                
                # Increment the counter of total edges seen
                self.t += 1

                # Print progress every 1000 edges
                if self.verbose and self.t % 1000 == 0:
                    print("Currently sampling element {} in the stream.".format(self.t))

                # Decide whether to add this edge to our sample
                if self._sample_edge(self.t):
                    # CRITICAL: Update counters BEFORE adding edge to S
                    # This way we find triangles with edges already in S
                    # lambda x, y: x + y means we're adding (incrementing)
                    self._update_counters(lambda x, y: x + y, edge)
                    
                    # NOW add the edge to our sample set S
                    self.S.add(edge)

                # Print current estimate every 1000 edges
                if self.verbose and self.t % 1000 == 0:
                    print("The current estimate for the number of triangles is {}.".format(
                        self.xi * self.tau)  # Estimate = scaling_factor × sample_count
                    )

            # Return the final estimate: xi (scaling factor) × tau (triangles in sample)
            return self.xi * self.tau
class TriestImproved(Triest):
    """
        This class implements the algorithm Triest improved presented in the paper

        'L. De Stefani, A. Epasto, M. Riondato, and E. Upfal, TRIÈST: Counting Local and Global Triangles in Fully-Dynamic
        Streams with Fixed Memory Size, KDD'16.'

        The algorithm provides an estimate of the number of triangles in a graph in a streaming environment,
        where the stream represent a series of edges.
    """

    @property
    def eta(self) -> float:
        return max(
            1.0,
            ((self.t - 1) * (self.t - 2)) / (self.M * (self.M - 1))
        )

    def _update_counters(self, operator: Callable[[int, int], int], edge: FrozenSet[int]) -> None:
        """
        This function updates the counters related to estimating the number of triangles. The update happens through
        the operator lambda and involves the edge and its neighbours.

        :param operator: the lambda used to update the counters
        :param edge: the edge interested in the update
        :return: nothing
        """
        common_neighbourhood: Set[int] = reduce(
            lambda a, b: a & b,
            [
                {
                    node
                    for link in self.S if vertex in link
                    for node in link if node != vertex
                }
                for vertex in edge
            ]
        )

        for vertex in common_neighbourhood:
            self.tau += self.eta
            self.tau_vertices[vertex] += self.eta

            for node in edge:
                self.tau_vertices[node] += self.eta

    def _sample_edge(self, t: int) -> bool:
        """
        This function determines if the new edge can be inserted in memory. If yes and if the memory if full,
        the function proceeds to remove a random edge from the memory to make space.

        :param edge: the current sample under consideration
        :param t: the number of observed samples in the stream
        :return: true if the new edge can be inserted in the memory, false otherwise
        """

        if t <= self.M:
            return True
        elif bernoulli.rvs(p=self.M / t):
            edge_to_remove: FrozenSet[int] = random.choice(list(self.S))
            self.S.remove(edge_to_remove)
            return True
        else:
            return False

    def run(self) -> float:
        """
        Runs the algorithm from the stream on the file.

        :return: the estimated number of triangles
        """

        if self.verbose:
            print("Running the algorithm with M = {}.".format(self.M))

        with open(self.file, 'r') as f:
            if self.verbose:
                print("File opened, processing the stream...")

            for line in f:
                edge = _get_edge(line)
                self.t += 1

                if self.verbose and self.t % 1000 == 0:
                    print("Currently sampling element {} in the stream.".format(self.t))

                self._update_counters(lambda x, y: x + y, edge)

                if self._sample_edge(self.t):
                    self.S.add(edge)

                if self.verbose and self.t % 1000 == 0:
                    print(
                        "The current estimate for the number of triangles is {}.".format(self.tau)
                    )

            return self.tau



if __name__ == "__main__":
    TriestImproved(
        file='web-Google.txt',
        M=1000,
        verbose=True
    ).run()
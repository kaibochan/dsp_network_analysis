import networkx as nx


# this class implements the algorithm from https://arxiv.org/pdf/cond-mat/0408187
# "Finding community structure in very large networks" by Clauset, Newman, and Moore (2004)
class GraphModularization:
    def __init__(self, G: nx.Graph) -> None:
        self.graph = G
        self.m = G.number_of_edges()
        if self.m == 0:
            raise ValueError("Graph must have at least one edge to compute modularity.")

        self._setup_data_structures()

    def _setup_data_structures(self):
        # algorithm needs to maintain 3 data structures
        # 1. a sparse matrix of delta Q values for each pair of communities with at least one edge between them
        #   - each row of the matrix is stored both as a balanced binary tree and as a max-heap so the largest can be found in constant time
        # 2. a max-heap, H, of the largest delta Q value in each row of the matrix
        # 3. a vector array, a, where ai is the fraction of edges connected to vertices in community i
        
        self.dq_matrix = {}
        self.dq_max_heap = []
        self.h_max_heap = []
        self.a_vector = []
        
        # on top of the data structures, the degree of each vertex in the graph is also needed
        self.degrees = dict(self.graph.degree())
    
    def _edge_fraction_comm_ij(self, i: int, j: int) -> float:
        # Compute the fraction of edges between communities i and j

        # [Eq. 5] eij = 1/2m ∑vw Avw δ(cv , i)δ(cw , j)
        edges_ij = self.graph.subgraph(self.graph.neighbors(i)).edges(self.graph.neighbors(j))
        edge_fraction_ij = len(edges_ij) / (2 * self.m)
        return edge_fraction_ij

    def _frac_edges_comm_i(self, i: int) -> float:
        # Compute the fraction of end of edges connected to vertices in community i

        # [Eq. 6] ai = 1/2m ∑v kv δ(cv , i)
        degree_sum_i = sum(dict(self.graph.degree(self.graph.neighbors(i))).values())
        frac_edges_i = degree_sum_i / (2 * self.m)
        return frac_edges_i
    
    def compute_modularity(self, communities: list[set]):
        # compute the modularity Q of the current graph partitioning
        
        Q = 0.0
        for i in range(len(communities)):
            e_ii = self._edge_fraction_comm_ij(i, i)  # [Eq. 5]
            a_i = self._frac_edges_comm_i(i)          # [Eq. 6]
            Q += e_ii - (a_i ** 2)                    # [Eq. 4] Q = ∑i (eii - ai^2)

        return Q

    def modularity_maximization(self):
        # algorithm to maximize modularity by merging communities
        # 1. calculate initial delta Q values for all pairs of communities connected by at least one edge
        # 2. while there are pairs of communities with positive delta Q values:
        #    a. find the pair of communities with the largest delta Q value
        # 3. repeat step 2 until only one community remains
        
        # calculate initial delta Q values
        communities = []
        for i in range(self.m):
            for j in range(i + 1, self.m):
                if self.graph.has_edge(i, j):
                    delta_Q = self.compute_modularity(i, j)
                    self.dq_matrix[(i, j)] = delta_Q
                    self.dq_max_heap.append((delta_Q, i, j))

        pass
"""
A simple graph representation used in RPM solvers. The graph is represented internally by a dictionary
(hash-table) implementation of an adjacency list where each node is mapped to a set of edges. An edge
is represented as a HalfEdge which only contains a link to the target node as the source node is already
kept as the key in the dictionary (e.g. {a->[b, c], b->[c]}.

author: Vikash Madhow
"""


class Graph:
    """
    A graph represented internally by a dictionary (hash-table) implementation of an adjacency
    list where each node is mapped to a set of edges. An edge is represented as a HalfEdge which
    only contains a link to the target node as the source node is already kept as the key in the
    dictionary (e.g. {a->{b, c}, b->{c}}.
    """
    def __init__(self, outgoing_edges, directed=True):
        """
        Creates a graph from a node map which is a dictionary mapping nodes to a set of outgoing half-edges.
        :param outgoing_edges: A dictionary where each node of the graph is mapped to a set of
                               outgoing half-edges.
        :param directed: True (default) if this is a directed graph.
        """
        # ensure that all nodes have a key-entry in the node-map.
        self._directed = directed
        self._incoming_edges = {}
        self._outgoing_edges = dict(outgoing_edges)
        for edges in outgoing_edges.values():
            for edge in edges:
                if edge.node not in self._outgoing_edges:
                    self._outgoing_edges[edge.node] = set()

        if not directed:
            for tail, edges in outgoing_edges.items():
                for edge in edges:
                    self._outgoing_edges.setdefault(edge.node, set()).add(edge.__class__(tail, edge.weight))

    @staticmethod
    def edges_from_node_to_targets(node_to_targets):
        """
        Utility method to creates a map of outgoing edges from a map of node to list of target nodes
        (e.g. {a: [b,c], c:[d]). Each item in the node list can be a node or a pair of a node and
         a weight (e.g. {a: [(b, 1), (c, 3)], c:[(d, 4])). The node list can also be a map or or a mix
         of both lists and maps ((e.g. {a: {b: 1, c:3}, c:[(d, 4]), e:[a], f:[g,h])

        :param node_to_targets: The node to to node_list map
        :return: The outgoing_edges map which can be used to create the graph.
        """
        outgoing_edges = {}
        for node, target_list in node_to_targets.items():
            targets = set()
            if isinstance(target_list, list) or isinstance(target_list, dict) or isinstance(target_list, set):
                for target in (target_list.items() if isinstance(target_list, dict) else target_list):
                    if isinstance(target, tuple) and len(target) == 2:
                        targets.add(ToHalfEdge(target[0], target[1]))
                    else:
                        targets.add(ToHalfEdge(target))
            else:
                targets.add(target_list)
            outgoing_edges[node] = targets
        return outgoing_edges

    @classmethod
    def from_graph(cls, graph):
        """
        Copies an existing graph.
        :param graph: Existing graph.
        :return: The copied graph.
        """
        outgoing_edges = {node:set(graph.outgoing_edges(node)) for node in graph.nodes}
        return cls(outgoing_edges, graph.directed)

    @property
    def directed(self):
        """Whether this is a directed graph or not."""
        return self._directed

    @property
    def nodes(self):
        """Returns all nodes in the graph."""
        return self._outgoing_edges.keys()

    def outgoing_edges(self, node):
        """
        Returns the set of outgoing edges for the node. The outgoing_edges of undirected graphs
        equals their incoming_edges.

        :param node: The node whose outgoing edges are being sought.
        :return: The outgoing edges for the node.
        :raise KeyError: If the nodes is not in the graph.
        """
        return self.__outgoing_edges(node)

    def incoming_edges(self, node):
        """
        Returns the set of incoming edges for the node. This is an O(n) operation for
        directed graphs where n is the number of nodes in the graph as the adjacency
        list only keeps outgoing edges from a node. The incoming edges have to be built
        by scanning the node map. For undirected graphs, this is the same as outgoing_edges.

        :param node: The node whose incoming edges are being sought.
        :return: The incoming edges for the node.
        """
        if self.directed:
            return self.__incoming_edges(node)
        else:
            return self.__outgoing_edges(node)

    def edges(self, node):
        """
        Returns the incoming and outgoing edges of the node.
        For undirected graph there are no difference between outgoing_edges, incoming_edges
        and edges.
        :param node: The node for which the edges will be returned.
        :return The edges for the node
        """
        if self.directed:
            return self.__incoming_edges(node).union(self.__outgoing_edges(node))
        else:
            return self.__outgoing_edges(node)

    def edge(self, from_node, to_node):
        """
        Returns the edge from from_node to to_node. Returns None if no such edge exists.
        :param from_node: The source node of the edge.
        :param to_node: The target node of the edge.
        :return The edge from from_node to to_node if it exists, None otherwise.
        """
        if from_node in self._outgoing_edges:
            for edge in self._outgoing_edges[from_node]:
                if edge.node == to_node:
                    return edge
        return None

    def add_node(self, node, outgoing_edges=None):
        """
        Adds a node the graph
        :param node: The node to add.
        :param outgoing_edges: The outgoing edges from the node. Default is None.
        """
        outgoing_edges = set() if outgoing_edges is None else outgoing_edges
        self._outgoing_edges[node] = outgoing_edges
        if not self.directed:
            for edges in outgoing_edges.items():
                for edge in edges:
                    self._outgoing_edges.setdefault(edge.node, set()).add(edge.__class__(node, edge.weight))

    def remove_node(self, node):
        """
        Removes the node from the graph.
        :param node: The node to remove.
        """
        if node in self._outgoing_edges:
            del self._outgoing_edges[node]

        if node in self._incoming_edges:
            del self._incoming_edges[node]

        e = HalfEdge(node)
        for node_to_edges in [self._outgoing_edges, self._incoming_edges]:
            for node, edges in node_to_edges.items():
                if e in edges:
                    edges.remove(e)

    def remove_edge(self, from_node, to_node):
        """
        Removes the edge connecting the two nodes from the graph.
        :param from_node: The source node of the edge to remove.
        :param to_node: The target node of the edge to remove.
        """
        if from_node in self._outgoing_edges:
            edges = self._outgoing_edges[from_node]
            edge = HalfEdge(to_node)
            if edge in edges:
                edges.remove(edge)

        if to_node in self._incoming_edges:
            edges = self._incoming_edges[to_node]
            e = HalfEdge(from_node)
            if e in edges:
                edges.remove(e)

        if not self._directed:
            if to_node in self._outgoing_edges:
                edges = self._outgoing_edges[to_node]
                edge = HalfEdge(from_node)
                if edge in edges:
                    edges.remove(edge)

            if from_node in self._incoming_edges:
                edges = self._incoming_edges[from_node]
                edge = HalfEdge(to_node)
                if edge in edges:
                    edges.remove(edge)

    def __outgoing_edges(self, node):
        """Internal method to compute the outgoing edges of a node."""
        return self._outgoing_edges[node]

    def __incoming_edges(self, node):
        """Internal method to compute the incoming edges."""
        if node not in self._incoming_edges:
            incoming_set = set()
            for tail, edges in self._outgoing_edges.items():
                for edge in edges:
                    if edge.node == node:
                        incoming_set.add(FromHalfEdge(tail, edge.weight))
            self._incoming_edges[node] = incoming_set
        return self._incoming_edges[node]

    def to_graph_viz(self):
        """Produces a GraphViz representation of this graph in the DOT language."""
        spec = ("digraph" if self.directed else "graph") + " {\n"
        for node in self.nodes:
            if len(self.outgoing_edges(node)) > 0:
                for edge in self.outgoing_edges(node):
                    spec += '    "' + str(node) + '"' + (" -> " if self.directed else " -- ") + \
                            '"' + str(edge.node) + '"' + \
                            ("" if edge.weight is None else '[label="' + str(edge.weight) + '"]') + \
                            ";\n"
            else:
                spec += '    "' + str(node) + '";\n'
        spec += "}"
        return spec

    def __str__(self):
        return self.to_graph_viz()

    def __repr__(self):
        return self.to_graph_viz()

    def __eq__(self, other):
        return self is other or self._outgoing_edges == other._outgoing_edges

    def __hash__(self):
        h = 13
        for node, edges in self._outgoing_edges:
            h = 31 * h + hash(node)
            for edge in edges:
                h = 31 * h + hash(edge)
        return h


class HalfEdge:
    """
    A half edge consists of node, representing a source (tail) or target (head) node
    and an optional weight, the other node of the edge being assumed to be available
    from somewhere else. It is used in the hash-table based adjacency list of Graph and
    the source node is the key in the hash-table mapped to a list of half edges for
    every edge originating from the key node to the target node of the half-edge.
    """
    def __init__(self, node, weight=None):
        self._node = node
        self.weight = weight

    @property
    def node(self):
        return self._node

    def __eq__(self, other):
        return self is other or self.node == other.node

    def __hash__(self):
        h = 13
        h = 31 * h + hash(self.node)
        return h

    def __repr__(self):
        return "-" + ("" if self.weight is None else "[" + str(self.weight) + "]-") + ">" + str(self.node)


class ToHalfEdge(HalfEdge):
    """A half-edge going towards a node."""
    def __repr__(self):
        return "-" + ("" if self.weight is None else "[" + str(self.weight) + "]-") + ">" + str(self.node)


class FromHalfEdge(HalfEdge):
    """A half-edge originating from a node."""
    def __repr__(self):
        return str(self.node) + "-" + ("" if self.weight is None else "[" + str(self.weight) + "]-") + ">"


class Edge(HalfEdge):
    """A edge from one node to another in a graph, known as tail and head nodes, respectively."""
    def __init__(self, tail, head, weight=None):
        super().__init__(head, weight)
        self._tail = tail

    @property
    def tail(self):
        return self._tail

    @property
    def head(self):
        return self.node

    def __eq__(self, other):
        return self is other or (type(self) is type(other) and
                                 self.tail == other.tail and
                                 self.head == other.head and
                                 self.weight == other.weight)

    def __hash__(self):
        h = 13
        h = 31 * h + hash(self.tail)
        h = 31 * h + hash(self.head)
        h = 31 * h + hash(self.weight)
        return h

    def __repr__(self):
        return str(self.tail) + "-" + ("" if self.weight is None else "[" + str(self.weight) + "]-") + ">" + str(self.head)


class Path:
    """
    A path is a starting node followed by zero or more outgoing half edges
    pointing to other nodes in sequence (e.g., a->b->c->d, with 'a' as the starting
    node and ->b, ->c and ->d as the consecutive outgoing half-edges linking a
    to d).

    A cost can be associated to a path and is relevant to certain algorithms,
    especially graph-search. If no cost has been provided (or set to none), a cost
    is calculated as follows: if the edges have numeric weights, the cost is calculated
    as the sum of those weights, otherwise it is taken simply as the length of
    path (the number of edges in it). In this case, a path consisting of a single node has
    cost and length 0.
    """
    def __init__(self, start_node, cost=None, *half_edges):
        self.start_node = start_node
        self.last_node = start_node if len(half_edges) == 0 else half_edges[len(half_edges) - 1].node
        self._half_edges = half_edges
        self._edges = None
        self._cost = cost

    @classmethod
    def from_path(cls, path):
        """Creates a copy of the path."""
        half_edges = []
        for half_edge in path.half_edges:
            half_edges.append(half_edge.__class__(half_edge.node, half_edge.weight))
        return cls(path.start_node, path.cost, *half_edges)

    @property
    def half_edges(self):
        return self._half_edges

    @property
    def edges(self):
        """The path as a list of full-edges, constructed on demand."""
        if self._edges is None:
            self._edges = []
            tail = self.start_node
            for half_edge in self.half_edges:
                self._edges.append(Edge(tail, half_edge.node, half_edge.weight))
                tail = half_edge.node
        return self._edges

    @property
    def cost(self):
        """
        The cost of the path measured as either the sum of the weight on the individual edges
        when they are numeric or the length of the path otherwise.
        """
        if self._cost is None:
            self._cost = 0
            for edge in self.half_edges:
                if isinstance(edge.weight, int) or isinstance(edge.weight, float):
                    self._cost += edge.weight
                else:
                    self._cost += 1
        return self._cost

    def extend(self, edge, cost=None):
        """
        Returns a new path consisting of this path extended by the supplied edge.
        :param edge: The edge to extends this path with
        :param cost: The cost of the new path. If this is None the default cost-computation
                     is applied to the new path (sum of weights if numeric, otherwise path-length).
        :return: The new extended path. The current path is not changed.
        """
        new_edges = list(self.half_edges)
        new_edges.append(edge)
        return Path(self.start_node, cost, *new_edges)

    def __getitem__(self, key):
        return self.edges[key]

    def __len__(self):
        """The length of a path is the number of edges in it"""
        return len(self.half_edges)

    def __eq__(self, other):
        return self is other or (type(self) is type(other) and self.half_edges == other.half_edges)

    def __hash__(self):
        h = 13
        h = 31 * h + hash(self.start_node)
        h = 31 * h + hash(self.half_edges)
        return h

    def __lt__(self, other):
        return self.cost < other.cost

    def __repr__(self):
        return str(self.start_node) + "".join(map(lambda e: str(e), self.half_edges))

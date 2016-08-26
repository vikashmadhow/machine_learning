"""
Some generic graph exploration, search and tree-growing algorithms working in breadth-first,
depth-first, minimum-cost, etc. The algos are generic enough for them to be adapted for more
sophisticated ones such as the A* search.

author: Vikash Madhow
"""

from Graph import Graph, Path
from collections import deque
from heapq import heappush, heappop


class PathQueue:
    """
    A path queue holds paths and is used by the graph exploration algorithm. Depending on
    how the path-queue returns paths on retrieval, the search will work as breadth-first,
    depth-first, etc. This idea of using different queue types for achieving different
    types of search is described in the book "Artificial intelligence: a modern approach"
    by Stuart Russell & Peter Norvig.
    """
    def __init__(self): pass

    def add(self, node): pass

    def add_all(self, nodes):
        for node in nodes:
            self.add(node)

    def pop(self): pass

    def has_more(self): pass


class FifoPathQueue(PathQueue):
    """
    A path-queue returning paths in first-in-first-out order. Using this
    path-queue in the search and explore functions produces breadth-first
    exploration behavior.
    """
    def __init__(self):
        super().__init__()
        self._nodes = deque()

    def add(self, node):
        self._nodes.append(node)

    def pop(self):
        return self._nodes.popleft()

    def has_more(self):
        return len(self._nodes) > 0

    def __len__(self):
        return len(self._nodes)


class LifoPathQueue(PathQueue):
    """
    A path-queue returning paths in last-in-first-out order. Using this
    path-queue in the search and explore functions produces depth-first
    exploration behavior.
    """
    def __init__(self):
        super().__init__()
        self._nodes = deque()

    def add(self, node):
        self._nodes.append(node)

    def pop(self):
        return self._nodes.pop()

    def has_more(self):
        return len(self._nodes) > 0

    def __len__(self):
        return len(self._nodes)


class PriorityPathQueue(PathQueue):
    """
    A path-queue returning paths in minimum-cost order. Using this path-queue
    in the search and explore functions produces minimum-cost first (greedy)
    exploration behavior.
    """
    def __init__(self):
        super().__init__()
        self._nodes = []

    def add(self, node):
        heappush(self._nodes, node)

    def pop(self):
        return heappop(self._nodes)

    def has_more(self):
        return len(self._nodes) > 0

    def __len__(self):
        return len(self._nodes)


# Graph exploration functions and objects
###########################################

# Signals the exploration function that outgoing edges from the current path
# being explored should not be followed but the exploration should continue
# on other paths.
DONT_FOLLOW_THIS_PATH = object()


def default_path_expansion(graph, path):
    """
    The default path expansion function returns all outgoing edges of the
    last node in the path.
    :param graph: The graph being explored.
    :param path: The path to expand.
    :return: All outgoing edges of the path to expand.
    """
    return graph.outgoing_edges(path.last_node)


def explore(graph, start_node, path_queue, explore_op, accumulator=None,
            expand_op=default_path_expansion, path_cost_op=None):
    """
    Explores the nodes in the graph starting from start_node. For every path from
    start_node to an arbitrary node in the graph, the explore_op function is called
    with the graph and the path (from the start_node to the current node). This function
    can return None to continue the exploration, the constant DONT_FOLLOW_THIS_PATH to
    continue the exploration without expanding the current path (ignoring all following
    nodes on path) or any other value, in which case the exploration is stopped and that
    value is returned as the result of the exploration.

    The path_cost_op function, if provided, is used to compute the cost of every
    path produced and is useful when searching the graph using more complicated cost
    functions (such as the heuristics used in A* search). If not provided, the path cost
    is taken to be the sum of the weight of the edges (if the weight are numeric) or simply
    the length of the path, otherwise.

    This exploration function is used to implement the search and tree-growing functions.

    :param graph: The graph to explore.
    :param start_node: The node to start the exploration at.
    :param path_queue: The path_queue to use, controlling the exploration behavior.
    :param explore_op: The function taking a graph and a path invoked for every path
                       explored for the graph. The accumulator parameter is passed as the
                       last parameter to this function and can be used to accumulate certain
                       information during the exploration. It could be used, for instance,
                       to construct a spanning subgraph of this graph.
    :param accumulator: A value supplied to the explore_op to accumulate data during the exploration.
                        Could be used by custom graph algorithms.
    :param expand_op: A function taking as parameters the graph and current exploring path and
                      returning the successor edges to explore. The default function returns
                      all outgoing edges of the current path.
    :param path_cost_op: The optional function to compute the cost of a new path, invoked
                         with the graph, path to be extended and half-edge with which the
                         path is being extended.
    :return: The result of the exploration which is the result returned by the
             explore_op function, or None if the exploration completed without the
             explore_op function returning any result (other than the
             DONT_FOLLOW_THIS_PATH constant).
    """
    explored = set()

    def _explore():
        while path_queue.has_more():
            path = path_queue.pop()
            frontier = path.last_node
            if frontier not in explored:
                explored.add(frontier)
                result = explore_op(graph, path, accumulator)
                if result is None:
                    successors = expand_op(graph, path)
                    if successors is not None:
                        for edge in filter(lambda e: e.node not in explored, successors):
                            path_queue.add(
                                path.extend(edge,
                                            None if path_cost_op is None else path_cost_op(graph, path, edge)))

                elif result is DONT_FOLLOW_THIS_PATH:
                    continue

                else:
                    return result
        else:
            return None

    path_queue.add(Path(start_node))
    return _explore()


def breadth_first_explore(graph, start_node, explore_op, accumulator=None, expand_op=default_path_expansion):
    """Explores the graph breadth-first"""
    return explore(graph, start_node, FifoPathQueue(), explore_op, accumulator, expand_op)


def depth_first_explore(graph, start_node, explore_op, accumulator=None, expand_op=default_path_expansion):
    """Explores the graph depth-first"""
    return explore(graph, start_node, LifoPathQueue(), explore_op, accumulator, expand_op)


def min_cost_first_explore(graph, start_node, explore_op, accumulator=None, expand_op=default_path_expansion):
    """Explores the graph, taking minimum costs path first"""
    return explore(graph, start_node, PriorityPathQueue(), explore_op, accumulator, expand_op)


def search(graph, start_node, path_queue, goal_op, expand_op=default_path_expansion, path_cost_op=None):
    """
    Search the graph, starting from the start node, for a path to a node
    for which goal_op returns true. The path_queue and path_cost_op arguments
    have the same semantics as for those arguments in the explore function.

    :param graph: The graph to search.
    :param start_node: The node to start the search from.
    :param path_queue: The path_queue to use, modifying the search behaviour as
                       describes for the explore() function.
    :param goal_op: This function is supplied with the graph and the current path
                    and, if it returns true, the search ends returning the current path.
                    Use the match_node() function to create a goal_op which matches a
                    specific node in the graph.
    :param path_cost_op: A function for calculating path-cost as used in the
                         explore() function.
    :return: The path from the start_node to a goal node (as defined by the goal_op) or
             None if no such path is found.
    """
    def search_explore_op(graph, path, accumulator):
        return path if goal_op(graph, path) else None

    return explore(graph, start_node, path_queue, search_explore_op, None, expand_op, path_cost_op)


def breadth_first_search(graph, start_node, goal_op, expand_op=default_path_expansion, path_cost_op=None):
    """Breadth-first search"""
    return search(graph, start_node, FifoPathQueue(), goal_op, expand_op, path_cost_op)


def depth_first_search(graph, start_node, goal_op, expand_op=default_path_expansion, path_cost_op=None):
    """Depth-first search"""
    return search(graph, start_node, LifoPathQueue(), goal_op, expand_op, path_cost_op)


def min_cost_search(graph, start_node, goal_op, expand_op=default_path_expansion, path_cost_op=None):
    """Minimum-cost (greedy) search"""
    return search(graph, start_node, PriorityPathQueue(), goal_op, expand_op, path_cost_op)


def match_node(goal_node):
    """
    Returns a goal_op function (to be used in search functions) that returns true
    if the last_node of the current path is the supplied goal node. This can be used
    when the goal node is a static node in the graph (as opposed to looking for a node
    with certain properties).

    :param goal_node: The goal node that this goal_op will match with.
    :return: The goal_op function for matching the supplied goal_node.
    """
    return lambda graph, path: path.last_node == goal_node


# Simple tree-growing algorithms
########################################

def spanning_tree(graph, start_node, path_queue, expand_op=default_path_expansion, path_cost_op=None):
    """
    Creates and return a spanning tree of the graph. The other parameters to this
    function have the same meaning as in GraphExplore.explore() function.
    """
    def grow_tree(g, path, tree):
        path_length = len(path)
        if path_length == 0:
            tree[path.start_node] = set()

        elif path_length == 1:
            last_edge = path.half_edges[0]
            tree.setdefault(path.start_node, set()).add(last_edge.__class__(last_edge.node, last_edge.weight))

        else:
            last_edge = path.half_edges[path_length - 1]
            tree.setdefault(path.half_edges[path_length - 2].node, set()).add(
                last_edge.__class__(last_edge.node, last_edge.weight))

    t = {}
    explore(graph, start_node, path_queue, grow_tree, t, expand_op, path_cost_op)
    return Graph(t)


def breadth_first_spanning_tree(graph, start_node, expand_op=default_path_expansion, path_cost_op=None):
    """Grows the tree, exploring the graph breadth-first."""
    return spanning_tree(graph, start_node, FifoPathQueue(), expand_op, path_cost_op)


def depth_first_spanning_tree(graph, start_node, expand_op=default_path_expansion, path_cost_op=None):
    """Grows the tree, exploring the graph depth-first."""
    return spanning_tree(graph, start_node, LifoPathQueue(), expand_op, path_cost_op)


def min_cost_spanning_tree(graph, start_node, expand_op=default_path_expansion, path_cost_op=None):
    """Minimum-cost tree, equivalent to Prim's algorithm"""
    return spanning_tree(graph, start_node, PriorityPathQueue(), expand_op, path_cost_op)


def main():
    g = Graph(Graph.edges_from_node_to_targets({'a':[('b', 1), ('d', 2)], 'b':[('c', 5), ('d', 1)], 'd':[('c', 12), ('e', 1)]}))
    explore(g, 'a', FifoPathQueue(), lambda g, p, a: print(p))
    explore(g, 'a', LifoPathQueue(), lambda g, p, a: print(p))
    explore(g, 'a', PriorityPathQueue(), lambda g, p, a: print(p))

    print()
    print(min_cost_search(g, 'a', match_node('c')))

    # Tree-growing test
    print(breadth_first_spanning_tree(g, 'a'))
    print(depth_first_spanning_tree(g, 'a'))
    print(min_cost_spanning_tree(g, 'a'))
    print(g)


if __name__ == "__main__":
    main()

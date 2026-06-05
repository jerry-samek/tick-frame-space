import networkx as nx
from substrate import Substrate


def test_first_cut_two_leaves_adjacent():
    s = Substrate(); s.tick()
    g = s.leaf_graph()
    assert g.number_of_nodes() == 2 and g.number_of_edges() == 1


def test_children_inherit_parent_neighbors():
    s = Substrate(); s.tick(); s.tick()
    g = s.leaf_graph()
    assert g.number_of_nodes() == 4
    assert nx.is_connected(g)

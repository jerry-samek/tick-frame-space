import networkx as nx
from nulls import poisson_3d, grid_2d, random_tree, eden_blob, diffusion_field


def test_poisson_3d_connected_meandeg_reasonable():
    g, coords = poisson_3d(n=2000, seed=0)
    md = 2 * g.number_of_edges() / g.number_of_nodes()
    assert nx.is_connected(g) and 3 < md < 40
    assert len(coords) == g.number_of_nodes()


def test_grid_2d_shape():
    g = grid_2d(40)
    assert g.number_of_nodes() == 1600


def test_random_tree_is_tree():
    assert nx.is_tree(random_tree(2000, seed=0))


def test_eden_blob_grows():
    g = eden_blob(800, seed=0)
    assert g.number_of_nodes() == 800 and nx.is_connected(g)


def test_diffusion_field_runs():
    g, pts, x = diffusion_field(500, seed=0, steps=50)
    assert len(x) == g.number_of_nodes()

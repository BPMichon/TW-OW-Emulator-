import pytest
from locations import GameMap

## Sample test data for testing locations
sample_locations = [
    {
        "id": "A",
        "name": "Alpha",
        "terrain": "FOREST",
        "school": "Druid",
        "loc_ability": "Regrowth",
        "adjacents": ["B"]
    },
    {
        "id": "B",
        "name": "Beta",
        "terrain": "SEA",
        "school": "Mage",
        "loc_ability": "Tidecall",
        "adjacents": ["A", "C"]
    },
    {
        "id": "C",
        "name": "Gamma",
        "terrain": "MOUNTAIN",
        "school": "Warrior",
        "loc_ability": "Stone Skin",
        "adjacents": ["B"]
    }
]

def test_build_graph_from_data():
    gmap = GameMap()
    gmap.load_from_data(sample_locations)

    # #Test node count
    assert len(gmap.graph.nodes) == 3

    ## Test edge count
    assert len(gmap.graph.edges) == 2  

    ## Test node attributes
    node_a = gmap.graph.nodes["A"]
    assert node_a["name"] == "Alpha"
    assert node_a["terrain"] == "FOREST"
    assert node_a["school"] == "Druid"
    assert node_a["ability"] == "Regrowth"
    assert isinstance(node_a["monster"], list)

def test_graph_edges():
    gmap = GameMap()
    gmap.load_from_data(sample_locations)

    assert gmap.graph.has_edge("A", "B")
    assert gmap.graph.has_edge("B", "C")
    assert not gmap.graph.has_edge("A", "C")

def test_visual_does_not_crash():
    gmap = GameMap()
    gmap.load_from_data(sample_locations)
    try:
        gmap.visual()
    except Exception as e:
        pytest.fail(f"Visual method raised an exception: {e}")

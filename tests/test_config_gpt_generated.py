import pytest

# import everything from the module under test
# adjust the import path if needed
from mqlib_wrap.config import (
    analyse_and_desug_config,
    gen_problem_string,
    DEFAULT_RUNTIME_LIMIT,
    DEFAULT_SEED,
)

# ============================================================
# analyse_and_desug_config — BASIC VALID CASES
# ============================================================

def test_config_minimal():
    cfg = {
        "edges": [((0, 1), 1.0)]
    }

    out = analyse_and_desug_config(cfg)

    assert out["nodes_number"] == 2
    assert out["edges_number"] == 1
    assert out["nodes"] == {0: 0.0, 1: 0.0}
    assert out["edges"] == {(0, 1): 1.0}
    assert out["qubo_shift"] == 1.
    assert out["runtime_limit"] == DEFAULT_RUNTIME_LIMIT
    assert out["seed"] == DEFAULT_SEED
    assert out["graph"] == [[1], [0]]


def test_config_nodes_override_and_default_field():
    cfg = {
        "edges": [((0, 1), 2.0)],
        "nodes": {1: 3.5},
        "default_field": -1.0,
    }

    out = analyse_and_desug_config(cfg)

    assert out["nodes"] == {0: -1.0, 1: 3.5}
    assert out["qubo_shift"] == -0.5


def test_config_edge_normalization():
    cfg = {
        "edges": [((3, 1), -2.0)]
    }

    out = analyse_and_desug_config(cfg)

    assert out["edges"] == {(1, 3): -2.0}
    assert out["nodes_number"] == 4
    assert out["graph"] == [[], [3], [], [1]]


def test_config_zero_weight_edge_allowed():
    cfg = {
        "edges": [((0, 1), 0.0)]
    }

    out = analyse_and_desug_config(cfg)

    assert out["edges"] == {(0, 1): 0.0}
    assert out["graph"] == [[1], [0]]


# ============================================================
# analyse_and_desug_config — ERROR CASES
# ============================================================

def test_config_not_dict():
    with pytest.raises(TypeError):
        analyse_and_desug_config(123)


def test_config_missing_edges():
    with pytest.raises(ValueError):
        analyse_and_desug_config({})


def test_config_empty_edges():
    with pytest.raises(ValueError):
        analyse_and_desug_config({"edges": []})


def test_config_duplicate_edges():
    cfg = {
        "edges": [((0, 1), 1.0), ((1, 0), 2.0)]
    }
    with pytest.raises(ValueError):
        analyse_and_desug_config(cfg)


def test_config_invalid_node():
    cfg = {
        "edges": [((0, 1), 1.0)],
        "nodes": [(0, "x")],
    }
    with pytest.raises(ValueError):
        analyse_and_desug_config(cfg)


# ============================================================
# gen_problem_string — BASIC STRUCTURE
# ============================================================

def test_problem_string_basic_shape():
    cfg = analyse_and_desug_config({
        "edges": [((0, 1), 2.0)],
        "nodes": {0: 1.0, 1: -1.0},
    })

    s = gen_problem_string(cfg)
    lines = s.strip().splitlines()

    assert lines[0] == "2 3"

    assert len(lines) == 4


# ============================================================
# gen_problem_string — NUMERICAL CORRECTNESS
# ============================================================

def test_problem_string_known_values():
    # hand-checkable example
    # edge (0,1) = 2.0
    # node fields: f0=1, f1=-1
    cfg = analyse_and_desug_config({
        "edges": [((0, 1), 2.0)],
        "nodes": {0: 1.0, 1: -1.0},
    })

    s = gen_problem_string(cfg)
    lines = s.strip().splitlines()

    # diagonal terms
    # Q00 = -2*1 + 2*(2) = 2
    # Q11 = -2*(-1) + 2*(2) = 6
    diags = {tuple(map(int, l.split()[:2])): float(l.split()[2])
             for l in lines[1:] if l.split()[0] == l.split()[1]}

    assert diags[(1, 1)] == 2.0
    assert diags[(2, 2)] == 6.0

    # off-diagonal
    off = [l for l in lines[1:] if l.split()[0] != l.split()[1]]
    assert off == ["1 2 -4.0"]


# ============================================================
# gen_problem_string — CONSISTENCY / INVARIANTS
# ============================================================

def test_problem_string_uses_all_nodes():
    cfg = analyse_and_desug_config({
        "edges": [((2, 3), 1.0)],
        "nodes": {0: 0.5},
    })

    s = gen_problem_string(cfg)
    lines = s.strip().splitlines()

    # nodes_number = max(0,2,3)+1 = 4
    assert lines[0].startswith("4 ")

    # must contain 4 diagonal terms
    diag_lines = [l for l in lines[1:] if l.split()[0] == l.split()[1]]
    assert len(diag_lines) == 4

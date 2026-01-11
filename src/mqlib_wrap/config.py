import logging

logger = logging.getLogger(__name__)

HEURISTICS = {
    # Max-Cut heuristics
    "BASELINE",
    "BURER2002",
    "DESOUSA2013",
    "DUARTE2005",
    "FESTA2002G",
    "FESTA2002GPR",
    "FESTA2002GVNS",
    "FESTA2002GVNSPR",
    "FESTA2002VNS",
    "FESTA2002VNSPR",
    "LAGUNA2009CE",
    "LAGUNA2009HCE",

    # QUBO heuristics
    "ALKHAMIS1998",
    "BEASLEY1998SA",
    "BEASLEY1998TS",
    "GLOVER1998a",
    "GLOVER2010",
    "HASAN2000GA",
    "HASAN2000TS",
    "KATAYAMA2000",
    "KATAYAMA2001",
    "LODI1999",
    "LU2010",
    "MERZ1999CROSS",
    "MERZ1999GLS",
    "MERZ1999MUTATE",
    "MERZ2002GREEDY",
    "MERZ2002GREEDYKOPT",
    "MERZ2002KOPT",
    "MERZ2002ONEOPT",
    "MERZ2004",
    "PALUBECKIS2004bMST1",
    "PALUBECKIS2004bMST2",
    "PALUBECKIS2004bMST3",
    "PALUBECKIS2004bMST4",
    "PALUBECKIS2004bMST5",
    "PALUBECKIS2004bSTS",
    "PALUBECKIS2006",
    "PARDALOS2008",
}


DEFAULT_NODES = {}
DEFAULT_HEURISTICS = "all"
DEFAULT_RUNTIME_LIMIT = 10
DEFAULT_SEED = 42
DEFAULT_DEFAULT_FIELD = 0.


def get_or_default_and_warn(config, key, default_value):
    value = config.get(key)
    if value is None:
        logger.warning(f"{key} is not present in the config, set to default {default_value}")
        return default_value
    return value


def check_heuristics_list(heuristics):
    for heuristic in heuristics:
        if not isinstance(heuristic, str):
            raise TypeError(f"Heuristic must be a string, but got {heuristic} of type {type(heuristic)}")
        if heuristic not in HEURISTICS:
            raise ValueError(f"{heuristic} is unknown, it must be from the following set {HEURISTICS}")


def analyse_and_desug_heuristics(heuristics):
    if isinstance(heuristics, list):
        if heuristics and heuristics[0] == "all_but":
            check_heuristics_list(heuristics[1:])
            return list(h for h in HEURISTICS if h not in heuristics[1:])
        else:
            check_heuristics_list(heuristics)
            return list(heuristics)
    elif heuristics == "all":
        return list(HEURISTICS)
    else:
        raise TypeError(f"`heuristics` field must be a list or a string, but got {heuristics} of type {type(heuristics)}")


def is_not_non_negative_int(value):
    return not isinstance(value, int) or value < 0


def analyse_and_desug_runtime_limit(runtime_limit):
    if not isinstance(runtime_limit, int) or runtime_limit < 1:
        raise ValueError(f"Invalid `runtime_limit` field {runtime_limit}, must be a positive integer value")
    return runtime_limit


def analyse_and_desug_seed(seed):
    if is_not_non_negative_int(seed):
        raise ValueError(f"Invalid `seed` {seed}, must be a non-negative integer value")
    return seed


def is_not_number(value):
    return not isinstance(value, int) and not isinstance(value, float)


def analyse_and_desug_default_field(default_field):
    if is_not_number(default_field):
        raise TypeError(f"`default_field` must be a number, got {default_field} of type {type(default_field)}")
    return float(default_field)


def check_node(node):
    if not isinstance(node, (tuple, list)) \
       or len(node) != 2 \
       or is_not_non_negative_int(node[0]) \
       or is_not_number(node[1]):
        raise ValueError(f"Invalid `node_id` and `field` pair {node}, must be a pair of a non-negative `int` and a number")


def check_sequence_of_nodes(nodes_seq):
    for node in nodes_seq:
        check_node(node)


def analyse_and_desug_nodes(nodes):
    if isinstance(nodes, dict):
        check_sequence_of_nodes(nodes.items())
        return {node_id : float(ampl) for node_id, ampl in nodes.items()}
    elif isinstance(nodes, (list, tuple)):
        check_sequence_of_nodes(nodes)
        return {node_id : float(ampl) for node_id, ampl in nodes}
    else:
        raise TypeError(f"`nodes` must be dict or list or tuple, but got {nodes} of type {type(nodes)}")


def is_not_non_negative_int_pair(value):
    return not isinstance(value, (tuple, list)) \
        or len(value) != 2 \
        or value[0] == value[1] \
        or is_not_non_negative_int(value[0]) \
        or is_not_non_negative_int(value[1])


def check_edge(edge):
    if not isinstance(edge, (tuple, list)) \
       or len(edge) != 2 \
       or is_not_non_negative_int_pair(edge[0]) \
       or is_not_number(edge[1]):
        raise ValueError(f"Invalid pair of edge and amplitude {edge}, it must be a pair of the pair of non-repeated non-negative integers and a number")


def analyse_edges_sequence(edges):
    seen_edges = set()
    for edge in edges:
        check_edge(edge)
        (lhs_id, rhs_id), ampl = edge
        if (lhs_id, rhs_id) in seen_edges:
            raise ValueError(f"Duplicated edge {(lhs_id, rhs_id)}")
        seen_edges.add((lhs_id, rhs_id))
        seen_edges.add((rhs_id, lhs_id))
        yield (min(lhs_id, rhs_id), max(lhs_id, rhs_id)), float(ampl)


def analyse_and_desug_edges(edges):
    if isinstance(edges, dict):
        edges_seq = edges.items()
    elif isinstance(edges, (list, tuple)):
        edges_seq = edges
    else:
        raise TypeError(f"`edges` must be a dict or list or tuple, got {edges} of type {type(edges)}")
    if not edges:
        raise ValueError("`edges` field must not contain empty container")
    return dict(analyse_edges_sequence(edges_seq))


def get_nodes_number(edges, nodes):

    def gen_node_ids():
        yield from nodes.keys()
        for lhs_id, rhs_id in edges.keys():
            yield lhs_id
            yield rhs_id

    return max(gen_node_ids()) + 1


def make_graph(nodes_number, edges):
    graph = [list() for _ in range(nodes_number)]
    for lhs_id, rhs_id in edges:
        graph[lhs_id].append(rhs_id)
        graph[rhs_id].append(lhs_id)
    return graph


def analyse_and_desug_config(config):
    if not isinstance(config, dict):
        raise TypeError(f"Input config must be a dictionary, but its actual type is {type(config)}")
    raw_edges = config.get("edges")
    if raw_edges is None:
        raise ValueError("`edges` field must be present in the config")
    default_field = analyse_and_desug_default_field(get_or_default_and_warn(config, "default_field", DEFAULT_DEFAULT_FIELD))
    edges = analyse_and_desug_edges(raw_edges)
    _nodes = analyse_and_desug_nodes(get_or_default_and_warn(config, "nodes", DEFAULT_NODES))
    heuristics = analyse_and_desug_heuristics(get_or_default_and_warn(config, "heuristics", DEFAULT_HEURISTICS))
    runtime_limit = analyse_and_desug_runtime_limit(get_or_default_and_warn(config, "runtime_limit", DEFAULT_RUNTIME_LIMIT))
    seed = analyse_and_desug_seed(get_or_default_and_warn(config, "seed", DEFAULT_SEED))
    nodes_number = get_nodes_number(edges, _nodes)
    nodes = {node_id : _nodes.get(node_id, default_field) for node_id in range(nodes_number)}
    qubo_shift = sum(edges.values()) - sum(nodes.values())
    graph = make_graph(nodes_number, edges)
    return {
        "nodes_number" : nodes_number,
        "edges_number" : len(edges),
        "nodes" : nodes,
        "edges" : edges,
        "graph" : graph,
        "qubo_shift" : qubo_shift,
        "heuristics" : heuristics,
        "runtime_limit" : runtime_limit,
        "seed" : seed,
    }


def gen_problem_string(config):
    nodes = config["nodes"]
    edges = config["edges"]
    graph = config["graph"]
    nodes_number = config["nodes_number"]
    edges_number = config["edges_number"]

    def make_qubo_edges_iter():
        for (lhs, rhs), ampl in edges.items():
            yield (lhs + 1, rhs + 1), -2 * ampl

    def get_neighbors_ampls_iter(node_id):
        for other_id in graph[node_id]:
            edge_id = min(node_id, other_id), max(node_id, other_id)
            yield edges[edge_id]

    def make_qubo_nodes_iter():
        for node_id, ampl in nodes.items():
            neighbors_field_shift = sum(get_neighbors_ampls_iter(node_id))
            yield node_id + 1, -2 * ampl + 2 * neighbors_field_shift
    
    def gen_string():
        yield str(nodes_number) + " " + str(edges_number + nodes_number) + "\n"
        for node_id, ampl in make_qubo_nodes_iter():
            yield str(node_id) + " " + str(node_id) + " " + str(ampl) + "\n"
        for (lhs_id, rhs_id), ampl in make_qubo_edges_iter():
            yield str(lhs_id) + " " + str(rhs_id) + " " + str(ampl) + "\n"

    return "".join(gen_string())


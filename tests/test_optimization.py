from itertools import product
from mqlib_wrap import run_heuristics, get_energy_function
from mqlib_wrap.config import analyse_and_desug_config


def get_all_states_iter(nodes_number):
    return product((1, -1), repeat=nodes_number)

def minimize_bruteforce(config):
    config = analyse_and_desug_config(config)
    nodes_number = config["nodes_number"]
    energy_function = get_energy_function(config)
    return min(map(lambda s: (energy_function(s), list(s)), get_all_states_iter(nodes_number)), key = lambda x: x[0])
    

def test_optimization():
    config = {
        "edges" : {(0, 1) : 1.,
                   (1, 2) : -1.,
                   (2, 0) : 1.,
                   (3, 2) : 0.45,
                   (1, 4) : -0.6,
                   (4, 3) : 1.1},
        "nodes" : {1 : 0.3, 4 : -0.3},
        "default_field" : -0.6,
        "heuristics" : "all",
        "runtime_limit" : 1,
    }
    results = run_heuristics(config)
    energy_function = get_energy_function(config)
    for _, result in results.items():
        energy, configuration = result["energy"], result["configuration"]
        assert abs(energy - energy_function(configuration)) < 1e-10
    correct_min, correct_argmin = minimize_bruteforce(config)
    best_result = min(results.items(), key = lambda x: x[1]["energy"])
    best_min = best_result[1]["energy"]
    best_argmin = best_result[1]["configuration"]
    assert abs(correct_min - best_min) < 1e-10
    assert correct_argmin == best_argmin

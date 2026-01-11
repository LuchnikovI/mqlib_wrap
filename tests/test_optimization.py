from mqlib_wrap import run_heuristics, get_energy_function

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

from functools import reduce
import logging
import tempfile
from pathlib import Path
from subprocess import run

from mqlib_wrap.config import analyse_and_desug_config, gen_problem_string

logger = logging.getLogger(__name__)

MQLIB_PATH = Path.home() / ".mqlib_bin" / "MQLib"

def _run_heuristic(config, heuristic):
    problem_string = gen_problem_string(config)
    runtime_limit = str(config["runtime_limit"])
    seed = str(config["seed"])
    with tempfile.NamedTemporaryFile() as f:
        f.write(bytes(problem_string, "utf-8"))
        f.flush()
        problem_path = f.name
        cmd_args = [MQLIB_PATH, "-fQ", problem_path, "-h", heuristic, "-r", runtime_limit, "-s", seed, "-ps"]
        result = run(cmd_args, capture_output=True)
        if result.stderr:
            logger.warning(f"stderr message appeared during MQLib execution: {result.stderr}")
        lines = result.stdout.split(sep=b"\n")
        energy = -float(lines[0].split(sep=b",")[3]) + config["qubo_shift"]
        configuration = list(map(lambda x: 2 * int(x) - 1, lines[-2].split(b" ")))
        return {"energy" : energy, "configuration" : configuration}


def _run_heuristics(config):
    heuristics = config["heuristics"]
    results = {}
    for heuristic in heuristics:
        logger.debug(f"Running {heuristic} heuristic")
        result = _run_heuristic(config, heuristic)
        logger.debug(f"Heuristic {heuristic} finished, best energy {result["energy"]}")
        results[heuristic] = result
    return results


def run_heuristics(config):
    analysed_config = analyse_and_desug_config(config)
    return _run_heuristics(analysed_config)


def get_energy_function(config):
    analysed_config = analyse_and_desug_config(config)
    nodes_number = analysed_config["nodes_number"]
    edges = analysed_config["edges"]
    nodes = analysed_config["nodes"]

    def energy_function(configuration):
        if isinstance(configuration, (list, tuple)) and len(configuration) == nodes_number:
            for var in configuration:
                if var != 1 and var != -1:
                    raise ValueError(f"Value {var} of avariable in configuration is invalid, must be 1 or -1")
            def interaction_energy_reduction_func(energy, edge_ampl):
                (lhs, rhs), ampl = edge_ampl
                return energy + configuration[lhs] * configuration[rhs] * ampl

            def local_energy_reduction_func(energy, node_ampl):
                node_id, ampl = node_ampl
                return energy + configuration[node_id] * ampl

            return reduce(
                interaction_energy_reduction_func,
                edges.items(),
                reduce(local_energy_reduction_func, nodes.items(), 0.))
        else:
            raise ValueError(f"Invalid configuration {configuration}, must be a list or tuple of length {nodes_number}")

    return energy_function

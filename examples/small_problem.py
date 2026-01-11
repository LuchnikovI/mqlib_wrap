import logging
from mqlib_wrap import run_heuristics

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

config = {
    "edges" : {(0, 1) : 1.,
               (1, 2) : -1.,
               (2, 0) : 1.,},
    "nodes" : {1 : 0.3},
    "default_field" : -1.,
    "heuristics" : "all",
    "runtime_limit" : 1,
    "seed" : 42
}

print(run_heuristics(config))

import logging
from mqlib_wrap import run_heuristics

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Here is the config that specifies parameters. Most of parameters are optional, if they are missed
# one drops a warning and set a default value.

config = {
    "edges" : {(0, 1) : 1., # --------> `edges` specifies interaction constants per edge,
               (1, 2) : -1., #           one does not allows duplication (e.g. (0,1) and (1,0))
               (2, 0) : 1.,}, #          in edges. The format is rather flexible, one can provide
                              #          list of pairs (two element tuples) of tuple of pairs
                              #          in place of this dict

    "nodes" : {1 : 0.3}, # ------------> `nodes` specifies local magnetic fields. If node is missed
                         #               the `default_field` value is set. `nodes` is optional, default
                         #               value is {}

    "default_field" : -1., # ----------> `default_field` specifies default value of local magnetic field
                           #             `default_field` is optional, default value is 0.

    "heuristics" : "all",  # ----------> `heuristics` specifies heuristics being run, if it is equal `all`
                           #             all heuristics are being run, one can set it to a list with names
                           #             of heuristics, in this case those heuristics are being run,
                           #             one can also set it to a list where first value is `all_but` flolowed
                           #             by names of heuristics, in this case all heuristics are being run
                           #             except those in the list. This field is optional, default value is
                           #             `all`

    "runtime_limit" : 1, # ------------> runtime limit in seconds for every heuristic, it is optional
                         #               default value is 10

    "seed" : 42 # ---------------------> random seed, it is optional, default value is 42
}

print(run_heuristics(config))

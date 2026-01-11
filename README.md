## What is it?
This is a minimal python wrapper for [MQLib](https://github.com/MQLib/MQLib) which is a library of heuristics for solving MaxCut and QUBO problems. It wraps binary executable for simplicity.

## What does it do?
It solves the following minimization problem
$$\underset{x_i \in \{-1, 1\}}{\rm minimize} \ \sum_{(i, j) \in E,\ i<j} J_{ij} x_ix_j + \sum_{i\in V} h_i x_i,$$
where $E$ is edges, $V$ is nodes in a problem graph $G = (V, E)$, $J_ij$ is an interaction strength, and $h_i$ is a local magnetic field.

## How to use it?
The library exposes two functions `run_heuristics` and `get_energy_function`. `run_heuristics` accepts a configuration (a dict) that specifies the optimization problem and parameters of the selected MQLib solvers, executes the solvers, and returns the resulting solutions. `get_energy_function` accepts the same configuration and returns a callable that evaluates the energy for a given spin configuration. For more details on the fortmat of the configuration see `examples/small_problem.py`

## How to install?
1) Clone this repo;
2) The library requires MQLib executable, to install the executable run `./ensure_mqlib.py` from the repo root. To uninstall the executable run `./muninstall_mqlib.py`;
3) Run `pip install .` from the clonned repo under your virtual environment.

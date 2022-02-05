# Leafcutter Ants Fungi Mutualism Agent-Based Model
An agent-based model to study the dynamics of the mutualism between leafcutter ants and their fungus garden.
It is implemented using the [Mesa](https://mesa.readthedocs.io/en/latest/) framework.

## Demo
<p align="center">
  <img width="500" height="500" src="leafcutter_ants_fungi_mutualism/figures/demo.gif">
</p>

## Installation
To install the dependencies using pip, use the following command
```bash
$ pip install -r requirements.txt
```
This will install all dependencies to require the model and notebooks (used for
analyzing and visualizing data)

## How to run
To run the model interactively in the browser, run the following command in the
root directory
```bash
$ mesa runserver
```
This will start a webserver at http://127.0.0.1:8521 which you can visit using
your browser.


Alternatively, one can run the model directly without live visualization by
using `leafcutter_ants_fungi_mutualism/run_model.py`. This is significantly
faster and persists the collected data. The usage is as follows
```
usage: run_model.py [-h] [-r REPETITIONS] [-t TIME_STEPS] [-n N_CORES]
                    [-c COLLECT_TIMESERIES]
                    output_file

Leafcutter Ants Fungy Mutualism model runner

positional arguments:
  output_file           location of output file

optional arguments:
  -h, --help            show this help message and exit
  -r REPETITIONS, --repetitions REPETITIONS
                        number of repeated model runs
  -t TIME_STEPS, --time-steps TIME_STEPS
                        number of time steps to execute
  -n N_CORES, --n-cores N_CORES
                        number of processes to use in pool
  -c COLLECT_TIMESERIES, --collect-timeseries COLLECT_TIMESERIES
                        collect timeseries data
```

## Mesa Changes
In order to use the parallelized version of Mesa's [BatchRunner](https://mesa.readthedocs.io/en/latest/apis/batchrunner.html),
we apply one of the fixes proposed in [mesa/#1107](https://github.com/projectmesa/mesa/issues/1107).
The fixed `BatchRunnerMP` is available in
`leafcutter_ants_fungi_mutualism/batchrunner.py`.

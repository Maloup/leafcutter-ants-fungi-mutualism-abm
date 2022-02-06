#! /usr/bin/env python3

import time
import argparse
import multiprocess as mp
import numpy as np
from itertools import product

from model import LeafcutterAntsFungiMutualismModel
from batchrunner import BatchRunnerMP

fixed_parameters = {'collect_data': True,
                    'width': 50,
                    'height': 50,
                    'num_ants': 50,
                    #For experiment 2 num_plants {30, 60, 120}, for experiment 1: 64
                    'num_plants': 64,
                    'pheromone_lifespan': 30,
                     #For experiment 2 num_plant_leaves {100, 50, 25}, for experiment 1: 100
                    'num_plant_leaves': 100 ,
                    'initial_foragers_ratio': 0.5,
                    'leaf_regrowth_rate': 0.5,
                    'ant_death_probability': 0.01,
                    'initial_fungus_energy': 50,
                    'fungus_decay_rate': 0.005,
                    'energy_biomass_cvn': 2.0,
                    'fungus_larvae_cvn': 0.9,
                    'energy_per_offspring': 1.0,
                    'fungus_biomass_death_threshold': 5.0,
                    'max_fitness_queue_size': 10,
                    'caretaker_carrying_amount': 1,
                    'caretaker_roundtrip_mean': 5.0,
                    'caretaker_roundtrip_std': 5.0,
                    'dormant_roundtrip_mean': 60.0,
}


def run_model(args):
    model, args = args
    m = model(**fixed_parameters)

    while m.running and m.schedule.steps < args["time_steps"]:
        m.step()

    return m


def run_model_parallel(args):
    n_cores = args["n_cores"]
    if n_cores is None:
        n_cores = mp.cpu_count()

    repetitions = args["repetitions"]
    results = []
    trip_durations = []

    with mp.Pool(n_cores) as pool:
        for model in pool.imap_unordered(
            run_model,
            [(LeafcutterAntsFungiMutualismModel, args) for _ in range(repetitions)]
        ):
            results.append(model.datacollector.get_model_vars_dataframe().to_dict())
            trip_durations.append(model.trip_durations)

    return results, trip_durations


def main(args):
    start = time.time()
    results, trip_durations = run_model_parallel(args)
    end = time.time()

    print(f"Done! Took {end - start}")
    print(f"------ Saving data to {args['output_file']} --------")
    np.savez(args["output_file"], results=results, trip_durations=trip_durations)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Leafcutter Ants Fungy Mutualism model runner")

    argparser.add_argument("output_file", type=str, help="location of output file")
    argparser.add_argument("-r", "--repetitions", type=int, default=1,
                           help="number of repeated model runs")
    argparser.add_argument("-t", "--time-steps", type=int, default=1000,
                           help="number of time steps to execute")
    argparser.add_argument("-n", "--n-cores", type=int, default=None,
                           help="number of processes to use in pool")
    argparser.add_argument("-c", "--collect-timeseries", type=bool,
                           default=True, help="collect timeseries data")

    args = vars(argparser.parse_args())

    main(args)

#! /usr/bin/env python3

import time
import argparse
import multiprocess as mp
import numpy as np
from itertools import product

from model import LeafcutterAntsFungiMutualismModel
from batchrunner import BatchRunnerMP


def run_model(args):
    model, args = args
    m = model(**{"collect_data": args["collect_timeseries"]})

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
            [(LeafcutterAntsFungiMutualismModel, args)
             for _ in range(repetitions)]
        ):
            results.append(
                model.datacollector.get_model_vars_dataframe().to_dict())
            trip_durations.append(model.trip_durations)

    return results, trip_durations


def main(args):
    start = time.time()
    results, trip_durations = run_model_parallel(args)
    end = time.time()

    print(f"Done! Took {end - start}")
    print(f"------ Saving data to {args['output_file']} --------")
    np.savez(args["output_file"], results=results,
             trip_durations=trip_durations)


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(
        description="Leafcutter Ants Fungy Mutualism model runner")

    argparser.add_argument("output_file", type=str,
                           help="location of output file")
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

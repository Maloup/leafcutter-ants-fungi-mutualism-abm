"""
One-Factor-At-a-Time (OFAT) (local) sensitivity analysis, based on methods provided by the SA notebook and the article of ten Broeke (2016)
Script to run OFAT using BatchRunnerMP and save data in the folder data/OFAT

Run script as Python3 OFAT.py filename n_cores

where n_cores specifies the number of cores to use for multiprocessing
"""
from model import LeafcutterAntsFungiMutualismModel, track_ants, track_leaves, track_ratio_foragers
from model import track_ants_leaves, track_dormant_ants
from batchrunner import BatchRunnerMP
import pandas as pd
import numpy as np

import os
import sys
from tqdm import tqdm

if not os.path.exists('data/OFAT'):
    os.makedirs('data/OFAT')
if not os.path.exists('figures/OFAT'):
    os.makedirs('figures/OFAT')


def collect_OFAT_data(fileName, problem, model_reporters, fixed_parameters,
                      repetitions=5, time_steps=100, distinct_samples=5,
                      save_data=True):
    """
    Function that collects data for the OFAT sensitivity analysis and save the data
    when save_data is set to true
    """

    # create a dictionary where each dataframe is saved as the value of key
    # variable name
    data = {}

    for var in tqdm(problem.keys()):
        # get the sample for this variable
        samples = np.linspace(
            *problem[var][1], num=distinct_samples, dtype=problem[var][0])

        # remove this parameter from the fixed parameter dictionary
        fixed_params_copy = fixed_parameters.copy()
        del fixed_params_copy[var]

        batch = BatchRunnerMP(LeafcutterAntsFungiMutualismModel,
                              max_steps=max_steps,
                              iterations=repetitions,
                              variable_parameters={var: samples},
                              fixed_parameters=fixed_params_copy,
                              model_reporters=model_reporters,
                              display_progress=False,
                              nr_processes=int(sys.argv[2])
                              )

        batch.run_all()

        data[var] = batch.get_model_vars_dataframe()

    if save_data:
        np.savez('data/OFAT/' + fileName, data=data, problem=problem,
                 model_reporters=list(model_reporters.keys()), fixed_parameters=fixed_parameters)

    return data


if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("no filename specified and no nr of cores specified")
        print("please run as python3 OFAT.py filname n_cores")
        sys.exit(-1)
    elif len(sys.argv) < 3:
        print("no filename OR no nr of cores specified")
        print("please run as python3 OFAT.py filname n_cores")
        sys.exit(-1)

    # define the parameters and ranges to run OFAT for
    problem = {'num_ants': [int, [10, 100]],
               'num_plants': [int, [30, 200]],
               'pheromone_lifespan': [int, [5, 100]],
               'num_plant_leaves': [int, [10, 200]],
               'initial_foragers_ratio': [float, [0.1, 1.0]],
               'leaf_regrowth_rate': [float, [0.01, 1.0]],
               'ant_death_probability': [float, [0, 0.02]],
               'initial_fungus_energy': [float, [10, 100]],
               'fungus_decay_rate': [float, [0.001, 0.02]],
               'energy_biomass_cvn': [float, [1, 4]],
               'fungus_larvae_cvn': [float, [0.2, 1.5]],
               'energy_per_offspring': [float, [0.5, 1.5]],
               'max_fitness_queue_size': [int, [1, 20]],
               'caretaker_carrying_amount': [float, [0.1, 2]],
               'dormant_roundtrip_mean': [float, [30, 80]],
               'caretaker_roundtrip_mean': [float, [5, 20]]
               }

    # obtain nominal model parameters
    model = LeafcutterAntsFungiMutualismModel()
    default_pheromone_lifespan = model.pheromone_lifespan

    # set the output variables
    model_reporters = {"Ants_Biomass": track_ants,
                       "Fungus_Biomass": lambda m: m.fungus.biomass,
                       "Fraction forager ants": track_ratio_foragers,
                       "Available leaves": track_leaves,
                       "Dormant caretakers fraction": track_dormant_ants,
                       "Death reason": lambda m: m.death_reason,
                       }

    # set fixed parameters, eg collect_data = False
    fixed_parameters = {'collect_data': False,
                        'width': 50,
                        'height': 50,
                        'num_ants': 50,
                        'num_plants': 64,
                        'pheromone_lifespan': 30,
                        'num_plant_leaves': 100,
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

    # estimation floor comp 2,5h
    repetitions = 64
    max_steps = 1000
    distinct_samples = 10

    fileName = f"reps{repetitions}maxtime{max_steps}distinctsam{distinct_samples}" + \
        sys.argv[1]

    collect_OFAT_data(fileName, problem, model_reporters, fixed_parameters,
                      repetitions=repetitions, time_steps=max_steps, distinct_samples=distinct_samples,
                      save_data=True)

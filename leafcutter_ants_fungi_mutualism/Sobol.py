"""
Sobol' (global) sensitivity analysis, based on methods provided by the SA notebook and the article of ten Broeke (2016)
Script to run Sobol' SA and save data
"""
from model import LeafcutterAntsFungiMutualismModel, track_ants, track_leaves, track_ratio_foragers
from mesa.batchrunner import BatchRunner
import pandas as pd
import numpy as np
import os, sys

import time
import argparse
import multiprocess as mp
from itertools import product


from SALib.sample import saltelli
from SALib.analyze import sobol

if not os.path.exists('data/Sobol'):
    os.makedirs('data/Sobol')
if not os.path.exists('figures/Sobol'):
    os.makedirs('figures/Sobol')

repetitions = 5
max_steps = 100
distinct_samples = 5


# from https://salib.readthedocs.io/en/latest/basics.html


# define the parameters and ranges in a way that is not confusing; uncomment parameters to include in analysis
problem = { #'num_ants': [int, [10,100]],
            #'num_plants': [int, [50,200]], 
            #'pheromone_lifespan': [int, [5, 100]],
            #'num_plant_leaves': [int, [10, 200]],
            #'initial_foragers_ratio': [float, [0.1, 1.0]], 
            #'leaf_regrowth_rate': [float, [0.01, 1.0]],
            'ant_death_probability': [float, [0, 0.02]],
            #'initial_fungus_energy': [float, [10, 100]],
            'fungus_decay_rate': [float, [0.001, 0.02]], 
            'energy_biomass_cvn': [float, [1, 4]], 
            'fungus_larvae_cvn': [float, [0.5, 1.5]],
            'max_fitness_queue_size': [int, [1, 20]],
            'caretaker_carrying_amount': [float, [0.1, 2]],
            #'dormant_roundtrip_mean': [float, [30, 80]],
            #'caretaker_roundtrip_mean': [float, [5, 20]]
}

# SALib's saltelli sampler wants it in another format so here we go
problem_sampler = {
    'num_vars': len(problem),
    'names': [key for key in sorted(problem.keys())],
    'bounds': [problem[key][1] for key in sorted(problem.keys())]
}

# set fixed parameters, eg collect_data = False. this includes all parameters not in problem
fixed_parameters = {'collect_data': False,
                    'width': 50,
                    'height': 50,
                    'num_ants': 50,
                    'num_plants': 100, 
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
                    'fungus_biomass_death_threshold': 5,
                    'max_fitness_queue_size': 20,
                    'caretaker_carrying_amount': 1,
                    'caretaker_roundtrip_mean': 5.0, 
                    'caretaker_roundtrip_std': 5.0,
                    'dormant_roundtrip_mean': 60.0,
}

# remove problem parameters from dictionary of fixed parameters
for key in problem.keys():
    del fixed_parameters[key]

##### ?????? ######
# The SA notebook does this, which is very different implementation than the example of the read the docs????
repetitions = 10
max_steps = 100
distinct_samples = 10

# param_values = saltelli.sample(problem_sampler, distinct_samples)
# shouldnt the "N" passed to saltelli.sample be a power of 2, otherwise the Sobol' sequence isn't valid????
""" /home/floor/.local/lib/python3.8/site-packages/SALib/sample/saltelli.py:94: UserWarning: 
        Convergence properties of the Sobol' sequence is only valid if
        `N` (10) is equal to `2^n`.
        
  warnings.warn(msg) """

# according to the readthedocs from SALib
# generate samples from the parameter space using saltelli sampler from SALib
# param_values = saltelli.sample(problem_sampler, 8)
# print(param_values.shape)
# print(type(param_values))

# np.savetxt('data/Sobol/saltellisample', param_values)





def run_model(args):#, problem_sampler, parameter_setting, fixed_parameters, i):

    model, args, problem_sampler, parameter_setting, fixed_parameters, i = args
    
    var_param = {}
    for key, val in zip(problem_sampler['names'], parameter_setting):
        var_param[key] = val
    # model = LeafcutterAntsFungiMutualismModel(**var_param, **fixed_parameters)
    # model, args = args
    m = model(**var_param, **fixed_parameters)

    while m.running and m.schedule.steps < args["time_steps"]:
        m.step()

    return m, i


def run_model_parallel(args):
    n_cores = args["n_cores"]
    if n_cores is None:
        n_cores = mp.cpu_count()

    # load the sample
    param_values = np.loadtxt('data/Sobol/saltellisample' + args['output_file'])

    results = np.zeros((len(param_values), 4))

    with mp.Pool(n_cores) as pool:
        for model, ix in pool.imap_unordered(
            run_model,
            [(LeafcutterAntsFungiMutualismModel, args, problem_sampler, param_values[i], fixed_parameters, i) for i in range(len(param_values))]
        ):
            results[ix] = model.fungus.biomass, track_ants(model), track_ratio_foragers(model), track_leaves(model), 

    return results


def main(args):
    start = time.time()
    results = run_model_parallel(args)
    end = time.time()

    print(f"Done! Took {end - start}")
    print(f"------ Saving data to {args['output_file']} --------")
    np.savez('data/Sobol/'+args["output_file"], results=results, fixed_parameters=fixed_parameters, problem=problem_sampler)

    


if __name__ == "__main__":
    argparser = argparse.ArgumentParser(description="Leafcutter Ants Fungy Mutualism model runner")

    argparser.add_argument("output_file", type=str, help="location of output file")
    # argparser.add_argument("input_sample", type=str, help="location of saltelli sample")    

    argparser.add_argument("-s", "--saltelli-sample", type=int, default=1024,
                           help="length of saltelli sample, preferrably power of 2")
    argparser.add_argument("-t", "--time-steps", type=int, default=1000,
                           help="number of time steps to execute")
    argparser.add_argument("-n", "--n-cores", type=int, default=None,
                           help="number of processes to use in pool")

    args = vars(argparser.parse_args())

    param_values = saltelli.sample(problem_sampler, args['saltelli_sample'], calc_second_order=False)
    # print(param_values.shape)
    # print(type(param_values))

    np.savetxt('data/Sobol/saltellisample' + args['output_file'], param_values)


    main(args)


























# this gives a Numpy matrix of 8000 by 3
# the saltelli sampler generates N*(2D+2) samples, where N = 1024 in this example and 
# D is the number of model inputs
# keyword argument: calc_second_order=False will exclude second-order indices, resulting in a smaller sample matrix
# with N*(D+2) rows instead

# run model
# save the samples to a text file:
# np.savetxt("data/Sobol/param_values.txt", param_values)
# each line in param_values is one input to the model
# the output should be saved to another file with a similar format: one output on each line. 
# the outputs can then be loaded with 
# Y = np.loadtxt("outputs.txt", float)

# so if we want to paralellize this among ourselves, we need to split up the param_values textfile
# then run the model, which can be done in python
# then save the outputs, however, they need to be on the same line as the parameter values (I assume!!)

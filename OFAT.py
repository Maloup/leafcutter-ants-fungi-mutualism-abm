"""
One-Factor-At-a-Time (OFAT) (local) sensitivity analysis, based on methods provided by the SA notebook and the article of ten Broeke (2016)

Script to run OFAT and save data

"""
from leafcutter_ants_fungi_mutualism.model import LeafcutterAntsFungiMutualismModel, track_ants, track_leaves, track_ratio_foragers
from mesa.batchrunner import BatchRunner, BatchRunnerMP
import pandas as pd
import numpy as np
# import matplotlib.pyplot as plt
# import seaborn as sns
import os, sys
from tqdm import tqdm

if not os.path.exists('Data/OFAT'):
    os.makedirs('Data/OFAT')
if not os.path.exists('Figures/OFAT'):
    os.makedirs('Figures/OFAT')



def collect_OFAT_data(fileName, problem, model_reporters, fixed_parameters, 
                      repetitions=5, time_steps=100, distinct_samples=5, 
                      save_data=True):
    """
    Function that collects data for the OFAT sensitivity analysis and save the data
    when save_data is set to true
    """

    # create a dictionary where each dataframe is saved as the value of key variable name
    data = {}

    for var in tqdm(problem.keys()):
        # get the sample for this variable
        samples = np.linspace(*problem[var][1], num=distinct_samples, dtype=problem[var][0])

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
                             nr_processes = 8)

        batch.run_all()

        data[var] = batch.get_model_vars_dataframe()

    if save_data:
        np.savez('Data/OFAT/' + fileName, data=data, param_data=(problem, model_reporters, fixed_parameters))

    return data

def plot_param_var_conf(ax, df, var, param, i):
    """
    Modified from the Sensitivity Analysis notebook provided by the course Agent-based-modelling
    
    Helper function for plot_all_vars. Plots the individual parameter vs
    variables passed.

    Args:
        ax: the axis to plot to
        df: dataframe that holds the data to be plotted
        var: variables to be taken from the dataframe
        param: which output variable to plot
    """
    x = df.groupby(var).mean().reset_index()[var]
    y = df.groupby(var).mean()[param]

    repetitions = df.groupby(var)[param].count()
    minimum = df.groupby(var)[param].min()
    maximum = df.groupby(var)[param].max()
    
    stdev = df.groupby(var)[param].std()

    ax.scatter(x, y, c='k', marker='o')
#     ax.plot(x, y, c='k', marker='o', linewidth = 0.8)
#     ax.fill_between(x, y - stdev, y + stdev, color='grey', alpha=0.2)
    ax.vlines(x, y-stdev, y + stdev, color='grey')
    
    
#     ax.plot(x, minimum, c='magenta', marker='x', linewidth = 0.8)
#     ax.plot(x, maximum, c='deepskyblue', marker='+', linewidth = 0.8)
    ax.scatter(x, minimum, c='magenta', marker='x')
    ax.scatter(x, maximum, c='deepskyblue', marker='+')

    ax.set_xlabel(var)
    ax.set_ylabel(param)

def plot_all_vars(data, model_reporters, save_fig=False, show_fig=True):
    """
    
    """

    fig, axs = plt.subplots(len(data.keys()),len(model_reporters.keys()), figsize=(15, 50))
    
    for row, var in enumerate(data.keys()):
        for col, output_param in enumerate(model_reporters.keys()):
            plot_param_var_conf(axs[row,col], data[var], var, output_param, col)
    
    if save_fig:
        fig.savefig('Figures/OFAT/' + fileName + '.svg')

    if show_fig:
        plt.show()

def recover_OFAT_data(fileName):
    """
    Recovers data saved in collect_OFAT_data function
    """
    return dict(np.load('Data/OFAT/' + fileName + '.npz', allow_pickle=True))['arr_0'][()]
    

# collect_data=True, num_ants=50, num_plants=30, width=20,
#                  height=50, pheromone_lifespan=30, num_plant_leaves=100,
#                  initial_foragers_ratio=0.5, leaf_regrowth_rate=1/2,
#                  ant_death_probability=0.01, initial_fungus_energy=50,
#                  fungus_decay_rate=0.005, energy_biomass_cvn=2.0,
#                  fungus_larvae_cvn=0.9, energy_per_offspring=1.0,
#                  fungus_biomass_death_threshold=5.0, fungus_feed_threshold=5.0,
#                  caretaker_carrying_amount=1, max_fitness_queue_size=20)



if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("no filename specified")
        sys.exit(-1)
    



    # define the parameters and ranges to run OFAT for
    problem = {'num_ants': [int, [10,100]],
               'num_plants': [int, [40,200]], 
               'pheromone_lifespan': [int, [5, 100]],
               'num_plant_leaves': [int, [10, 200]],
               'initial_foragers_ratio': [float, [0.1, 1.0]], 
               'leaf_regrowth_rate': [float, [0.01, 1.0]],
               'ant_death_probability': [float, [0, 0.02]],
               'initial_fungus_energy': [float, [10, 100]],
               'fungus_decay_rate': [float, [0.001, 0.1]], 
               'energy_biomass_cvn': [float, [1, 4]], 
               'fungus_larvae_cvn': [float, [0.5, 1.5]],
               'energy_per_offspring': [float, [0.5, 1.5]],
               'max_fitness_queue_size': [int, [1, 20]],
               'caretaker_carrying_amount': [float, [0.1, 2]],
               'dormant_roundtrip_mean': [float, [30, 80]]
    }

    # problem = {'num_ants': [int, [10,100]],
    #            'num_plants': [int, [10,100]], 
    #            'num_plant_leaves': [int, [10, 200]],
    #            'leaf_regrowth_rate': [float, [0.01, 1.0]],
    #            'ant_death_probability': [float, [0, 0.02]],
    #            'fungus_decay_rate': [float, [0.001, 0.1]], 
    #            'energy_biomass_cvn': [float, [1, 4]], 
    #            'fungus_larvae_cvn': [float, [0.5, 1.5]],
    #            'energy_per_offspring': [float, [0.5, 1.5]],
    #            'caretaker_carrying_amount': [float, [0.5, 2]],
    # }

    # obtain nominal model parameters
    model = LeafcutterAntsFungiMutualismModel()
    default_pheromone_lifespan = model.pheromone_lifespan


    # set the output variables
    model_reporters = {"Ants_Biomass": track_ants,
                       "Fungus_Biomass": lambda m: m.fungus.biomass,
                       "Fraction forager ants": track_ratio_foragers,
    }

    # set fixed parameters, eg collect_data = False
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
                         'fungus_larvae_cvn': 1.4,
                         'energy_per_offspring': 1.0,
                         'fungus_biomass_death_threshold': 5,
                         'max_fitness_queue_size': 10,
                         'caretaker_carrying_amount': 1,
                         'caretaker_roundtrip_mean': 5.0, 
                         'caretaker_roundtrip_std': 5.0,
                         'dormant_roundtrip_mean': 60.0,
    }

    # estimation floor comp 2,5h
    repetitions = 10
    max_steps = 1000
    distinct_samples = 10

    fileName = f"reps{repetitions}maxtime{max_steps}distinctsam{distinctsamples}" + sys.argv[1]


    collect_OFAT_data(fileName, problem, model_reporters, fixed_parameters, 
                      repetitions=repetitions, time_steps=max_steps, distinct_samples=distinct_samples, 
                      save_data=True)

    # data = recover_OFAT_data(fileName)

    # plot_all_vars(data, model_reporters)

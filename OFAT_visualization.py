import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from leafcutter_ants_fungi_mutualism.model import LeafcutterAntsFungiMutualismModel, track_ants, track_leaves, track_ratio_foragers

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

def plot_all_vars(data, model_reporters, save_fig=True, show_fig=False):
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


if __name__ == '__main__':
    # define the parameters and ranges to run OFAT for
    problem = {'num_ants': [int, [1,100]],
               'num_plants': [int, [1,100]], 
               'pheromone_lifespan': [int, [5, 100]],
               'num_plant_leaves': [int, [10, 200]],
               'initial_foragers_ratio': [float, [0.1, 1.0]], 
               'leaf_regrowth_rate': [float, [0.01, 1.0]],
               'ant_death_probability': [float, [0, 0.1]],
               'initial_fungus_energy': [float, [10, 100]],
               'fungus_decay_rate': [float, [0.001, 0.1]], 
               'energy_biomass_cvn': [float, [1, 3]], 
               'fungus_larvae_cvn': [float, [0.5, 1.5]],
               'energy_per_offspring': [float, [1.0, 10]],
               'fungus_feed_threshold': [float, [5.0, 20.0]],
               'max_fitness_queue_size': [int, [1, 100]],
    }

    # set the output variables
    model_reporters = {"Ants_Biomass": track_ants,
                       "Fungus_Biomass": lambda m: m.fungus.biomass,
                       "Fraction forager ants": track_ratio_foragers,
    }

    # set fixed parameters, eg collect_data = False
    fixed_parameters = {'collect_data': False}


    fileName = 'SA-experimentation270122'

    repetitions = 5
    max_steps = 500
    distinct_samples = 5

    data = recover_OFAT_data(fileName)

    plot_all_vars(data, model_reporters)

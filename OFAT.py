"""
One-Factor-At-a-Time (OFAT) (local) sensitivity analysis, based on methods provided by the SA notebook and the article of ten Broeke (2016)

"""
from leafcutter_ants_fungi_mutualism.model import LeafcutterAntsFungiMutualismModel, track_ants
from mesa.batchrunner import BatchRunner, BatchRunnerMP
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

if not os.path.exists('Data/OFAT'):
    os.makedirs('Data/OFAT')
if not os.path.exists('Figures/OFAT'):
    os.makedirs('Figures/OFAT')


# model = LeafcutterAntsFungiMutualismModel(num_ants=50, num_plants=30, width=20, height=50,
#                  pheromone_lifespan=30, num_plant_leaves=100,
#                  leaf_regrowth_rate=1/2, ant_death_probability=0.01,
#                  initial_fungus_energy=50, fungus_decay_rate=1/50)

# reps = 100
# for r in range(reps):
#     model.step()

# data = model.datacollector.get_model_vars_dataframe()
# print(data)

"""
Pre-test to determine whether the model converges to a steady state behaviour
"""
model = LeafcutterAntsFungiMutualismModel(num_ants=50, num_plants=30, width=20, height=50,
                 pheromone_lifespan=30, num_plant_leaves=100,
                 leaf_regrowth_rate=1/2, ant_death_probability=0.01,
                 initial_fungus_energy=50, fungus_decay_rate=1/50)

repetitions = 100
time_steps = 100

output_variables = {"Ants_Biomass": track_ants,
                    "Fungus_Biomass": lambda m: m.fungi[0].biomass}

variable_parameters = {'num_ants': [20,50]}

# batch = BatchRunner(LeafcutterAntsFungiMutualismModel,
#                     max_steps = time_steps, 
#                     variable_parameters = variable_parameters,
#                     iterations = repetitions,
#                     model_reporters = output_variables,
#                     display_progress = True)

batch = BatchRunner(LeafcutterAntsFungiMutualismModel,
                    max_steps = time_steps, 
                    variable_parameters = variable_parameters,
                    iterations = repetitions,
                    model_reporters = output_variables,
                    display_progress = True)


batch.run_all()

data = batch.get_model_vars_dataframe()

print(data)

""" 
Code based on the sensitivity analysis notebook
"""
def collect_data_OFAT():
    # define variables and bounds
    problem = {
        'num_vars': 3,
        'names': ['pheromone_lifespan', 'ant_death_probability', 'fungus_decay_rate'],
        'bounds': [[10, 50], [0.01, 0.1], [0.001, 0.01]]
    }

    # define fixed parameters
    # fixed_params = {}

    # set the repetitions, amount of steps, amount of distinc_samples
    replicates = 5
    max_steps = 100
    distinct_samples = 5

    # set the outputs
    model_reporters = {"Fungus": lambda m: m.fungi[0].biomass,
                        "Ants": track_ants}

    data = {}

    for i, var in enumerate(problem['names']):
        # get the bounds for this variable and get <distinct_samples> samples within this space (uniform)
        samples = np.linspace(*problem['bounds'][i], num=distinct_samples)

        # pheromon_lifespan needs to be an integer
        if var == 'pheromone_lifespan':
            samples = np.linspace(*problem['bounds'][i], num=distinct_samples, dtype=int)

        batch = BatchRunner(LeafcutterAntsFungiMutualismModel, 
                            max_steps=max_steps,
                            iterations=replicates,
                            variable_parameters={var: samples},
                            model_reporters=model_reporters,
                            display_progress=True)
                            # fixed_parameters = ...

        batch.run_all()

        data[var] = batch.get_model_vars_dataframe()
        
    return data


# the following functions are copied directly from the notebook and still need to be adapted
def plot_param_var_conf(ax, df, var, param, i):
    """
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

    replicates = df.groupby(var)[param].count()
    err = (1.96 * df.groupby(var)[param].std()) / np.sqrt(replicates)

    ax.plot(x, y, c='k')
    ax.fill_between(x, y - err, y + err)

    ax.set_xlabel(var)
    ax.set_ylabel(param)

def plot_all_vars(df, param):
    """
    Plots the parameters passed vs each of the output variables.

    Args:
        df: dataframe that holds all data
        param: the parameter to be plotted
    """

    f, axs = plt.subplots(3, figsize=(7, 10))
    
    for i, var in enumerate(problem['names']):
        plot_param_var_conf(axs[i], data[var], var, param, i)



# data = collect_data_OFAT()
# for param in ('Ants', 'Fungus'):
#     plot_all_vars(data, param)
#     plt.show()


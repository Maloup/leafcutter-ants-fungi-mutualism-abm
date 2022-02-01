import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from model import LeafcutterAntsFungiMutualismModel, track_ants, track_leaves, track_ratio_foragers, track_ants_leaves

import sys


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

    ax.vlines(x, y-stdev, y + stdev, color='grey', alpha = 0.8)
    ax.plot(df[var], df[param], 'ko', markersize=0.8)

    
    ax.scatter(x, y, c='darkgreen', marker='o')
#     ax.plot(x, y, c='k', marker='o', linewidth = 0.8)
#     ax.fill_between(x, y - stdev, y + stdev, color='grey', alpha=0.2)
    
    
    
#     ax.plot(x, minimum, c='magenta', marker='x', linewidth = 0.8)
#     ax.plot(x, maximum, c='deepskyblue', marker='+', linewidth = 0.8)
    ax.scatter(x, minimum, c='magenta', marker='x')
    ax.scatter(x, maximum, c='deepskyblue', marker='+')

    ax.set_xlabel(var)
    ax.set_ylabel(param)
    # ax.grid()

    ax.tick_params(which='both', labelsize=12)

def plot_all_vars(data, model_reporters, save_fig=True, show_fig=False):
    """
    Modified from the Sensitivity Analysis notebook provided by the course Agent-based-modelling

    Uses plot_param_var_conf to plot the OFAT results provided in data on separate axes
    """

    fig, axs = plt.subplots(len(data.keys()),len(model_reporters)-1, figsize=(5*(len(model_reporters)-1), 3.5*len(data.keys())),
                            constrained_layout=True
                            )

    for row, var in enumerate(data.keys()):
        for col, output_param in enumerate(model_reporters):
            if output_param == 'Death reason':
# #             print(output_param)
#                 x = snapshot_data.groupby(var).mean().reset_index()[var]
# #             print(x)
#                 y = snapshot_data.groupby(var).count()['Death reason']
# #             print(y)
#                 axs[row,col].scatter(x, y, c='darkgreen', marker='o')
#                 axs[row,col].set_xlabel(var)
#                 axs[row,col].set_ylabel(param)
                continue
                # filter out the Death reason from plotting, for separate plotting
            else:
                plot_param_var_conf(axs[row,col], data[var], var, output_param, col)
    

    # fig.tight_layout()

    if save_fig:
        fig.savefig('figures/OFAT/' + fileName + '.svg')
        fig.savefig('figures/OFAT/' + fileName + '.pdf', bbox_inches='tight')

    if show_fig:
        plt.show()



def recover_OFAT_data(fileName):
    """
    Recovers data saved in collect_OFAT_data function
    """
    return dict(np.load('data/OFAT/' + fileName + '.npz', allow_pickle=True))


def plot_fraction_dead(data, model_reporters, save_fig=True, show_fig=False):
    """ Creates figure of the fraction of colonies that died out in early stage,
    for the variable parameters run for in the OFAT """

    # fig, axs = plt.subplots(1, len(data.keys()), figsize=(3.5*len(data.keys()), 5),
    #                         constrained_layout=True
                            # )
    fig, axs = plt.subplots(4,4, figsize=(4*5, 5*4),
                        constrained_layout=True
                        )
    counter = 0
    for row in range(4):
        for col in range(4):
            var = list(data.keys())[counter]

            param = 'Death reason'
            # print(data)
            df = data[var]
            # print(df)
            # print(len(df))
            x = df.groupby(var).mean().reset_index()[var] 
            y = df.groupby(var).count()['Death reason'] / 64 # this is hard coded
            axs[row, col].plot(x, y, c='darkgreen', marker='o')
            axs[row, col].set_xlabel(var)
            axs[row, col].set_ylabel(param)
            axs[row, col].tick_params(which='both', labelsize=12)
            counter += 1
            axs[row, col].set_ylim(0,1)
            
    fig.suptitle('Fraction of 64 colonies that die out in early stage', fontsize=24)
    # fig.tight_layout()
    if save_fig:
        fig.savefig('figures/OFAT/fractiondeath' + fileName + '.svg')#'.pdf', bbox_inches='tight')
        fig.savefig('figures/OFAT/fractiondeath' + fileName + '.pdf', bbox_inches='tight')

    if show_fig:
        plt.show()

if __name__ == '__main__':

    if len(sys.argv) < 2:
        print("no filename of data specified, please specify full filename excluding extension.npz")
        sys.exit(-1)

    repetitions = 50
    max_steps = 3000
    distinct_samples = 10

    # fileName = f"reps{repetitions}maxtime{max_steps}distinctsam{distinct_samples}ripper"
    
    fileName = sys.argv[1]

    results = recover_OFAT_data(fileName)

    data = results['data'][()]
    problem = results['problem'][()]
    model_reporters = results['model_reporters'][()]
    fixed_parameters = results['fixed_parameters'][()]

    # plot_all_vars(data, model_reporters)
    plot_fraction_dead(data, model_reporters)
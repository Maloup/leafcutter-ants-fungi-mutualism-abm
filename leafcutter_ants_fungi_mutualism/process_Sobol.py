"""
Process the results made using Sobol.py script
"""

from SALib.analyze import sobol
import numpy as np
import matplotlib.pyplot as plt


data = np.load('data/Sobol/sobol_modelevals_test290122.npz', allow_pickle=True)
# print(data['results'])
problem = data['problem'][()]
results = data['results'][()]


Si_fungus = sobol.analyze(problem, results[:,0], calc_second_order=False, print_to_console=True)
Si_ants = sobol.analyze(problem, results[:,1], calc_second_order=False, print_to_console=True)
Si_forager = sobol.analyze(problem, results[:,2], calc_second_order=False, print_to_console=True)
Si_leaves = sobol.analyze(problem, results[:,3], calc_second_order=False, print_to_console=True)

def plot_index(s, params, i, title=''):
    """
    Creates a plot for Sobol sensitivity analysis that shows the contributions
    of each parameter to the global sensitivity.

    Args:
        s (dict): dictionary {'S#': dict, 'S#_conf': dict} of dicts that hold
            the values for a set of parameters
        params (list): the parameters taken from s
        i (str): string that indicates what order the sensitivity is.
        title (str): title for the plot
    """

    if i == '2':
        p = len(params)
        params = list(combinations(params, 2))
        indices = s['S' + i].reshape((p ** 2))
        indices = indices[~np.isnan(indices)]
        errors = s['S' + i + '_conf'].reshape((p ** 2))
        errors = errors[~np.isnan(errors)]
    else:
        indices = s['S' + i]
        errors = s['S' + i + '_conf']
        plt.figure()

    l = len(indices)

    plt.title(title)
    plt.ylim([-0.2, len(indices) - 1 + 0.2])
    plt.yticks(range(l), params)
    plt.errorbar(indices, range(l), xerr=errors, linestyle='None', marker='o')
    plt.axvline(0, c='k')

for Si in (Si_fungus, Si_ants, Si_forager, Si_leaves):
    # First order
    plot_index(Si, problem['names'], '1', 'First order sensitivity')
    plt.show()

    # Total order
    plot_index(Si, problem['names'], 'T', 'Total order sensitivity')
    plt.show()

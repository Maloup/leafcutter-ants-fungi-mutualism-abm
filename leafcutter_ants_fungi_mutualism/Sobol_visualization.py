"""
Process the results made using Sobol.py script
"""
from model import LeafcutterAntsFungiMutualismModel, track_ants, track_leaves, track_ratio_foragers, track_ants_leaves
from SALib.analyze import sobol
import numpy as np
import matplotlib.pyplot as plt

def fungus_biomass(model):
    return model.fungus.biomass

run = 1
data = np.load(f'data/Sobol/ripper/run_{run}.npz', allow_pickle=True)
# print(data['results'])
problem = data['problem'][()]
results = data['results'][()]
model_reporters = data['model_reporters'][()]

Si_all = {}

for i, key in enumerate(sorted(model_reporters.keys())):
    Si_all[key] = sobol.analyze(problem, results[:,i], calc_second_order=False, print_to_console=True, seed=546)

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
    plt.xlim([-0.2, 1])
    plt.yticks(range(l), params)
    plt.errorbar(indices, range(l), xerr=errors, linestyle='None', marker='o')
    plt.axvline(0, c='k')

# for Si in Si_all:
#     # First order
#     plot_index(Si_all[Si], problem['names'], '1', 'First order sensitivity')
#     plt.show()

#     # Total order
#     plot_index(Si_all[Si], problem['names'], 'T', 'Total order sensitivity')
#     plt.show()

# for run in range(1,5):
#     data = np.load(f'data/Sobol/ripper/run_{run}.npz', allow_pickle=True)
#     problem = data['problem'][()]
#     results = data['results'][()]
#     model_reporters = data['model_reporters'][()]

#     Si_all = {}

#     for i, key in enumerate(sorted(model_reporters.keys())):
#         Si_all[key] = sobol.analyze(problem, results[:,i], calc_second_order=False, print_to_console=True, seed=546)


#     Si = 'Ants_Biomass'
#     #First order
#     plot_index(Si_all[Si], problem['names'], '1', 'First order sensitivity')
#     plt.show()

#     # Total order
#     plot_index(Si_all[Si], problem['names'], 'T', 'Total order sensitivity')
#     plt.show()



# concatenate the data to obtain one set of indices
# need to preserve order

results_combined = np.zeros((512*7*10, 6))

results_all = []

for run in range(1,11):
    # get results
    data = np.load(f'data/Sobol/ripper/run_{run}.npz', allow_pickle=True)
    results_all.append(data['results'][()])

counter = 0
for ix in range(512*7):
    for run in range(10):
        results_combined[counter] = results_all[run][ix]

Si_all_combined = {}

for i, key in enumerate(sorted(model_reporters.keys())):
    Si_all_combined[key] = sobol.analyze(problem, results[:,i], calc_second_order=False, print_to_console=True, seed=546)



# Si = 'Ants_Biomass'
# #First order
# plot_index(Si_all_combined[Si], problem['names'], '1', 'First order sensitivity')
# plt.show()

# # Total order
# plot_index(Si_all_combined[Si], problem['names'], 'T', 'Total order sensitivity')
# plt.show()

Si = 'Dormant caretakers fraction'
#First order
plot_index(Si_all_combined[Si], problem['names'], '1', 'First order sensitivity')
plt.show()

# Total order
plot_index(Si_all_combined[Si], problem['names'], 'T', 'Total order sensitivity')
plt.show()

Si = 'Fraction forager ants'
#First order
plot_index(Si_all_combined[Si], problem['names'], '1', 'First order sensitivity')
plt.show()

# Total order
plot_index(Si_all_combined[Si], problem['names'], 'T', 'Total order sensitivity')
plt.show()
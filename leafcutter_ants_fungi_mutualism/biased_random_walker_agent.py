import numpy as np
from mesa import Agent

from .util import manhattan_distance


class BiasedRandomWalkerAgent(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.prev_pos = None

    def random_move(self):
        """
        Randomly move to a Moore neighborhood.
        """
        neighbors = self.model.grid.get_neighborhood(self.pos, moore=True)
        if self.prev_pos is None:
            # random move
            next_pos = self.random.choice(neighbors)
        else:
            # biased random move
            dists = np.array([manhattan_distance(self.prev_pos, n)
                              for n in neighbors])
            prob_dist = dists/np.sum(dists)
            print(neighbors, prob_dist)
            next_idx = np.random.choice(len(neighbors), p=prob_dist)
            print(next_idx)
            next_pos = neighbors[next_idx]

        self.prev_pos = self.pos
        self.model.grid.move_agent(self, next_pos)

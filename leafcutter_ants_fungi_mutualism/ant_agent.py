from .biased_random_walker_agent import BiasedRandomWalkerAgent
from .plant import Plant
from .pheromone import Pheromone
from .util import manhattan_distance

import numpy as np
from enum import Enum, auto


class AntWorkerState(Enum):
    EXPLORE = auto()
    RECRUIT = auto()
    HARVEST = auto()
    CTAKING = auto()


class AntAgent(BiasedRandomWalkerAgent):
    def __init__(self, unique_id, model, state = AntWorkerState.EXPLORE):
        self.unique_id = unique_id
        super().__init__(unique_id, model)
        self.state = state
        self.has_leaf = False

    def step(self):
        # mortality
        if self.random.random() <= self.model.ant_death_probability:
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)
            return

        # be nice if Python had pattern matching with enums
        if self.state == AntWorkerState.EXPLORE:
            self.explore_step()
        elif self.state == AntWorkerState.RECRUIT:
            self.recruit_step()
        elif self.state == AntWorkerState.HARVEST:
            self.harvest_step()
        elif self.state == AntWorkerState.CTAKING:
            self.caretaking_step()

    def explore_step(self):
        """
        When in explore state, the worker ant does a random walk until one of
        the following events occurs:
        1. It finds a pheromone and switches to harvest state in which it
           will follow the pherome trail to the plant and return a leaf to the
           nest.
        2. It finds a plant, after which it will switch to the recruit state to
           alert other ants of the location of the plant.
        If it finds both, it will go into the recruit state.
        """
        self.random_move()

        nearby_plants, nearby_pheromones = self.get_nearby_plants_and_pheromones()

        if nearby_plants:
            plant = self.random.choice(nearby_plants)
            if plant.take_leaf():
                self.has_leaf = True
                self.state = AntWorkerState.RECRUIT
        elif nearby_pheromones:
            # XXX: should following state transition happen probabilistically?
            self.state = AntWorkerState.HARVEST

    def recruit_step(self):
        """
        In the recruit state, the ant returns to the hive in a straight line
        (using its memory/sensing abilities) while leaving a pheromone trail for
        other ants to find and harvest the plant.
        """
        if self.model.on_nest(self):
            # found nest, task of laying pheromone trail complete, return to
            # explore state
            self.state = AntWorkerState.EXPLORE
            return

        # leave pheromone on current location
        # TODO: should this have some extra energy cost?
        self.put_pheromone()

        # step towards nest
        x_step, y_step = self.get_direction_towards_nest()
        self.model.grid.move_agent(
            self, (self.pos[0] + x_step, self.pos[1] + y_step))

    def harvest_step(self):
        """
        In the harvest state, the ant follows the trail of pheromones towards
        the plant. If it arrives at a plant, it will cut a piece of leaf off and
        carry it to the nest to feed the fungus.
        """
        if self.has_leaf:
            # return to nest with leaf
            if self.model.on_nest(self):
                # found nest, feed fungus
                # TODO: now assumes we have just a single fungus, decide on how
                # transfer leaf to fungus
                self.model.fungus.feed()
                self.has_leaf = False
                self.state = AntWorkerState.EXPLORE
                return

            # Long distance foraging routs are repeatedly re-marked by ants
            #   traveling along these trails (Jaffé & Howse 1979)
            self.put_pheromone()

            x_step, y_step = self.get_direction_towards_nest()
            self.model.grid.move_agent(
                self, (self.pos[0] + x_step, self.pos[1] + y_step))
        else:
            nearby_plants, nearby_pheromones = self.get_nearby_plants_and_pheromones()
            if nearby_plants:
                # found plant, get leaf
                plant = self.random.choice(nearby_plants)
                if plant.take_leaf():
                    self.has_leaf = True
                else:
                    # plant's leaves have been exhausted, return to exploring
                    self.state = AntWorkerState.EXPLORE
                return

            # follow pheromone trail

            if not nearby_pheromones:
                # pheromones disappeared
                self.state = AntWorkerState.EXPLORE
                return

            ant_dist_from_nest = manhattan_distance(self.pos, self.model.nest.pos)
            pheromones_dist_change = np.array([
                manhattan_distance(p.pos, self.model.nest.pos) - ant_dist_from_nest
                for p in nearby_pheromones
            ])
            if np.all(pheromones_dist_change <= 0):
                # no outwards going pheromones near, do explore step
                self.state = AntWorkerState.EXPLORE
                self.explore_step()
                return

            # choose random outwards going pheromone
            outwards_pheromones = np.argwhere(pheromones_dist_change > 0).flatten()
            rand_outwards = self.random.choice(outwards_pheromones)
            outwards_pheromone = nearby_pheromones[rand_outwards]
            self.model.grid.move_agent(self, outwards_pheromone.pos)

    def caretaking_step(self):
        """
        If enough fungus is available, then feed one unit to larvae
        (decrement `fungus.biomass`, increment `nest.energy_buffer``).
        """
        # TODO: we can also track the number of caretakers in the model
        #   and perform the feeding step in one function call instead of
        #   individually for every caretaker ant. This can be considered once
        #   we have task allocation/switching up and running.
        if not self.model.fungus.dead or self.model.fungus.biomass >= self.model.fungus_feed_threshold:
            self.model.feed_larvae()
        else:
            pass # TODO: maybe task-switching can be implemented here?

    def put_pheromone(self):
        """
        Put a pheromone on the current position of the ant if there is none yet,
        otherwise re-mark the cell.
        """
        cell_agents = self.model.grid.get_cell_list_contents(self.pos)
        for agent in cell_agents:
            if isinstance(agent, Pheromone):
                agent.remark()
                return

        agent = Pheromone(self.model.next_id(), self.model)
        self.model.schedule.add(agent)
        self.model.grid.place_agent(agent, self.pos)

    def get_direction_towards_nest(self):
        """
        Get the direction tuple towards the nest. Returns a tuple with the
        first element corresponding to the x direction and the second element
        corresponding to the y direction. Directions are in {-1, 0, 1}.
        """
        nest_x, nest_y = self.model.nest.pos
        self_x, self_y = self.pos

        angle = np.arctan2(nest_x - self_x, nest_y - self_y)
        x_step = round(np.sin(angle))
        y_step = round(np.cos(angle))

        return x_step, y_step

    def get_nearby_plants_and_pheromones(self):
        neighbors = self.model.grid.get_neighbors(
            self.pos, moore=True, include_center=True)
        nearby_plants = []
        nearby_pheromones = []
        for p in neighbors:
            if isinstance(p, Plant):
                nearby_plants.append(p)
            elif isinstance(p, Pheromone):
                nearby_pheromones.append(p)

        return nearby_plants, nearby_pheromones

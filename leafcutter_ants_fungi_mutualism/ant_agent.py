from .random_walker_agent import BiasedRandomWalkerAgent
from .plant import Plant
from .pheromone import Pheromone
from .util import arctan_activation_pstv, manhattan_distance

import numpy as np
import queue
from enum import Enum, auto


class AntWorkerState(Enum):
    EXPLORE = auto()
    RECRUIT = auto()
    HARVEST = auto()
    CARETAKING = auto()


class DeathReason(Enum):
    FUNGUS = auto()
    ANTS = auto()


def track_death_reason(model):
    if model.death_reason:
        return model.death_reason
    fungus_dead_p = model.fungus.dead
    if fungus_dead_p:
        return DeathReason.FUNGUS

    agents_list = model.schedule.agents
    for agent in agents_list:
        if isinstance(agent, AntAgent):
            return None
    return DeathReason.ANTS


class AntAgent(BiasedRandomWalkerAgent):
    def __init__(self, unique_id, model, state=AntWorkerState.EXPLORE):
        self.unique_id = unique_id
        super().__init__(unique_id, model)
        self.state = state
        self.has_leaf = False
        self.neighbor_density_acc = 0
        self.trip_duration = 0
        self.roundtrip_length = None

    def step(self):
        # mortality
        if self.random.random() <= self.model.ant_death_probability:
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)
            return

        # be nice if Python had pattern matching with enums
        if self.state is AntWorkerState.EXPLORE:
            self.explore_step()
        elif self.state is AntWorkerState.RECRUIT:
            self.recruit_step()
        elif self.state is AntWorkerState.HARVEST:
            self.harvest_step()
        elif self.state is AntWorkerState.CARETAKING:
            self.caretaking_step()

        if self.state is not AntWorkerState.CARETAKING:
            self.neighbor_density_acc += self.get_neighborhood_density()
            self.trip_duration += 1

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
            self.returned_to_nest()
            return

        # leave pheromone on current location
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
        nearby_plants, nearby_pheromones = self.get_nearby_plants_and_pheromones()
        if nearby_plants:
            # found plant, get leaf
            plant = self.random.choice(nearby_plants)
            if plant.take_leaf():
                self.has_leaf = True
                self.state = AntWorkerState.RECRUIT
            else:
                # plant's leaves have been exhausted, return to exploring
                self.state = AntWorkerState.EXPLORE
            return

        if not nearby_pheromones:
            # pheromones disappeared
            self.state = AntWorkerState.EXPLORE
            return

        # follow pheromone trail outwards from nest
        ant_dist_from_nest = manhattan_distance(self.pos, self.model.nest.pos)
        pheromones_dist_change = np.array([
            manhattan_distance(p.pos, self.model.nest.pos) - ant_dist_from_nest
            for p in nearby_pheromones
        ])
        if np.all(pheromones_dist_change <= 0):
            # no outwards going pheromones near, do random move
            self.random_move()
            self.state = AntWorkerState.EXPLORE
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
        if self.roundtrip_length is None:
            self.set_roundtrip_length(
                mu=self.model.caretaker_roundtrip_mean, sigma=self.model.caretaker_roundtrip_std)

        self.roundtrip_length -= 1
        if self.roundtrip_length == 0:
            fitness = arctan_activation_pstv(
                self.model.fungus.biomass/self.fungus_biomass_start, 1
            )

            # dormancy
            if 0.5 > fitness:
                self.set_roundtrip_length(
                    mu=self.model.dormant_roundtrip_mean,
                    sigma=self.model.dormant_roundtrip_mean/2)

            # feeding
            else:
                # `fungus.dead` tested inside `feed_larvae`
                self.model.nest.feed_larvae()

                self.set_roundtrip_length(
                    mu=self.model.caretaker_roundtrip_mean, sigma=self.model.caretaker_roundtrip_std)

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

    def returned_to_nest(self):
        # feed fungus first if we have a leaf
        if self.has_leaf:
            self.model.fungus.feed()
            self.has_leaf = False

        # task division
        interaction_prob = self.neighbor_density_acc / self.trip_duration
        # add fitness to fitness_queue
        fitness = 1 - interaction_prob

        try:
            self.model.nest.fitness_queue.put_nowait(fitness)
        except queue.Full:
            self.model.nest.fitness_queue.get()
            self.model.nest.fitness_queue.put_nowait(fitness)

        # Drafting a random caretaker
        if self.random.random() <= (1 - interaction_prob):
            nest_content = self.model.grid.iter_cell_list_contents(self.pos)
            caretakers = list(filter(
                lambda a: isinstance(
                    a, AntAgent) and a.state is AntWorkerState.CARETAKING,
                nest_content
            ))
            if caretakers:
                drafted_caretaker = self.random.choice(caretakers)
                drafted_caretaker.state = AntWorkerState.EXPLORE

        # Switching roles with certain probability
        if self.random.random() <= interaction_prob:
            self.state = AntWorkerState.CARETAKING
        else:
            self.state = AntWorkerState.EXPLORE

        self.reset_trip()

    def get_neighborhood_density(self):
        neighbor_cells = self.model.grid.get_neighborhood(
            self.pos, moore=True, include_center=True)

        count = 0
        for cell in neighbor_cells:
            for agent in self.model.grid.iter_cell_list_contents(cell):
                if isinstance(agent, AntAgent) and self.unique_id != agent.unique_id:
                    count += 1
                    break

        neighbor_density = count/9
        return neighbor_density

    def reset_trip(self):
        self.neighbor_density_acc = 0
        self.trip_duration = 0

    def set_roundtrip_length(self, mu=5, sigma=5):
        self.fungus_biomass_start = self.model.fungus.biomass
        self.roundtrip_length = max(round(np.random.normal(mu, sigma)), 1)

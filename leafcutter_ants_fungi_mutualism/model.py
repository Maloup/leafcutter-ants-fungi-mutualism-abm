from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from .ant_agent import AntAgent, AntWorkerState
from .plant import Plant
from .nest import Nest
from .fungus import Fungus


def track_leaves(model):
    return sum(1 for agent in model.schedule.agents
               if isinstance(agent, AntAgent) and agent.has_leaf)


def track_ants(model):
    return sum(1 for agent in model.schedule.agents
               if isinstance(agent, AntAgent))


def track_ratio_foragers(model):
    n_ants = 0
    n_foragers = 0
    for agent in model.schedule.agents:
        if isinstance(agent, AntAgent):
            n_ants += 1
            if agent.state is not AntWorkerState.CARETAKING:
                n_foragers += 1

    if n_ants > 0:
        return n_foragers / n_ants
    else:
        return 0.0


def track_forager_fitness(model):
    fitness_queue_list = list(model.nest.fitness_queue.queue)
    if len(fitness_queue_list) != 0:
        return sum(fitness_queue_list)/len(fitness_queue_list)

    return 0.5


class LeafcutterAntsFungiMutualismModel(Model):
    """
    The model class holds the model-level attributes, manages the agents, and generally handles
    the global level of our model.

    There is only one model-level parameter: how many agents the model contains. When a new model
    is started, we want it to populate itself with the given number of agents.

    The scheduler is a special model component which controls the order in which agents are activated.
    """

    def __init__(self, collect_data=True, num_ants=50, num_plants=30, width=50,
                 height=50, pheromone_lifespan=30, num_plant_leaves=100,
                 initial_foragers_ratio=0.5, leaf_regrowth_rate=1/2,
                 ant_death_probability=0.01, initial_fungus_energy=50,
                 fungus_decay_rate=0.005, energy_biomass_cvn=2.0,
                 fungus_larvae_cvn=0.9, energy_per_offspring=1.0,
                 fungus_biomass_death_threshold=5.0, fungus_feed_threshold=5.0,
                 caretaker_carrying_amount=1, max_fitness_queue_size=20,
                 caretaker_roundtrip_mean=5.0, caretaker_roundtrip_std=5.0,
                 dormant_roundtrip_mean=60.0, dormant_roundtrip_std=30.0):
        super().__init__()

        self.collect_data = collect_data
        self.num_ants = num_ants
        self.num_plants = num_plants
        self.pheromone_lifespan = pheromone_lifespan
        self.num_plant_leaves = num_plant_leaves
        self.leaf_regrowth_rate = leaf_regrowth_rate
        self.ant_death_probability = ant_death_probability
        self.initial_fungus_energy = initial_fungus_energy
        self.fungus_decay_rate = fungus_decay_rate
        self.energy_biomass_cvn = energy_biomass_cvn
        self.fungus_larvae_cvn = fungus_larvae_cvn
        self.energy_per_offspring = energy_per_offspring
        self.fungus_feed_threshold = fungus_feed_threshold
        self.fungus_biomass_death_threshold = fungus_biomass_death_threshold
        self.max_fitness_queue_size = max_fitness_queue_size
        self.caretaker_carrying_amount = caretaker_carrying_amount

        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width=width, height=height, torus=False)
        self.initial_foragers_ratio = initial_foragers_ratio

        self.nest = None
        self.fungus = None
        self.caretaker_roundtrip_mean = caretaker_roundtrip_mean
        self.caretaker_roundtrip_std = caretaker_roundtrip_std
        self.dormant_roundtrip_mean = dormant_roundtrip_mean
        self.dormant_roundtrip_std = dormant_roundtrip_std
        self.init_agents()

        self.datacollector = DataCollector(
            model_reporters={
                "Fungus Biomass": lambda model: model.fungus.biomass,
                "Ant Biomass": track_ants,
                "Ants with Leaves": track_leaves,
                "Fraction forager ants": track_ratio_foragers,
            }
        )

        self.running = True

        if self.collect_data:
            self.datacollector.collect(self)

    def init_agents(self):
        self.init_nest()
        self.init_plants()
        self.init_ants()
        self.init_fungus()

    def init_nest(self):
        self.nest = Nest(self.next_id(), self)
        self.schedule.add(self.nest)
        nest_pos = (self.grid.width // 2, self.grid.height // 2)
        self.grid.place_agent(self.nest, nest_pos)

    def init_plants(self):
        for i in range(self.num_plants):
            # XXX: should every plant have the same number of leaves, or should
            # we add some randomness to that?
            agent = Plant(self.next_id(), self)
            self.schedule.add(agent)

            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)

            while x == self.nest.pos[0] and y == self.nest.pos[1]:
                # don't spawn plant on nest
                x = self.random.randrange(self.grid.width)
                y = self.random.randrange(self.grid.height)

            self.grid.place_agent(agent, (x, y))

    def init_ants(self):
        foragers_count = int(self.initial_foragers_ratio * self.num_ants)
        for i in range(foragers_count):
            # default state is explorer
            agent = AntAgent(self.next_id(), self)
            self.schedule.add(agent)
            self.grid.place_agent(agent, self.nest.pos)

        for i in range(self.num_ants - foragers_count):
            agent = AntAgent(self.next_id(), self,
                             state=AntWorkerState.CARETAKING)
            self.schedule.add(agent)
            self.grid.place_agent(agent, self.nest.pos)

    def init_fungus(self):
        self.fungus = Fungus(self.next_id(), self)
        self.schedule.add(self.fungus)
        self.grid.place_agent(self.fungus, self.nest.pos)

    def on_nest(self, agent):
        return agent.pos == self.nest.pos

    def step(self):
        """
        A model step. Used for collecting data and advancing the schedule
        """
        if self.collect_data:
            self.datacollector.collect(self)

        self.schedule.step()

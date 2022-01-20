from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from .ant_agent import AntAgent
from .ant_agent import AntWorkerState
from .plant import Plant
from .nest import Nest
from .fungus import Fungus


def track_leaves(model):
    return sum(1 for agent in model.schedule.agents
               if isinstance(agent, AntAgent) and agent.has_leaf)


def track_ants(model):
    return sum(1 for agent in model.schedule.agents
               if isinstance(agent, AntAgent))


class LeafcutterAntsFungiMutualismModel(Model):
    """
    The model class holds the model-level attributes, manages the agents, and generally handles
    the global level of our model.

    There is only one model-level parameter: how many agents the model contains. When a new model
    is started, we want it to populate itself with the given number of agents.

    The scheduler is a special model component which controls the order in which agents are activated.
    """

    def __init__(self, num_ants=50, num_plants=30, width=20, height=50,
                 pheromone_lifespan=30, num_plant_leaves=100,
                 initial_foragers_ratio = 0.5, energy_per_offspring = 1.0,
                 leaf_regrowth_rate=1/2, ant_death_probability=0.01,
                 initial_fungus_energy=50, fungus_decay_rate=1/50,
                 biomass_offspring_cvn = 0.1, biomass_energy_cvn = 1.0,
                 fungus_biomass_death_threshold = 5.0, fungus_feed_threshold = 5.0):
        super().__init__()
        # TODO: can we create a macro that can automate these assignments?
        self.num_ants = num_ants
        self.num_plants = num_plants
        self.pheromone_lifespan = pheromone_lifespan
        self.num_plant_leaves = num_plant_leaves
        self.leaf_regrowth_rate = leaf_regrowth_rate
        self.ant_death_probability = ant_death_probability
        self.initial_fungus_energy = initial_fungus_energy
        self.fungus_decay_rate = fungus_decay_rate
        self.biomass_offspring_cvn = biomass_offspring_cvn
        self.biomass_energy_cvn = biomass_energy_cvn
        self.energy_per_offspring = energy_per_offspring
        self.fungus_feed_threshold = fungus_feed_threshold
        self.fungus_biomass_death_threshold = fungus_biomass_death_threshold

        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width=width, height=height, torus=False)
        self.initial_foragers_ratio = initial_foragers_ratio

        self.nest = None
        self.fungus = None

        self.init_agents()

        self.datacollector = DataCollector(
            model_reporters={
                "Fungus Biomass": lambda model: model.fungus.biomass,
                "Ant Biomass": track_ants,
                "Ants with Leaves": track_leaves,
            }
        )

        self.running = True
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
            agent = AntAgent(self.next_id(), self, state = AntWorkerState.CTAKING)
            self.schedule.add(agent)
            self.grid.place_agent(agent, self.nest.pos)

    def init_fungus(self):
        self.fungus = Fungus(self.next_id(), self)
        self.schedule.add(self.fungus)
        self.grid.place_agent(self.fungus, self.nest.pos)

    def on_nest(self, agent):
        return agent.pos == self.nest.pos

    def feed_larvae(self):
        # WARN: check for non-zero fungal biomass is assumed to be
        # done by caller. If this check is done then expect no problems
        # unless there are race conditions.
        if (self.fungus.biomass > 1.0):
            self.fungus.biomass -= 1.0
            # `biomass_energy_cvn` defaults to 1.0
            self.nest.energy_buffer += self.biomass_energy_cvn * 1.0


    def step(self):
        """
        A model step. Used for collecting data and advancing the schedule
        """
        self.datacollector.collect(self)
        self.schedule.step()

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector

from .ant_agent import AntAgent
from .plant import Plant
from .nest import Nest
from .fungus import Fungus


def track_leaves(model):
    return sum(1 for agent in model.schedule.agents
               if isinstance(agent, AntAgent) and agent.has_leaf)


class LeafcutterAntsFungiMutualismModel(Model):
    """
    The model class holds the model-level attributes, manages the agents, and generally handles
    the global level of our model.

    There is only one model-level parameter: how many agents the model contains. When a new model
    is started, we want it to populate itself with the given number of agents.

    The scheduler is a special model component which controls the order in which agents are activated.
    """

    def __init__(self, num_ants=50, num_plants=20, width=20, height=50,
                 pheromone_lifespan=30, num_plant_leaves=20):
        super().__init__()
        self.num_ants = num_ants
        self.num_plants = num_plants
        self.pheromone_lifespan = pheromone_lifespan
        self.num_plant_leaves = num_plant_leaves

        self.schedule = RandomActivation(self)
        self.grid = MultiGrid(width=width, height=height, torus=False)

        self.nest_pos = (self.grid.width // 2, self.grid.height // 2)
        self.fungi = []

        self.init_agents()

        self.datacollector = DataCollector(
            model_reporters={
                "Fungus Energy": lambda model: model.fungi[0].energy,
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
        agent = Nest(self.next_id(), self)
        self.schedule.add(agent)
        self.grid.place_agent(agent, self.nest_pos)

    def init_plants(self):
        for i in range(self.num_plants):
            # XXX: should every plant have the same number of leaves, or should
            # we add some randomness to that?
            agent = Plant(self.next_id(), self)
            self.schedule.add(agent)

            x = self.random.randrange(self.grid.width)
            y = self.random.randrange(self.grid.height)
            self.grid.place_agent(agent, (x, y))

    def init_ants(self):
        for i in range(self.num_ants):
            agent = AntAgent(self.next_id(), self)
            self.schedule.add(agent)

            self.grid.place_agent(agent, self.nest_pos)

    def init_fungus(self):
        agent = Fungus(self.next_id(), self)
        self.schedule.add(agent)
        self.grid.place_agent(agent, self.nest_pos)
        self.fungi.append(agent)

    def step(self):
        """
        A model step. Used for collecting data and advancing the schedule
        """
        self.datacollector.collect(self)
        self.schedule.step()

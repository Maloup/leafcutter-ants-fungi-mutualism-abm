from mesa import Agent

from .ant_agent import AntAgent


class Nest(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def ant_birth(self, n):
        for _ in range(n):
            agent = AntAgent(self.model.next_id(), self.model)
            self.model.schedule.add(agent)

            self.model.grid.place_agent(agent, self.pos)

    def step(self):
        # TODO: make this nice, parameterize some stuff. also, this should be
        #   somehow proportional to the amount of caretakers
        offspring_size = int(self.model.biomass_offspring_cvn*self.model.fungus.biomass)
        self.ant_birth(offspring_size)
        self.model.fungus.biomass -= offspring_size

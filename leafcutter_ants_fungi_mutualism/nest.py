from mesa import Agent

from .ant_agent import AntAgent


class Nest(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

    def ant_birth(self, n):
        for _ in range(n):
            agent = AntAgent(self.model.next_id(), self.model)
            self.model.schedule.add(agent)

            self.model.grid.place_agent(agent, self.model.nest_pos)

    def step(self):
        # TODO: make this nice, parameterize some stuff. also, this should be
        #   somehow proportional to the amount of caretakers
        offspring_size = int(0.1*self.model.fungi[0].biomass)
        self.ant_birth(offspring_size)
        self.model.fungi[0].biomass -= offspring_size

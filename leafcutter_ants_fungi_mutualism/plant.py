from mesa import Agent


class Plant(Agent):
    def __init__(self, unique_id, model, num_leaves=20):
        super().__init__(unique_id, model)
        self.initial_num_leaves = self.model.num_plant_leaves
        self.num_leaves = self.model.num_plant_leaves

    def take_leaf(self):
        self.num_leaves -= 1
        if self.num_leaves == 0:
            self.model.grid._remove_agent(self.pos, self)
            self.model.schedule.remove(self)

    def step(self):
        pass

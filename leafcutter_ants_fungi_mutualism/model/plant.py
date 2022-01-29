from mesa import Agent


class Plant(Agent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.initial_num_leaves = self.model.num_plant_leaves
        self.num_leaves = self.model.num_plant_leaves

    def take_leaf(self):
        if self.num_leaves >= 1:
            self.num_leaves -= 1
            return True

        return False

    def step(self):
        if self.num_leaves < self.initial_num_leaves:
            self.num_leaves += self.model.leaf_regrowth_rate

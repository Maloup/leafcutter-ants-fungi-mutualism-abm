from mesa import Agent


class Plant(Agent):
    """
    Plant agent, the main resource for the ants. Ants collect
    leaves from this agent and this agent regrows some of its leaves
    at every time step.
    """

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.initial_num_leaves = self.model.num_plant_leaves
        self.num_leaves = self.model.num_plant_leaves

    def take_leaf(self) -> bool:
        """
        Called by ants in the `HARVEST` state. One unit of leaf is removed.
        """
        if self.num_leaves >= 1:
            self.num_leaves -= 1
            return True

        return False

    def step(self) -> None:
        """
        The leaves regrow at a fixed rate up to a fixed upper bound.
        """
        if self.num_leaves < self.initial_num_leaves:
            self.num_leaves += self.model.leaf_regrowth_rate

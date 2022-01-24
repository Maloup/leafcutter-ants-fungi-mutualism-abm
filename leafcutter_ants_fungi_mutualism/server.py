"""
Configure visualization elements and instantiate a server
"""

from .model import (
    LeafcutterAntsFungiMutualismModel, AntAgent, Plant, Nest, Fungus
)
from .pheromone import Pheromone

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.modules import CanvasGrid, ChartModule
from mesa.visualization.UserParam import UserSettableParameter


def circle_portrayal_example(agent):
    if agent is None:
        return

    if isinstance(agent, AntAgent):
        portrayal = {
            "Shape": "circle",  # "leafcutter_ants_fungi_mutualism/resources/ant.png"
            "Color": "brown",
            "Layer": 1,
            "Filled": True,
            "r": 0.6
        }

        if agent.has_leaf:
            portrayal["text"] = "leaf"
            portrayal["text_color"] = "green"

        return portrayal
    elif isinstance(agent, Plant):
        return {
            "Shape": "circle",  # "leafcutter_ants_fungi_mutualism/resources/plant.png"
            "Color": "green",
            "Layer": 0,
            "r": agent.num_leaves/agent.initial_num_leaves
        }
    elif isinstance(agent, Nest):
        return {
            "Shape": "circle",
            "Color": "black",
            "Layer": 0,
            "r": 1
        }
    elif isinstance(agent, Fungus):
        portrayal = {
            "Shape": "circle",
            "Color": "purple",
            "Layer": 0,
            "r": 0.85
        }

        if agent.dead:
            portrayal["text"] = "dead"
            portrayal["text_color"] = "purple"

        return portrayal
    elif isinstance(agent, Pheromone):
        return {
            "Shape": "circle",
            "Color": "blue",
            "Layer": 0,
            "r": agent.lifespan/agent.initial_lifespan
        }
    else:
        print(f"Not yet visualized agent {agent.__class__}!")
        return {
            "Shape": "circle",
            "Color": "red",
            "Layer": 0,
            "r": 0.75
        }


canvas_element = CanvasGrid(circle_portrayal_example, 50, 50, 500, 500)
fungus_biomass_element = ChartModule([{
    "Label": "Fungus Biomass",
    "Color": "black"
}], data_collector_name="datacollector")
ants_biomass_element = ChartModule([{
    "Label": "Ant Biomass",
    "Color": "brown"
}], data_collector_name="datacollector")
ant_leaves_element = ChartModule([{
    "Label": "Ants with Leaves",
    "Color": "green"
}], data_collector_name="datacollector")

model_kwargs = {
    "num_ants": UserSettableParameter("slider", "Number of ants", 50, 1, 200, 1),
    "num_plants": UserSettableParameter("slider", "Number of plants", 30, 1, 100, 1),
    "num_plant_leaves": UserSettableParameter(
        "slider", "Number of leaves on plant", 100, 1, 500, 1
    ),
    "leaf_regrowth_rate": UserSettableParameter(
        "slider", "Leaf regrowth rate", 1/2, 0, 1, 0.01
    ),
    "pheromone_lifespan": UserSettableParameter(
        "slider", "Pheromone lifespan", 30, 1, 300, 1
    ),
    "ant_death_probability": UserSettableParameter(
        "slider", "Ant death probability", 0.01, 0.01, 0.5, 0.01
    ),
    "initial_fungus_energy": UserSettableParameter(
        "slider", "Initial fungus energy", 50, 1, 200, 1
    ),
    "fungus_decay_rate": UserSettableParameter(
        "slider", "Fungus decay rate", 1/50, 0, 1, 0.01
    ),
    "initial_foragers_ratio": UserSettableParameter(
        "slider", "Initial Foragers Ratio", 0.1, 0, 1, 0.01
    ),

    "width": 50,
    "height": 50
}

server = ModularServer(
    LeafcutterAntsFungiMutualismModel,
    [canvas_element, fungus_biomass_element,
        ants_biomass_element, ant_leaves_element],
    "LeafcutterAntsFungiMutualism",
    model_kwargs,
)

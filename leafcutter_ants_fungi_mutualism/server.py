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
    if agent is None or isinstance(agent, Fungus):
        return

    if isinstance(agent, AntAgent):
        portrayal = {
            "Shape": "circle", #"leafcutter_ants_fungi_mutualism/resources/ant.png"
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
            "Shape": "circle", #"leafcutter_ants_fungi_mutualism/resources/plant.png"
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

canvas_element = CanvasGrid(circle_portrayal_example, 50, 50, 650, 650)
fungus_energy_element = ChartModule([{
    "Label": "Fungus Energy",
    "Color": "black"
}], data_collector_name="datacollector")
ant_leaves_element = ChartModule([{
    "Label": "Ants with Leaves",
    "Color": "green"
}], data_collector_name="datacollector")

model_kwargs = {
    "num_ants": UserSettableParameter("slider", "Number of ants", 50, 1, 200, 1),
    "num_plants": UserSettableParameter("slider", "Number of plants", 20, 1, 100, 1),
    "pheromone_lifespan": UserSettableParameter("slider", "Pheromone lifespan", 75, 1, 300, 1),
    "num_plant_leaves": UserSettableParameter("slider", "Number of leaves on plant", 20, 1, 100, 1),
    "width": 50,
    "height": 50
}

server = ModularServer(
    LeafcutterAntsFungiMutualismModel,
    [canvas_element, fungus_energy_element, ant_leaves_element],
    "LeafcutterAntsFungiMutualism",
    model_kwargs,
)

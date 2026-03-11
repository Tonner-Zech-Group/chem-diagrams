"""Main EnergyDiagram class"""

from importlib.metadata import version

from .energy_diagram import EnergyDiagram

__version__ = version("chemdiagrams")

__all__ = [
    "EnergyDiagram",
    "__version__",
]

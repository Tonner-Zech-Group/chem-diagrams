from __future__ import annotations
from typing import TYPE_CHECKING

from dataclasses import dataclass
from collections.abc import Sequence

if TYPE_CHECKING:
    from matplotlib.lines import Line2D
    from matplotlib.text import Annotation

from ..validation import Validators
from .. import constants
from . import FigureManager




class PathManager:
    """
    PathManager class for handling the Paths

    """

    def __init__(
            self,
            figure_manager: FigureManager,
        ) -> None:
        self.figure_manager = figure_manager
        self.path_data = {}
        self.mpl_objects = {}

    def draw_path(
            self, 
            x_data: Sequence[float], 
            y_data: Sequence[float], 
            color: str, 
            linetypes: Sequence[int] | None = None, 
            path_name: str | None = None, 
            show_numbers: bool = True
        ) -> None:
        
        # Sanity checks and linetype normalization
        Validators._validate_numeric_sequence(x_data, "x_data")
        Validators._validate_numeric_sequence(y_data, "y_data")
        if not isinstance(path_name, (str, type(None))):
            raise TypeError("path_name must be a string or None")
        if path_name in list(self.path_data.keys()):
            raise ValueError("path_name must not already exist")
        if len(x_data) != len(y_data):
            raise ValueError("x_data and y_data must have the same length")

        ALLOWED_LINETYPES = [-2, -1, 0, 1, 2]
        if linetypes is None:
            linetypes = [1] * (len(y_data)-1)
        elif isinstance(linetypes, int):
            if linetypes not in ALLOWED_LINETYPES:
                raise ValueError(f"linetype must be in {ALLOWED_LINETYPES}.")
            linetypes = [linetypes] * (len(y_data)-1)
        elif isinstance(linetypes, Sequence):
            if not all(val in ALLOWED_LINETYPES for val in linetypes):
                raise ValueError(f"linetype elements must be in {ALLOWED_LINETYPES}.")
            if len(linetypes) != len(x_data) - 1 or len(linetypes) != len(y_data) - 1:
                raise ValueError(f"Length of linetypes + 1 (now {len(linetypes)} + 1) must equal the number of data points (right now {len(x_data)}).")
        else:
            raise TypeError("linetypes must be an tuple, list or integer.")
        
        # Save data for numbering or legend
        has_label = True
        if path_name is None:
            has_label = False
            path_name = f"__NONAME{len(self.path_data)}"
        self.path_data[path_name] = {
            "x": x_data, 
            "y": y_data, 
            "color": color, 
            "has_label": has_label, 
            "show_numbers": show_numbers,
        }

        # Initialize nested dics
        connections = {}
        plateaus = {}

        # Create lists in order to draw the lines
        x_corners = []
        y_corners = []
        linetypes = linetypes

        # Draw the lines
        for i, v in enumerate(y_data):
            x_corners.append(x_data[i]-0.5*constants.WIDTH_PLATEAU)
            x_corners.append(x_data[i]+0.5*constants.WIDTH_PLATEAU)
            y_corners.append(y_data[i])
            y_corners.append(y_data[i])
            plateau = self.figure_manager.ax.hlines(v, x_data[i]-0.25, x_data[i]+0.25, zorder=2, lw=1.8, color=color, capstyle='round')
            plateaus[f"{x_data[i]:.1f}"] = plateau
            if i > 0:
                connector = self._draw_connector(x_corners[-3:-1],y_corners[-3:-1], linetypes[i-1], color)
                connections[f"{sum(x_corners[-3:-1]) / 2:.1f}"] = connector

        # Save Path
        self.mpl_objects[path_name] = PathObject(connections, plateaus)

    def _draw_connector(
            self, 
            x_coords: Sequence[float], 
            y_coords: Sequence[float], 
            linetype: int, 
            color: str
        ) -> Line2D | dict[str, Line2D | Annotation] | None:
        if linetype == 0:
            connector = None
        elif linetype == 1:
            connector = self._draw_dotted_line(x_coords, y_coords, color)
        elif linetype == -1:
            connector = self._draw_broken_line(x_coords, y_coords, color, dotted=True)
        elif linetype == 2:
            connector = self._draw_line(x_coords, y_coords, color)
        elif linetype == -2:
            connector = self._draw_broken_line(x_coords, y_coords, color, dotted=False)
        else:
            raise ValueError(f"Invalid linetype argument: {linetype}")
        return connector

    def _draw_dotted_line(self, 
            x_coords: Sequence[float], 
            y_coords: Sequence[float], 
            color: str
        ) -> Line2D:
        return self.figure_manager.ax.plot(x_coords, y_coords, zorder=1, ls=':', lw=1.0, color=color)[0]
    
    def _draw_line(self, 
            x_coords: Sequence[float], 
            y_coords: Sequence[float], 
            color: str
        ) -> Line2D:
        return self.figure_manager.ax.plot(x_coords, y_coords, zorder=1, ls='-', lw=0.8, color=color)[0]

    def _draw_broken_line(self, 
            x_coords: Sequence[float], 
            y_coords: Sequence[float], 
            color: str, 
            dotted: bool = True
        ) -> dict[str, Line2D | Annotation]:
        # Portion of the line that has a gap
        linegap = 0.2 
        # Ensure tuples are converted to list
        x_coords = list(x_coords)
        y_coords = list(y_coords)

        # Draw first part of line
        x1 = x_coords.copy()
        y1 = y_coords.copy()
        x1[1] = x1[0] + (x1[1]-x1[0])*(0.5-linegap/2)
        y1[1] = y1[0] + (y1[1]-y1[0])*(0.5-linegap/2)
        if dotted:
            line_1 = self._draw_dotted_line(x1, y1, color=color)
        else:
            line_1 = self._draw_line(x1, y1, color=color)

        # Draw second part of line
        x2 = x_coords.copy()
        y2 = y_coords.copy()
        x2[0] = x2[0] + (x2[1]-x2[0])*(0.5+linegap/2)
        y2[0] = y2[0] + (y2[1]-y2[0])*(0.5+linegap/2)
        if dotted:
            line_2 = self._draw_dotted_line(x2, y2, color=color)
        else:
            line_2 = self._draw_line(x2, y2, color=color)

        # Draw small orthogonal lines
        stopper_1 = self.figure_manager.ax.annotate('', xy=(x1[1], y1[1]), xytext=(x1[1]+0.001*(x2[0]-x1[1]), y1[1]+0.001*(y2[0]-y1[1])), 
                arrowprops=dict(arrowstyle='|-|', color=color, lw=0.8, shrinkA=15, shrinkB=15, mutation_scale=3,zorder=1)
        )
        stopper_2 = self.figure_manager.ax.annotate('', xy=(x2[0], y2[0]), xytext=(x2[0]-0.001*(x2[0]-x1[1]), y2[0]-0.001*(y2[0]-y1[1])), 
                arrowprops=dict(arrowstyle='|-|', color=color, lw=0.8, shrinkA=15, shrinkB=15, mutation_scale=3,zorder=1)
        )
        return BrokenLine(line_1, line_2, stopper_1, stopper_2)
        

@dataclass
class PathObject:
    connections: dict
    plateaus: dict

    def remove(self):
        for _, connection in self.connections.items():
            connection.remove()
        for _, plateau in self.plateaus.items():
            plateau.remove()

@dataclass
class BrokenLine:
    line_part_1: Line2D
    line_part_2: Line2D
    stopper_1: Annotation
    stopper_2: Annotation

    def remove(self):
        self.line_part_1.remove()
        self.line_part_2.remove()
        self.stopper_1.remove()
        self.stopper_2.remove()

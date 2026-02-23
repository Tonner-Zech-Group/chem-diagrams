from __future__ import annotations

from ..validation import Validators
from .. import constants
from . import FigureManager

class LayoutManager:
    """
    LayoutManager class for handling the Styles

    """

    def __init__(
            self,
            figure_manager: FigureManager,
            extra_x_margin: tuple[float, float] | list[float],
            extra_y_margin: tuple[float, float] | list[float],
            no_width_limit: bool,
            figsize: tuple[float, float] | list[float] | None = None, 
        ) -> None:
        Validators.validate_numeric_sequence(figsize, "figsize", allow_none=True, min_value=0, required_length=2)
        Validators.validate_numeric_sequence(extra_x_margin, "extra_x_margin", required_length=2)
        Validators.validate_numeric_sequence(extra_y_margin, "extra_x_margin", required_length=2)

        self.figure_manager = figure_manager
        self.figsize = figsize
        self.extra_x_margin = extra_x_margin
        self.extra_y_margin = extra_y_margin
        self.no_width_limit = no_width_limit


    def adjust_xy_limits(self, path_data: dict) -> dict[str, tuple]:
        # Get all x and y values out of the path data dictionary
        x_all = [
                element
                for path in path_data.values()
                if path and len(path) > 0
                for element in path["x"]
            ]
        y_all = [
                element
                for path in path_data.values()
                if path and len(path) > 0
                for element in path["y"]
            ]
        # Add values if no path was added yet to avoid errors
        if len(x_all) == 0:
            x_all = [0]
        if len(y_all) == 0:
            y_all = [0,10]

        # Adjust the axis limits
        margins = {
            "x": (
                min(x_all) 
                + constants.DEFAULT_X_MARGINS[0] 
                + self.extra_x_margin[0], 
                max(x_all) 
                + constants.DEFAULT_X_MARGINS[1] 
                + self.extra_x_margin[1],
            ),
            "y": (
                min(y_all) 
                + (max(y_all)-min(y_all)) 
                * (constants.DEFAULT_Y_MARGINS[0] + self.extra_y_margin[0]), 
                max(y_all) 
                + (max(y_all)-min(y_all)) 
                * (constants.DEFAULT_Y_MARGINS[1] + self.extra_y_margin[1]),
            )
        }
        self.figure_manager.ax.set_xlim(margins["x"])
        self.figure_manager.ax.set_ylim(margins["y"])

        return margins

    def scale_figure(self, path_data: dict) -> tuple[float, float]:
        # Scale only, if no figure size is predetermined
        if self.figsize is None:
            # Function for scaling the figure automatically
            margins = self.adjust_xy_limits(path_data)

            # Determine and set width
            x_size = constants.X_SCALE*(margins["x"][1] - margins["x"][0])
            if x_size > constants.MAX_WIDTH and not self.no_width_limit:
                x_size = constants.MAX_WIDTH
            if x_size <= 0: # Avoid a figure without size
                x_size = 1
            self.figure_manager.fig.set_figwidth(x_size)

            # Determine and set height
            y_size = constants.HEIGHT
            if y_size > x_size:
                y_size = x_size  # Avoid ugly diagrams
            self.figure_manager.fig.set_figheight(y_size)
            return (x_size, y_size)
        
        else:
            self.adjust_xy_limits(path_data)
            self.figure_manager.fig.set_figwidth(self.figsize[0])
            self.figure_manager.fig.set_figheight(self.figsize[1])
            return self.figsize[:]



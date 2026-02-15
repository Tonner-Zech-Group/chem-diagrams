from __future__ import annotations
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
from matplotlib import font_manager

if TYPE_CHECKING:
    from collections.abc import Sequence

from ..validation import Validators
from .. import constants


class FigureManager:
    """
    FigureManager class for handling the figure

    """

    def __init__(
            self,
            fontsize: int = 8, 
            dpi: int = 150,
            verbose: bool = False, 
        ) -> None:

        # Sanity checks
        Validators._validate_number(fontsize, "fontsize", min_value=0)
        Validators._validate_number(dpi, "dpi", min_value=0)

        # Initialize the diagram, get the axis and set axis limits
        self.fig = plt.figure(dpi=dpi)
        self.ax = self.fig.gca()
        self.ax.tick_params(which='both', direction="inout", top=False, right=False, bottom=False)
        self.ax.tick_params(which='both',labelsize=fontsize)
        self.fontsize = fontsize
        self.mpl_objects = {}

    def set_xlabels(
            self, 
            labels: Sequence, 
            labelplaces: Sequence[float] | None = None, 
            fontsize: int | None = None, 
            weight: str = "bold", 
            in_plot: bool = False
        ) -> None:

        # Sanity checks
        Validators._validate_numeric_sequence(labelplaces, "labelplaces", allow_none=True)
        Validators._validate_number(fontsize, "fontsize", allow_none=True, min_value=0)
        if labelplaces is not None:
            if len(labels) != len(labelplaces):
                raise ValueError("There must be the same number of labels and labelplaces.")

        # Create labelplace list if none given
        if labelplaces is None:
            labelplaces = list(range(len(labels)))
        self.labelproperties = {
            "labels": labels,
            "labelplaces": labelplaces,
            "fontsize": fontsize,
            "weight": weight,
            "in_plot": in_plot,
        }

        # Clear or hide labels if present
        self.ax.set_xticks([])
        for mpl_object in self.mpl_objects.values():
            mpl_object.remove()
        self.mpl_objects = {}

        # Set font of x labels
        if fontsize is None:
            fontsize = self.fontsize
        labelfont = font_manager.FontProperties(
            weight=weight, size=fontsize)

        # Set labels in the plot or at axis
        if in_plot:       
            for x, labeltext in zip(labelplaces, labels):
                if all_values_at_x := self._get_all_values_at_x(x):
                    y_diff = - constants.DISTANCE_LABEL_LINE * (
                        self.ax.get_ylim()[1] - self.ax.get_ylim()[0]
                    )
                    y_min_at_x = min(all_values_at_x)
                    label = self.ax.text(
                        x,
                        y_min_at_x + y_diff,
                        labeltext,
                        font=labelfont,
                        ha="center",
                        va="center",
                    )
                    self.mpl_objects[str(x)] = label
                else:
                    print(f"Warning: There was no datapoint found at x = {x}")
        else:
            self.ax.set_xticks(labelplaces)
            self.ax.set_xticklabels(labels)
            for label in self.ax.get_xticklabels():
                label.set_fontproperties(labelfont)


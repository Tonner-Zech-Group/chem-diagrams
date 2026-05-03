from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
from matplotlib.axes import Axes

if TYPE_CHECKING:
    pass

from ..validation import Validators


class FigureManager:
    """
    Creates and owns the Matplotlib figure and axes used by the diagram.

    Acts as the central reference point for all other managers, which
    access the figure and axes through this object rather than holding
    their own references.
    """

    def __init__(self, fontsize: int, dpi: int = 150, ax: Axes | None = None) -> None:
        """
        Initialize the Matplotlib figure and configure default tick styling.

        Parameters
        ----------
        fontsize : int, optional
            Base font size applied to axis tick labels throughout the diagram.
            Default is ``constants.STD_FONTSIZE``.
        dpi : int, optional
            Resolution of the figure in dots per inch. Default is 150.
        ax : matplotlib.axes.Axes or None, optional
            External Matplotlib axes to use for the diagram. If None, a new figure
            and axes are created internally. If provided, the figure from this axes
            is used. Default is None.
        """

        # Sanity checks
        Validators.validate_number(fontsize, "fontsize", min_value=0)
        Validators.validate_number(dpi, "dpi", min_value=0)

        # Create ax and fig or use external ax if provided
        if ax is not None:
            if not isinstance(ax, Axes):
                raise TypeError("ax must be a matplotlib.axes.Axes object.")
            self.ax = ax
            fig = ax.get_figure()
            if not isinstance(fig, plt.Figure):
                raise TypeError(
                    "The provided ax does not belong to a valid Matplotlib figure."
                )
            self.fig = fig
            self.has_external_ax = True
        else:
            self.fig = plt.figure(dpi=dpi)
            self.ax = self.fig.gca()
            self.has_external_ax = False

        # Configure axis
        self.ax.tick_params(
            which="both", direction="inout", top=False, right=False, bottom=False
        )
        self.ax.tick_params(which="both", labelsize=fontsize)
        self.ax.set_xticks([])
        self.ax.set_axisbelow(True)
        self.fontsize = fontsize

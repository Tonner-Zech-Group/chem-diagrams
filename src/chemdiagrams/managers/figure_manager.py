from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.pyplot as plt

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

    def __init__(
        self,
        fontsize: int,
        dpi: int = 150,
    ) -> None:
        """
        Initialize the Matplotlib figure and configure default tick styling.

        Parameters
        ----------
        fontsize : int, optional
            Base font size applied to axis tick labels throughout the diagram.
            Default is ``constants.STD_FONTSIZE``.
        dpi : int, optional
            Resolution of the figure in dots per inch. Default is 150.
        """

        # Sanity checks
        Validators.validate_number(fontsize, "fontsize", min_value=0)
        Validators.validate_number(dpi, "dpi", min_value=0)

        # Initialize the diagram, get the axis and set axis limits
        self.fig = plt.figure(dpi=dpi)
        self.ax = self.fig.gca()
        self.ax.tick_params(
            which="both", direction="inout", top=False, right=False, bottom=False
        )
        self.ax.tick_params(which="both", labelsize=fontsize)
        self.ax.set_xticks([])
        self.ax.set_axisbelow(True)
        self.fontsize = fontsize

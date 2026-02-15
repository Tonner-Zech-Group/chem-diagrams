from __future__ import annotations
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt


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
        Validators.validate_number(fontsize, "fontsize", min_value=0)
        Validators.validate_number(dpi, "dpi", min_value=0)

        # Initialize the diagram, get the axis and set axis limits
        self.fig = plt.figure(dpi=dpi)
        self.ax = self.fig.gca()
        self.ax.tick_params(which='both', direction="inout", top=False, right=False, bottom=False)
        self.ax.tick_params(which='both',labelsize=fontsize)
        self.fontsize = fontsize




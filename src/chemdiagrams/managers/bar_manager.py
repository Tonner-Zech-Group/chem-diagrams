from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from matplotlib.lines import Line2D
    from matplotlib.text import Annotation, Text



from .. import constants
from ..validation import Validators
from .figure_manager import FigureManager


class BarManager:
    """
    Manages the creation and storage of energy difference bars.

    Handles drawing of annotated double-headed arrows that span between
    two energy levels, including optional horizontal whisker lines and
    text labels. Rendered artists are stored in ``mpl_objects`` for
    later access via ``EnergyDiagram.bars``.
    """

    def __init__(
            self,
            figure_manager: FigureManager,
        ) -> None:
        self.figure_manager = figure_manager
        self.mpl_objects: list = []


    def draw_difference_bar(
            self, 
            x: float, 
            y_start_end: tuple[float, float] | list[float], 
            description: str,
            margins: dict, 
            diff: float | None = None,
            left_side: bool = False,
            add_difference: bool = True,
            fontsize: int | None = None, 
            color: str = "black", 
            arrowstyle: str = "|-|", 
            x_whiskers: Sequence[float | None] = (None, None), 
            whiskercolor: str | None = None,
        ) -> None:

        # Sanity checks
        Validators.validate_number(x, "x")
        Validators.validate_numeric_sequence(
            y_start_end, "y_start_end", required_length=2
        )
        Validators.validate_number(
            fontsize, "fontsize", allow_none=True, min_value=0
        )
        Validators.validate_number(diff, "diff", allow_none=True)
        if not isinstance(x_whiskers, Sequence):
            raise TypeError("x_whiskers must be a list or tuple of length 2.")
        if len(x_whiskers) != 2:
            raise ValueError("x_whiskers must be a list or tuple of length 2.")
        if not all(isinstance(val, (float, int, type(None))) for val in x_whiskers):
            raise ValueError("Elements of x_whiskers must be a float or None.")

        y_start, y_end = y_start_end
        if fontsize is None:
            fontsize = self.figure_manager.fontsize

        # Automatic scaling of diff
        if diff is None:
            diff = constants.DISTANCE_TEXT_DIFFBAR
            diff *= margins["x"][1] - margins["x"][0]
            diff /= (self.figure_manager.fig.get_figwidth())
        
        # Adjust diff and ha to side
        if left_side:
            diff *= -1
            horizontal_alignment = "right"
        else:
            horizontal_alignment = "left"

        # Draw vertical bar
        bar = self.figure_manager.ax.annotate(
                    '', 
                    xy=(x, y_end), 
                    xytext=(x, y_start), 
                    arrowprops=dict(
                        arrowstyle=arrowstyle, 
                        color=color, 
                        lw=0.7, 
                        shrinkA=0, #no whitespace above and below the Bar
                        shrinkB=0, #no whitespace above and below the Bar
                        mutation_scale=3 #scaling of the horizontal caps
                        )
                )
                   
        # Draw text next to bar
        if add_difference:
            difference_str =  str(round(y_end-y_start))
        else:
            difference_str = ""
        text = self.figure_manager.ax.text(
                    x + diff, (y_start + y_end) / 2,  
                    description + difference_str,  
                    ha=horizontal_alignment, va='center', 
                    fontsize=fontsize, color=color, 
                )
        

        # Draw the whiskers
        if whiskercolor is None:
            whiskercolor = color
        whisker_1 = None
        whisker_2 = None
        for i, x_whisker in enumerate(x_whiskers):
            if x_whisker is not None:
                whisker = self.figure_manager.ax.plot(
                    (x_whisker, x),
                    (y_start_end[i], y_start_end[i]),
                    zorder=0.8, 
                    ls=':', 
                    lw=0.7, 
                    color=whiskercolor
                )[0]
                if i == 0:
                    whisker_1 = whisker
                elif i == 1:
                    whisker_2 = whisker
        
        # Save whiskers
        self.mpl_objects.append(DifferenceBar(bar, text, whisker_1, whisker_2))


@dataclass
class DifferenceBar:
    """
    Container for the Matplotlib artists that make up a single difference bar.

    Attributes
    ----------
    bar : Annotation
        The double-headed arrow spanning the two energy levels.
    text : Text
        The label displayed beside the arrow.
    whisker_1 : Line2D or None
        Horizontal whisker line at the bottom energy level, or None if not drawn.
    whisker_2 : Line2D or None
        Horizontal whisker line at the top energy level, or None if not drawn.
    """
    bar: Annotation
    text: Text
    whisker_1: Line2D | None
    whisker_2: Line2D | None
    
    
        
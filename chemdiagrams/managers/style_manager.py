from __future__ import annotations
from typing import TYPE_CHECKING

from dataclasses import dataclass
from collections.abc import Sequence

from matplotlib import font_manager

from ..validation import Validators
from .. import constants
from . import FigureManager, NumberManager


if TYPE_CHECKING:
    from matplotlib.text import Annotation, Text
    from matplotlib.lines import Line2D

class StyleManager:
    """
    Manages the visual style and x-axis labels of the diagram.

    Handles spine visibility, axis arrows, and background elements
    for the four supported styles: ``"boxed"``, ``"halfboxed"``,
    ``"open"``, and ``"twosided"``. Also manages x-axis label
    placement, either below the axis or inside the plot area.
    """

    def __init__(
            self,
            figure_manager: FigureManager,
            style: str,
        ) -> None:
        self.figure_manager = figure_manager
        self.style = style
        self.mpl_objects = StyleObjects({},{},{})
        self.set_diagram_style(self.style)
        

    
    
    def set_diagram_style(self, style: str) -> None:
        def draw_arrow(xy, xytext):
            arrow = self.figure_manager.ax.annotate(
                    '', 
                    xy=xy, 
                    xytext=xytext,
                    xycoords="axes fraction", 
                    arrowprops=dict(
                        arrowstyle='-|>', 
                        color="black", 
                        lw=0.8,
                        shrinkA=0,
                        shrinkB=0, 
                        mutation_scale=10,
                        zorder=1
                        )
                 )
            return arrow
        
        ALLOWED_STYLES = ["boxed", "halfboxed", "open", "twosided"]

        if style not in ALLOWED_STYLES:
            raise ValueError(f"style must be one of {ALLOWED_STYLES}.")

        # Remove grid lines and set x axes to default height
        self.figure_manager.ax.xaxis.grid(False)
        self.figure_manager.ax.yaxis.grid(False)
        self.figure_manager.ax.spines["bottom"].set_position(('axes', 0))
        
        # Remove unwanted objects
        self.mpl_objects.remove_axes()
        axes_dict = {}
        arrows_dict = {}
        
        # Adjust axes
        if style == "boxed":
            self.figure_manager.ax.spines["top"].set_visible(True)
            self.figure_manager.ax.spines["right"].set_visible(True)
            self.figure_manager.ax.spines["left"].set_visible(True)
            self.figure_manager.ax.spines["bottom"].set_visible(True)

        elif style == "halfboxed":
            self.figure_manager.ax.spines["top"].set_visible(False)
            self.figure_manager.ax.spines["right"].set_visible(False)
            self.figure_manager.ax.spines["left"].set_visible(True)
            self.figure_manager.ax.spines["bottom"].set_visible(True)
            arrows_dict["x_arrow"] = draw_arrow((1.02, 0),(0.97, 0))
            arrows_dict["y_arrow"] = draw_arrow((0, 1.02),(0, 0.97))
            
        elif style == "open":
            self.figure_manager.ax.spines["top"].set_visible(False)
            self.figure_manager.ax.spines["right"].set_visible(False)
            self.figure_manager.ax.spines["left"].set_visible(True)
            self.figure_manager.ax.spines["bottom"].set_visible(False)
            axes_dict["x_axis"] = self.figure_manager.ax.axhline(0, color="black", zorder=0.5, lw=1.0)
            arrows_dict["y_arrow"] = draw_arrow((0, 1.02),(0, 0.97))

        elif style == "twosided":
            self.figure_manager.ax.spines["top"].set_visible(False)
            self.figure_manager.ax.spines["right"].set_visible(False)
            self.figure_manager.ax.spines["left"].set_visible(True)
            self.figure_manager.ax.spines["bottom"].set_visible(True)
            self.figure_manager.ax.spines["bottom"].set_position(('axes', -0.03))
            arrows_dict["x_arrow_right"] = draw_arrow((1.01, -0.03),(0.96, -0.03))
            arrows_dict["x_arrow_left"] = draw_arrow((-0.01, -0.03),(0.04, -0.03))
            arrows_dict["y_arrow"] = draw_arrow((0, 1.02),(0, 0.97))

        self.mpl_objects.arrows = arrows_dict
        self.mpl_objects.axes = axes_dict



    def set_xlabels(
            self,
            margins: dict[str, tuple],
            figsize: tuple[float, float],
            path_data: dict, 
            labels: Sequence, 
            labelplaces: Sequence[float] | None = None, 
            fontsize: int | None = None, 
            weight: str = "bold", 
            in_plot: bool = False
        ) -> None:

        # Sanity checks
        Validators.validate_numeric_sequence(labelplaces, "labelplaces", allow_none=True)
        Validators.validate_number(fontsize, "fontsize", allow_none=True, min_value=0)
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
        self.figure_manager.ax.set_xticks([])
        self.mpl_objects.remove_labels()
        label_dict = {}

        # Set font of x labels
        if fontsize is None:
            fontsize = self.figure_manager.fontsize
        labelfont = font_manager.FontProperties(
            weight=weight, 
            size=fontsize
        )

        # Set labels in the plot or at axis
        if in_plot:       
            for x, labeltext in zip(labelplaces, labels):
                all_values_at_x = NumberManager._get_all_values_at_x(path_data, x)
                if all_values_at_x:
                    y_diff = - constants.DISTANCE_LABEL_LINE * (
                        (fontsize / constants.STD_FONTSIZE)
                        * (margins["y"][1] - margins["y"][0])
                        / figsize[1] 
                    )
                    y_min_at_x = min(all_values_at_x)
                    label = self.figure_manager.ax.text(
                        x,
                        y_min_at_x + y_diff,
                        labeltext,
                        font=labelfont,
                        ha="center",
                        va="center",
                    )
                    label_dict[f"{x:.1f}"] = label
                else:
                    print(f"Warning: There was no datapoint found at x = {x}, therfore no label is shown.")
            self.mpl_objects.x_labels = label_dict
        else:
            self.figure_manager.ax.set_xticks(labelplaces)
            self.figure_manager.ax.set_xticklabels(labels)
            for label in self.figure_manager.ax.get_xticklabels():
                label.set_fontproperties(labelfont)


@dataclass
class StyleObjects:
    """
    Container for the Matplotlib artists controlled by the style manager.

    Attributes
    ----------
    arrows : dict of str to Annotation
        Axis arrow artists, keyed by name (e.g. ``"x_arrow"``, ``"y_arrow"``).
    axes : dict of str to Line2D
        Supplementary axis line artists, such as the horizontal zero line
        in the ``"open"`` style, keyed by name (e.g. ``"x_axis"``).
    x_labels : dict of str to Text
        In-plot x label artists, keyed by x-coordinate as a formatted
        string. Only populated when ``in_plot=True`` is used in
        ``set_xlabels``; otherwise labels are handled by Matplotlib's
        own tick system and not stored here.
    """
    arrows: dict[str, Annotation]
    axes: dict[str, Line2D]
    x_labels: dict[str, Text]

    def remove_axes(self):
        for _, arrow in self.arrows.items():
            arrow.remove()
        for _, axis in self.axes.items():
            axis.remove()
        self.arrows = {}
        self.axes = {}
    
    def remove_labels(self):
        for _, label in self.x_labels.items():
            label.remove()
        self.x_labels = {}



    
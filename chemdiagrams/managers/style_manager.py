from __future__ import annotations
from typing import TYPE_CHECKING

from dataclasses import dataclass
from collections.abc import Sequence

from matplotlib import font_manager
import matplotlib.patches as mpatches
import numpy as np

from ..validation import Validators
from .. import constants
from . import FigureManager, NumberManager


if TYPE_CHECKING:
    from matplotlib.text import Annotation, Text
    from matplotlib.lines import Line2D
    from matplotlib.patches import Rectangle

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
        self.mpl_objects = StyleObjects({},{},{},{},{})
        self.axes_break_data = {"x": [], "y": []}
        self.has_axes_breaks = False
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
                        lw=0.0,
                        shrinkA=0,
                        shrinkB=0, 
                        mutation_scale=12,
                        zorder=1
                        )
                 )
            return arrow
        
        ALLOWED_STYLES = ["boxed", "halfboxed", "open", "twosided"]

        if style not in ALLOWED_STYLES:
            raise ValueError(f"style must be one of {ALLOWED_STYLES}.")
        
        self.style = style

        # Remove grid lines and set x axes to default cover_width
        self.figure_manager.ax.xaxis.grid(False)
        self.figure_manager.ax.yaxis.grid(False)
        self.figure_manager.ax.spines["bottom"].set_position(('axes', 0))
        self.figure_manager.ax.set_zorder(0.5)
        
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
            axes_dict["x_axis"] = self.figure_manager.ax.axhline(0, color="black", zorder=0.5, lw=0.8)
            arrows_dict["y_arrow"] = draw_arrow((0, 1.02),(0, 0.97))

        elif style == "twosided":
            self.figure_manager.ax.spines["top"].set_visible(False)
            self.figure_manager.ax.spines["right"].set_visible(False)
            self.figure_manager.ax.spines["left"].set_visible(True)
            self.figure_manager.ax.spines["bottom"].set_visible(True)
            self.figure_manager.ax.spines["bottom"].set_position(
                ('axes', constants.X_AXIS_OFFSET_OPENSTYLE)
            )
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

    def add_xaxis_break(
            self,
            margins: dict[str, tuple],
            figsize: tuple[float, float],
            x: float,
            gap_scale: float = 1,
            stopper_scale: float = 1,
            angle: float =  30,
        ) -> None:

        def draw_xaxis_break(x_pos, y_pos):
            # gap in x data coords
            gap = (
                constants.STD_BREAK_GAP
                * (margins["x"][1] - margins["x"][0])
                / figsize[0]
                * gap_scale
            )

            # cover_width in y axis fraction
            cover_width = (
                constants.STD_BREAK_COVER_WIDTH
                / figsize[1]
            )

            # Add white covering reactange 
            # x in data coords, y in axis fractions
            rect = mpatches.Rectangle(
                (x_pos - gap / 2, y_pos - cover_width / 2),                         
                gap,       
                cover_width,                          
                transform=self.figure_manager.ax.get_xaxis_transform(),
                facecolor='white',
                edgecolor='white',
                zorder=4.5,
                clip_on=False,
            )
            self.figure_manager.ax.add_artist(rect)
            
            # Convert stopper angle
            # delta_x in data coords, delta_y in axis coords
            delta_x = np.cos(angle * np.pi / 180) * 0.001
            delta_y = (
                np.sin(angle * np.pi / 180) 
                * 0.001
                / (margins["x"][1] - margins["x"][0])
                * figsize[1]
                / figsize[0]
            )

            # Draw stoppers
            stopper_1 = self.figure_manager.ax.annotate(
                '', 
                xy=(x_pos - gap/2, y_pos), 
                xytext=(
                    x_pos - gap/2 + delta_x, 
                    y_pos + delta_y
                ),
                xycoords=self.figure_manager.ax.get_xaxis_transform(),
                arrowprops=dict(
                    arrowstyle='|-|', 
                    color="black", 
                    lw=0.8, 
                    shrinkA=15, 
                    shrinkB=15, 
                    mutation_scale=3*stopper_scale,
                    zorder=0.7,
                )
            )
            stopper_1.set_zorder(5)

            stopper_2 = self.figure_manager.ax.annotate(
                '', 
                xy=(x_pos + gap/2, y_pos), 
                xytext=(
                    x_pos + gap/2 + delta_x, 
                    y_pos + delta_y
                ),
                xycoords=self.figure_manager.ax.get_xaxis_transform(),
                arrowprops=dict(
                    arrowstyle='|-|', 
                    color="black", 
                    lw=0.8, 
                    shrinkA=15, 
                    shrinkB=15, 
                    mutation_scale=3*stopper_scale,
                    zorder=0.7,
                )
            )
            stopper_2.set_zorder(5)

            return AxisBreak(rect, stopper_1, stopper_2)
        
        self.has_axes_breaks = True
        if self.style == "open":
            raise NotImplementedError("x-axis breaks are not compatible with open diagram style")
        elif self.style == "halfboxed":
            break_object = draw_xaxis_break(x, 0) 
        elif self.style == "boxed":
            break_object_bottom = draw_xaxis_break(x, 0)
            break_object_top = draw_xaxis_break(x, 1)
            break_object = {
                "top": break_object_top,
                "bottom": break_object_bottom,
            }
        elif self.style == "twosided":
            break_object = draw_xaxis_break(x, constants.X_AXIS_OFFSET_OPENSTYLE)

        self.mpl_objects.xaxis_breaks[f"{x:.1f}"] = break_object

        # Save for redrawing
        self.axes_break_data["x"].append({
            "x": x,
            "gap_scale": gap_scale,
            "stopper_scale": stopper_scale,
            "angle": angle,
        })



    def add_yaxis_break(
            self,
            margins: dict[str, tuple],
            figsize: tuple[float, float],
            y: float,
            gap_scale: float = 1,
            stopper_scale: float = 1,
            angle: float = 30,
        ) -> None:

        def draw_xaxis_break(x_pos, y_pos):
            # Gap in y data coords
            gap = (
                constants.STD_BREAK_GAP
                * (margins["y"][1] - margins["y"][0])
                / figsize[1]
                * gap_scale
            )

            # Cover_width in x axis fraction
            cover_width = (
                constants.STD_BREAK_COVER_WIDTH
                / figsize[0]

            )

            # Add white covering reactange 
            # y in data coords, x in axis fractions
            rect = mpatches.Rectangle(
                (x_pos - cover_width / 2, y_pos - gap / 2),                         
                cover_width,       
                gap,                          
                transform=self.figure_manager.ax.get_yaxis_transform(),
                facecolor='white',
                edgecolor='white',
                zorder=4.5,
                clip_on=False,
            )
            self.figure_manager.ax.add_artist(rect)

            # Convert stopper angle
            delta_x = (
                np.sin(angle * np.pi / 180) 
                * 0.001
                / (margins["y"][1] - margins["y"][0])
                * figsize[1]
                / figsize[0]
            )
            delta_y = (
                np.cos(angle * np.pi / 180) 
                * 0.001
            )

            # Draw stoppers
            stopper_1 = self.figure_manager.ax.annotate(
                '', 
                xy=(x_pos, y_pos - gap/2), 
                xytext=(
                    x_pos + delta_x, 
                    y_pos - gap/2 + delta_y
                ),
                xycoords=self.figure_manager.ax.get_yaxis_transform(),
                arrowprops=dict(
                    arrowstyle='|-|', 
                    color="black", 
                    lw=0.8, 
                    shrinkA=15, 
                    shrinkB=15, 
                    mutation_scale=3*stopper_scale,
                    zorder=0.7,
                )
            )
            stopper_1.set_zorder(5)

            stopper_2 = self.figure_manager.ax.annotate(
                '', 
                xy=(x_pos, y_pos + gap/2), 
                xytext=(
                    x_pos + delta_x, 
                    y_pos + gap/2 + delta_y
                ),
                xycoords=self.figure_manager.ax.get_yaxis_transform(),
                arrowprops=dict(
                    arrowstyle='|-|', 
                    color="black", 
                    lw=0.8, 
                    shrinkA=15, 
                    shrinkB=15, 
                    mutation_scale=3*stopper_scale,
                    zorder=0.7,
                )
            )
            stopper_2.set_zorder(5)

            return AxisBreak(rect, stopper_1, stopper_2)

        self.has_axes_breaks = True
        if self.style == "boxed":
            break_object_left = draw_xaxis_break(0, y)
            break_object_right = draw_xaxis_break(1, y)
            break_object = {
                "left": break_object_left,
                "right": break_object_right,
            }
        else:
            break_object = draw_xaxis_break(0, y)

        self.mpl_objects.yaxis_breaks[f"{y:.1f}"] = break_object
        
        # Save for redrawing
        self.axes_break_data["y"].append({
            "y": y,
            "gap_scale": gap_scale,
            "stopper_scale": stopper_scale,
            "angle": angle,
        })


    def reset_axis_breaks(
            self,
            margins: dict[str, tuple],
            figsize: tuple[float, float],
        ) -> None:
        self.mpl_objects.remove_axes_breaks()
        xaxis_breaks = self.axes_break_data["x"][:]
        yaxis_breaks = self.axes_break_data["y"][:]
        self.axes_break_data["x"] = []
        self.axes_break_data["y"] = []
        for x_break in xaxis_breaks:
            self.add_xaxis_break(
                margins=margins, 
                figsize=figsize,
                **x_break,
            )
        for y_break in yaxis_breaks:
            self.add_yaxis_break(
                margins=margins, 
                figsize=figsize,
                **y_break,
            )


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
    xaxis_breaks : dict of str to AxisBreak
        X-axis break artists, keyed by position as a formatted string
        (e.g. ``"2.0"``).
    yaxis_breaks : dict of str to AxisBreak
        Y-axis break artists, keyed by position as a formatted string
        (e.g. ``"5.0"``).
    """
    arrows: dict[str, Annotation]
    axes: dict[str, Line2D]
    x_labels: dict[str, Text]
    xaxis_breaks: dict[str, AxisBreak]
    yaxis_breaks: dict[str, AxisBreak]

    def remove_axes(self):
        for _, arrow in self.arrows.items():
            arrow.remove()
        for _, axis in self.axes.items():
            axis.remove()
        for _, axis_break in self.xaxis_breaks.items():
            axis_break.remove()
        for _, axis_break in self.yaxis_breaks.items():
            axis_break.remove()
        self.arrows = {}
        self.axes = {}
        self.xaxis_breaks = {}
        self.yaxis_breaks = {}

    def remove_axes_breaks(self):
        for _, axis_break in self.xaxis_breaks.items():
            axis_break.remove()
        for _, axis_break in self.yaxis_breaks.items():
            axis_break.remove()
        self.xaxis_breaks = {}
        self.yaxis_breaks = {}
    
    def remove_labels(self):
        for _, label in self.x_labels.items():
            label.remove()
        self.x_labels = {}


@dataclass
class AxisBreak:
    whitespace: Rectangle
    stopper_1: Annotation
    stopper_2: Annotation

    def remove(self):
        self.whitespace.remove()
        self.stopper_1.remove()
        self.stopper_2.remove()


    
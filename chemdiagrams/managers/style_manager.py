from __future__ import annotations

from dataclasses import dataclass

from ..validation import Validators
from .. import constants
from . import FigureManager


class StyleManager:
    """
    StyleManager class for handling the Styles

    """

    def __init__(
            self,
            figure_manager: FigureManager,
            style: str,
        ) -> None:
        self.figure_manager = figure_manager
        self.style = style
        self.mpl_objects = StyleObjects({},{})
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
        self.mpl_objects.delete()
        axes = {}
        arrows = {}
        
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
            arrows["x_arrow"] = draw_arrow((1.02, 0),(0.97, 0))
            arrows["y_arrow"] = draw_arrow((0, 1.02),(0, 0.97))
            
        elif style == "open":
            self.figure_manager.ax.spines["top"].set_visible(False)
            self.figure_manager.ax.spines["right"].set_visible(False)
            self.figure_manager.ax.spines["left"].set_visible(True)
            self.figure_manager.ax.spines["bottom"].set_visible(False)
            axes["x_axis"] = self.figure_manager.ax.axhline(0, color="black", zorder=0.5, lw=1.0)
            axes["y_arrow"] = draw_arrow((0, 1.02),(0, 0.97))

        elif style == "twosided":
            self.figure_manager.ax.spines["top"].set_visible(False)
            self.figure_manager.ax.spines["right"].set_visible(False)
            self.figure_manager.ax.spines["left"].set_visible(True)
            self.figure_manager.ax.spines["bottom"].set_visible(True)
            self.figure_manager.ax.spines["bottom"].set_position(('axes', -0.03))
            arrows["x_arrow_right"] = draw_arrow((1.01, -0.03),(0.96, -0.03))
            arrows["x_arrow_left"] = draw_arrow((-0.01, -0.03),(0.04, -0.03))
            arrows["y_arrow"] = draw_arrow((0, 1.02),(0, 0.97))

        self.mpl_objects = StyleObjects(arrows,axes)




@dataclass
class StyleObjects:
    arrows: dict
    axes: dict

    def delete(self):
        for _, arrow in self.arrows.items():
            arrow.remove()
        for _, axis in self.axes.items():
            axis.remove()


    
from __future__ import annotations
from typing import TYPE_CHECKING

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

if TYPE_CHECKING:
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from matplotlib.text import Text
    from collections.abc import Sequence

from .managers import (
    FigureManager,
    PathManager,
    NumberManager,
    StyleManager,
    LayoutManager,
    BarManager,
    PathObject,
    StyleObjects,
    DifferenceBar,
)

from . import constants


from .validation import Validators

class EnergyDiagram:
    """
    EnergyDiagram class for plotting reaction energy figures conveniently

    """

    ############################################################
    # Methods for drawing the general plot
    ############################################################

    def __init__(
            self, 
            extra_x_margin: tuple[float, float] | list[float] = (0,0), 
            extra_y_margin: tuple[float, float] | list[float] = (-0.1,0.15), 
            figsize: tuple[float, float] | list[float] | None = None, 
            fontsize: int = 8, 
            verbose: bool = False, 
            style: str = "open",
            dpi: int = 150,
        ) -> None:
        
        self._figure_manager = FigureManager(
            fontsize=fontsize, 
            dpi=dpi
        )
        self._path_manager = PathManager(
            self._figure_manager
        )
        self._number_manager = NumberManager(
            self._figure_manager
        )
        self._style_manager = StyleManager(
            self._figure_manager, 
            style=style
        )
        self._layout_manager = LayoutManager(
            self._figure_manager, 
            extra_x_margin=extra_x_margin, 
            extra_y_margin=extra_y_margin, 
            figsize=figsize
        )
        self._bar_manager = BarManager(
            self._figure_manager
        )
        self.verbose = verbose

    def set_xlabels(
            self, 
            labels: Sequence, 
            labelplaces: Sequence[float] | None = None, 
            fontsize: int | None = None, 
            weight: str = "bold", 
            in_plot: bool = False
        ) -> None:
        self._figure_manager.set_xlabels(
            labels,
            labelplaces=labelplaces,
            fontsize=fontsize,
            weight=weight,
            in_plot=in_plot,
        )

    def set_diagram_style(self, style: str) -> None:
        self._layout_manager.adjust_xy_limits(self._path_manager.path_data)  
        self._style_manager.set_diagram_style(style)
        try:
            self.set_xlabels(**self._figure_manager.labelproperties)
        except AttributeError:
            pass

    def draw_difference_bar(
            self, 
            x: float, 
            y_start_end: tuple[float, float] | list[float], 
            description: str, 
            diff: float | None = None,
            left_side: bool = False,
            fontsize: int | None = None, 
            color: str = "black", 
            arrowstyle: str = "|-|", 
            x_whiskers: Sequence[float | None] = (None, None), 
            whiskercolor: str | None = None
        ) -> None:
        margins = self._layout_manager.adjust_xy_limits(
            self._path_manager.path_data
        ) 
        self._bar_manager.draw_difference_bar(
            x, y_start_end, description, margins,
            diff=diff,
            left_side=left_side,
            fontsize=fontsize,
            color=color,
            arrowstyle=arrowstyle,
            x_whiskers=x_whiskers,
            whiskercolor=whiskercolor,
            )

    def draw_path(
            self, 
            x_data: Sequence[float], 
            y_data: Sequence[float], 
            color: str, 
            linetypes: Sequence[int] | None = None, 
            path_name: str | None = None, 
            show_numbers: bool = True
        ) -> None:
        self._path_manager.draw_path(
            x_data, y_data, color,
            linetypes=linetypes,
            path_name=path_name,
            show_numbers=show_numbers,
        )

        self._layout_manager.scale_figure(
            self._path_manager.path_data
        )
        try: 
            self.set_xlabels(**self._figure_manager.labelproperties)
        except AttributeError:
            pass


    def legend(self, 
            loc: str = "best", 
            fontsize: int | None = None
        ) -> None:
        Validators._validate_number(fontsize, "fontsize", allow_none=True, min_value=0)
        if fontsize is None:
            fontsize = self._figure_manager.fontsize
        patches = []
        for path_name, path_info in self._path_manager.path_data.items():
            if path_info["has_label"]:
                patches.append(
                    mpatches.Patch(
                        color=path_info["color"], 
                        label=path_name
                    )
                )
        self._figure_manager.ax.legend(
            handles=patches, 
            fontsize=fontsize, 
            loc=loc
        )

    def show(self) -> None:
        figsize = self._layout_manager.scale_figure(
            self._path_manager.path_data
        ) 
        if self.verbose == True:
            print(f"Figure size is {round(figsize[0],2)} x {round(figsize[1],2)} inches.")
        plt.show()

    ############################################################
    # Methods for plotting numbers
    ############################################################

    def add_numbers_naive(
            self,
            x_min_max: tuple[float, float] | list[float] | float | None = None,
        ) -> None:
        margins = self._layout_manager.adjust_xy_limits(
            self._path_manager.path_data
        )
        self._number_manager.add_numbers_naive(
            self._path_manager.path_data, margins, x_min_max
        )

    def add_numbers_stacked(
        self,
        x_min_max: tuple[float, float] | list[float] | float | None = None, 
        sort_by_energy: bool = True, 
        no_overlap_with_nonnumbered: bool = True
        ) -> None:
        margins = self._layout_manager.adjust_xy_limits(
            self._path_manager.path_data
        )
        self._number_manager.add_numbers_stacked(
            self._path_manager.path_data, 
            margins, 
            x_min_max,
            sort_by_energy=sort_by_energy,
            no_overlap_with_nonnumbered=no_overlap_with_nonnumbered
        )

    def add_numbers_auto(
            self, 
            x_min_max: tuple[float, float] | list[float] | float | None = None,
        ) -> None:
        margins = self._layout_manager.adjust_xy_limits(
            self._path_manager.path_data
        )
        self._number_manager.add_numbers_auto(
            self._path_manager.path_data,
            margins,
            x_min_max = x_min_max,
        )

    def add_numbers_average(
            self, 
            x_min_max: tuple[float, float] | list[float] | float | None = None,
            color: str = "black"
        ) -> None:
        margins = self._layout_manager.adjust_xy_limits(
            self._path_manager.path_data
        )
        self._number_manager.add_numbers_average(
            self._path_manager.path_data,
            margins, 
            x_min_max = x_min_max,
            color = color
        )
        

    ############################################################
    # Getters
    ############################################################

    @property
    def ax(self) -> Axes:
        return self._figure_manager.ax
    
    @property
    def fig(self) -> Figure:
        return self._figure_manager.fig
    
    @property
    def lines(self) -> dict[str, PathObject]:
        return self._path_manager.mpl_objects
    
    @property
    def ax_objects(self) -> StyleObjects:
        return self._style_manager.mpl_objects
    
    @property
    def bars(self) -> list[DifferenceBar]:
        return self._bar_manager.mpl_objects
    
    @property
    def numbers(self) -> dict[str, dict[str, Text]]:
        return self._number_manager.mpl_objects
    
    
from __future__ import annotations

from typing import TYPE_CHECKING

import numpy as np

from ..constants import Constants

if TYPE_CHECKING:
    from matplotlib.text import Text

    from .figure_manager import FigureManager


class CollisionManager:
    """
    Container for methods related to calculating difference values
    for object collision avoidance.
    """

    def __init__(
        self,
        figure_manager: FigureManager,
        constants: Constants,
    ) -> None:
        self.figure_manager = figure_manager
        self.constants = constants

    def _get_diff_img_plateau(
        self,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
    ) -> float:
        """Compute vertical spacing value for image plateau distance in data coordinates."""
        diff_to_plateau = (
            (margins["y"][1] - margins["y"][0])
            / figsize[1]
            * self.constants.DISTANCE_IMAGE_LINE
        )
        return diff_to_plateau

    def _get_diff_img_number(
        self,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
        fontsize: int,
    ) -> float:
        """Compute vertical spacing value for image number distance in data coordinates."""
        diff_to_number = (
            (fontsize / self.constants.STD_FONTSIZE)
            * (margins["y"][1] - margins["y"][0])
            / figsize[1]
            * self.constants.DISTANCE_NUMBER_LINE
        )
        return diff_to_number

    def _get_diff_to_label(
        self,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
    ) -> float:
        """Compute vertical spacing needed for label placement in data coordinates."""
        diff_to_label = (
            (margins["y"][1] - margins["y"][0])
            / figsize[1]
            * (self.constants.DISTANCE_TO_LABEL)
        )
        return diff_to_label

    def _get_label_boundaries(
        self,
        label: Text,
    ) -> tuple[float, float]:
        """
        Get vertical maximum and minimum y boundaries of a label in data coordinates.

        Returns
        -------
        tuple
            A tuple of (y_min, y_max) for the label in data coordinates.
        """
        label_window = label.get_window_extent().transformed(
            self.figure_manager.ax.transData.inverted()
        )
        y_min = label_window.ymin
        y_max = label_window.ymax
        return (y_min, y_max)

    def _get_number_diffs(
        self,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
        fontsize: int,
    ) -> tuple[float, float]:
        """
        Compute vertical spacing values for label placement in data coordinates.

        Both values scale proportionally with font size, y-axis range, and
        figure height so that spacing remains visually consistent regardless
        of the diagram's scale.

        Returns
        -------
        diff_bias : float
            The vertical gap between an energy bar and the first label.
        diff_per_step : float
            The vertical distance between consecutive stacked labels.
        """
        diff_bias = (
            (fontsize / self.constants.STD_FONTSIZE)
            * (margins["y"][1] - margins["y"][0])
            / figsize[1]
            * self.constants.DISTANCE_NUMBER_LINE
        )
        diff_per_step = (
            (fontsize / self.constants.STD_FONTSIZE)
            * (margins["y"][1] - margins["y"][0])
            / figsize[1]
            * self.constants.DISTANCE_NUMBER_NUMBER
        )
        return diff_bias, diff_per_step

    def _get_axis_break_stopper_differences(
        self,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
        angle: float,
    ) -> tuple[float, float]:
        """
        Compute data coordinate differences for axis break stoppers in x and y directions.
        """
        delta_x = (
            np.cos(angle * np.pi / 180)
            * 0.001
            * (margins["x"][1] - margins["x"][0])
            / figsize[0]
        )
        delta_y = (
            np.sin(angle * np.pi / 180)
            * 0.001
            * (margins["y"][1] - margins["y"][0])
            / figsize[1]
        )
        return delta_x, delta_y

    def _get_axis_break_whitespace_cover_width(
        self,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
    ) -> float:
        """Compute data coordinate width for axis break whitespace cover."""
        cover_width = (
            self.constants.MERGED_PLATEAU_COVER_WIDTH
            * (margins["y"][1] - margins["y"][0])
            / figsize[1]
        )
        return cover_width

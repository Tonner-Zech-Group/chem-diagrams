from __future__ import annotations

from re import findall

import numpy as np

from ..constants import Constants


class DifferenceManager:
    """
    Container for methods related to calculating difference values
    for object collision avoidance and label placement. This manager does not store
    any state or rendered artists, but is kept separate for organizational
    purposes and to avoid circular imports.
    """

    @staticmethod
    def _get_diff_img_plateau(
        constants: Constants,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
    ) -> float:
        """Compute vertical spacing value for image plateau distance in data coordinates."""
        diff_to_plateau = (
            (margins["y"][1] - margins["y"][0]) / figsize[1] * constants.DISTANCE_IMAGE_LINE
        )
        return diff_to_plateau

    @staticmethod
    def _get_diff_img_number(
        constants: Constants,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
        fontsize: int,
    ) -> float:
        """Compute vertical spacing value for image number distance in data coordinates."""
        diff_to_number = (
            (fontsize / constants.STD_FONTSIZE)
            * (margins["y"][1] - margins["y"][0])
            / figsize[1]
            * constants.DISTANCE_NUMBER_LINE
        )
        return diff_to_number

    @staticmethod
    def _get_diff_img_label(
        constants: Constants,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
        fontsize: int,
        labeltext: str,
    ) -> float:
        """Compute vertical spacing value for image label distance in data coordinates."""
        n_linebreaks = len(findall("\n", labeltext))
        diff_to_label = (
            (fontsize / constants.STD_FONTSIZE)
            * (margins["y"][1] - margins["y"][0])
            / figsize[1]
            * (
                constants.DISTANCE_IMAGE_LABEL
                + n_linebreaks * constants.DISTANCE_LABEL_NEWLINE
            )
        )
        return diff_to_label

    @staticmethod
    def _get_diff_plateau_label(
        constants: Constants,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
        fontsize: int,
        labeltext: str,
    ) -> float:
        """Compute vertical spacing value for plateau label distance in data coordinates."""
        n_linebreaks = len(findall("\n", labeltext))
        diff_to_label = (
            (fontsize / constants.STD_FONTSIZE)
            * (margins["y"][1] - margins["y"][0])
            / figsize[1]
            * (constants.DISTANCE_LABEL_LINE + n_linebreaks * constants.DISTANCE_LABEL_NEWLINE)
        )
        return diff_to_label

    @staticmethod
    def _get_number_diffs(
        constants: Constants,
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
            (fontsize / constants.STD_FONTSIZE)
            * (margins["y"][1] - margins["y"][0])
            / figsize[1]
            * constants.DISTANCE_NUMBER_LINE
        )
        diff_per_step = (
            (fontsize / constants.STD_FONTSIZE)
            * (margins["y"][1] - margins["y"][0])
            / figsize[1]
            * constants.DISTANCE_NUMBER_NUMBER
        )
        return diff_bias, diff_per_step

    @staticmethod
    def _get_axis_break_stopper_differences(
        constants: Constants,
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

    @staticmethod
    def _get_axis_break_whitespace_cover_width(
        constants: Constants,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
    ) -> float:
        """Compute data coordinate width for axis break whitespace cover."""
        cover_width = (
            constants.MERGED_PLATEAU_COVER_WIDTH
            * (margins["y"][1] - margins["y"][0])
            / figsize[1]
        )
        return cover_width

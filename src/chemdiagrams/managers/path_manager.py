from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import TYPE_CHECKING

import matplotlib.patches as mpatches
import numpy as np
from matplotlib import font_manager
from scipy.interpolate import CubicSpline

if TYPE_CHECKING:
    from matplotlib.collections import LineCollection
    from matplotlib.lines import Line2D
    from matplotlib.patches import Rectangle
    from matplotlib.text import Annotation

from .. import constants
from ..validation import Validators
from .difference_manager import DifferenceManager
from .figure_manager import FigureManager
from .style_manager import StyleManager


class PathManager:
    """
    Manages the creation and storage of reaction path artists.

    Draws horizontal energy levels (plateaus) and the connectors
    between them, storing all rendered artists in ``mpl_objects`` and
    the underlying data in ``path_data`` for use by other managers.
    """

    def __init__(
        self,
        figure_manager: FigureManager,
    ) -> None:
        self.figure_manager = figure_manager
        self.path_data: dict[str, dict] = {}
        self.path_label_data: list[dict] = []
        self.mpl_objects: dict[str, PathObject] = {}
        self.merged_plateau_objects: list[dict] = []

    def draw_path(
        self,
        x_data: Sequence[float],
        y_data: Sequence[float],
        color: str,
        linetypes: Sequence[int] | int | None = None,
        path_name: str | None = None,
        show_numbers: bool = True,
        width_plateau: float | None = None,
        lw_plateau: float | str = "plateau",
    ) -> None:
        # Sanity checks and linetype normalization
        Validators.validate_numeric_sequence(x_data, "x_data")
        Validators.validate_numeric_sequence(y_data, "y_data")
        if not isinstance(path_name, (str, type(None))):
            raise TypeError("path_name must be a string or None")
        if path_name in list(self.path_data.keys()):
            raise ValueError("path_name must not already exist")
        if len(x_data) != len(y_data):
            raise ValueError("x_data and y_data must have the same length")
        if width_plateau is not None:
            Validators.validate_number(width_plateau, "width_plateau", min_value=0)
        else:
            width_plateau = constants.WIDTH_PLATEAU

        ALLOWED_LINETYPES = [-2, -1, 0, 1, 2, 3, 4]
        if linetypes is None:
            linetypes = [1] * (len(y_data) - 1)
        elif isinstance(linetypes, int):
            if linetypes not in ALLOWED_LINETYPES:
                raise ValueError(f"linetype must be in {ALLOWED_LINETYPES}.")
            linetypes = [linetypes] * (len(y_data) - 1)
        elif isinstance(linetypes, Sequence):
            if not all(val in ALLOWED_LINETYPES for val in linetypes):
                raise ValueError(f"linetype elements must be in {ALLOWED_LINETYPES}.")
            if len(linetypes) != len(x_data) - 1 or len(linetypes) != len(y_data) - 1:
                raise ValueError(
                    f"Length of linetypes + 1 (now {len(linetypes)} + 1) "
                    f"must equal the number of data points (right now {len(x_data)})."
                )
        else:
            raise TypeError("linetypes must be an tuple, list or integer.")

        if isinstance(lw_plateau, str):
            if lw_plateau == "plateau":
                lw_plateau = constants.LW_PLATEAU
            elif lw_plateau == "connector":
                lw_plateau = constants.LW_CONNECTOR
            else:
                raise ValueError(
                    "Invalid string value for lw_plateau. "
                    "Use 'plateau', 'connector', or a number."
                )
        else:
            Validators.validate_number(lw_plateau, "lw_plateau", min_value=0)
        assert isinstance(lw_plateau, (float, int))

        # Save data for numbering or legend
        has_name = True
        if path_name is None:
            has_name = False
            path_name = f"__NONAME{len(self.path_data)}"
        self.path_data[path_name] = {
            "x": x_data,
            "y": y_data,
            "color": color,
            "has_name": has_name,
            "show_numbers": show_numbers,
        }

        # Initialize nested dics
        connections: dict = {}
        plateaus: dict = {}
        labels: dict = {}

        # Create lists in order to draw the lines
        x_corners = []
        y_corners = []

        # Draw the lines
        for i, v in enumerate(y_data):
            x_corners.append(x_data[i] - 0.5 * width_plateau)
            x_corners.append(x_data[i] + 0.5 * width_plateau)
            y_corners.append(y_data[i])
            y_corners.append(y_data[i])
            if width_plateau > 0:
                plateau = self.figure_manager.ax.hlines(
                    v,
                    x_corners[-2],
                    x_corners[-1],
                    zorder=constants.ZORDER_PLATEAU,
                    lw=lw_plateau,
                    color=color,
                    capstyle="round",
                )
            else:
                plateau = None
            plateaus[f"{x_data[i]:.1f}"] = plateau
            if i > 0:
                connector = self._draw_connector(
                    x_corners[-3:-1], y_corners[-3:-1], linetypes[i - 1], color
                )
                connections[f"{sum(x_corners[-3:-1]) / 2:.1f}"] = connector
        # Save Path
        self.mpl_objects[path_name] = PathObject(connections, plateaus, labels)

    def add_path_labels(
        self,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
        path_name: str,
        labels: Sequence[str],
        fontsize: int | None = None,
        weight: str = "normal",
        color: str | None = None,
    ) -> None:
        # Sanity checks
        if path_name not in self.path_data.keys():
            raise ValueError(f'Path "{path_name}" does not exist.')
        Validators.validate_string_sequence(
            labels,
            "labels",
            can_contain_none=True,
            required_length=len(self.path_data[path_name]["x"]),
        )
        if fontsize is not None:
            Validators.validate_number(fontsize, "fontsize", min_value=0, allow_none=True)
        else:
            fontsize = self.figure_manager.fontsize
        if color is None:
            color = self.path_data[path_name]["color"]

        labelfont = font_manager.FontProperties(weight=weight, size=fontsize)

        for i, labeltext in enumerate(labels):
            if labeltext is not None:
                x = self.path_data[path_name]["x"][i]
                y = self.path_data[path_name]["y"][i]
                label_artist = StyleManager._add_label_in_plot(
                    figure_manager=self.figure_manager,
                    margins=margins,
                    figsize=figsize,
                    labeltext=labeltext,
                    fontsize=fontsize,
                    labelfont=labelfont,
                    x=x,
                    y=y,
                    color=color,
                )
                self.mpl_objects[path_name].labels[f"{x:.1f}"] = label_artist

        self.path_label_data.append(
            {
                "path_name": path_name,
                "labels": labels,
                "fontsize": fontsize,
                "weight": weight,
                "color": color,
            }
        )

    def _recalculate_path_labels(
        self,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
    ) -> None:
        old_path_label_data = self.path_label_data.copy()
        self.path_label_data = []
        for label_data in old_path_label_data:
            # Remove old labels
            self.mpl_objects[label_data["path_name"]].remove_labels()

            # Add new labels with updated positions
            self.add_path_labels(
                margins=margins,
                figsize=figsize,
                **label_data,
            )

    def merge_plateaus(
        self,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
        x: int,
        path_name_left: str,
        path_name_right: str,
        gap_scale: float = 1,
        stopper_scale: float = 1,
        angle: float = 30,
    ) -> None:
        # Sanity checks
        Validators.validate_number(x, "x")
        Validators.validate_number(gap_scale, "gap_scale", min_value=0)
        Validators.validate_number(stopper_scale, "stopper_scale", min_value=0)
        Validators.validate_number(angle, "angle")
        try:
            full_plateau_left = self.mpl_objects[path_name_left].plateaus[f"{x:.1f}"]
        except KeyError:
            raise ValueError(
                f'Path "{path_name_left}" must exist and have a value at x = {x}.'
            )
        try:
            full_plateau_right = self.mpl_objects[path_name_right].plateaus[f"{x:.1f}"]
        except KeyError:
            raise ValueError(
                f'Path "{path_name_right}" must exist and have a value at x = {x}.'
            )
        if full_plateau_left is None:
            raise ValueError(f"Plateau for {path_name_left} at x = {x} is non-existent.")
        if full_plateau_right is None:
            raise ValueError(f"Plateau for {path_name_right} at x = {x} is non-existent.")
        y_left = full_plateau_left.get_segments()[0][0][1]
        y_right = full_plateau_right.get_segments()[0][0][1]
        if y_left != y_right:
            raise ValueError(
                f"{path_name_left} and {path_name_right} must have the same y at x = {x}."
            )
        y = y_left

        # Get color information
        color_left = full_plateau_left.get_color()
        color_right = full_plateau_right.get_color()
        full_plateau_left.remove()
        full_plateau_right.remove()

        # Print plateaus
        gap = constants.MERGED_PLATEAU_GAP * gap_scale
        plateau_left = self.figure_manager.ax.hlines(
            y,
            x - constants.WIDTH_PLATEAU / 2,
            x - gap / 2,
            zorder=constants.ZORDER_PLATEAU,
            lw=constants.LW_PLATEAU,
            color=color_left,
            capstyle="round",
        )
        plateau_right = self.figure_manager.ax.hlines(
            y,
            x + constants.WIDTH_PLATEAU / 2,
            x + gap / 2,
            zorder=constants.ZORDER_PLATEAU,
            lw=constants.LW_PLATEAU,
            color=color_right,
            capstyle="round",
        )

        # Draw white rectangle to
        cover_width = DifferenceManager._get_axis_break_whitespace_cover_width(
            margins, figsize
        )

        # Add white covering reactange
        # x in data coords, y in axis fractions
        whitespace = mpatches.Rectangle(
            (x - gap / 2, y - cover_width / 2),
            gap,
            cover_width,
            facecolor="white",
            edgecolor="white",
            zorder=constants.ZORDER_MERGED_PLATEAU_COVER,
        )

        # Calculate stopper direction in data coordinates
        delta_x, delta_y = DifferenceManager._get_axis_break_stopper_differences(
            margins,
            figsize,
            angle,
        )

        stopper_left = self.figure_manager.ax.annotate(
            "",
            xy=(x - gap / 2, y),
            xytext=(x - gap / 2 + delta_x, y + delta_y),
            arrowprops=dict(
                arrowstyle="|-|",
                color=color_left,
                lw=constants.LW_MERGED_PLATEAU_STOPPER,
                shrinkA=15,
                shrinkB=15,
                mutation_scale=constants.SIZE_MERGED_PLATEAU_STOPPER * stopper_scale,
                zorder=constants.ZORDER_MERGED_PLATEAU_STOPPER,
            ),
        )
        stopper_right = self.figure_manager.ax.annotate(
            "",
            xy=(x + gap / 2, y),
            xytext=(x + gap / 2 - delta_x, y - delta_y),
            arrowprops=dict(
                arrowstyle="|-|",
                color=color_right,
                lw=constants.LW_MERGED_PLATEAU_STOPPER,
                shrinkA=15,
                shrinkB=15,
                mutation_scale=constants.SIZE_MERGED_PLATEAU_STOPPER * stopper_scale,
                zorder=constants.ZORDER_MERGED_PLATEAU_STOPPER,
            ),
        )

        # Save mpl objects get a pointer for angle correction
        merged_plateau = MergedPlateau(
            plateau_left,
            plateau_right,
            stopper_left,
            stopper_right,
            whitespace,
        )
        self.mpl_objects[path_name_left].plateaus[f"{x:.1f}"] = merged_plateau
        self.mpl_objects[path_name_right].plateaus[f"{x:.1f}"] = merged_plateau

        self.merged_plateau_objects.append(
            {
                "object": merged_plateau,
                "angle": angle,
            }
        )

    def _recalculate_merged_plateaus(
        self,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
    ) -> None:
        for merged_plateau_dict in self.merged_plateau_objects:
            merged_plateau_object = merged_plateau_dict["object"]
            angle = merged_plateau_dict["angle"]
            merged_plateau_object.recalculate_gap(margins, figsize, angle)

    def _draw_connector(
        self,
        x_coords: Sequence[float],
        y_coords: Sequence[float],
        linetype: int,
        color: str,
    ) -> Line2D | list[Line2D] | BrokenLine | None:
        connector: Line2D | list[Line2D] | BrokenLine | None = None
        if linetype == 0:
            connector = None
        elif linetype == 1:
            connector = self._draw_dotted_line(x_coords, y_coords, color)
        elif linetype == -1:
            connector = self._draw_broken_line(x_coords, y_coords, color, dotted=True)
        elif linetype == 2:
            connector = self._draw_line(x_coords, y_coords, color)
        elif linetype == -2:
            connector = self._draw_broken_line(x_coords, y_coords, color, dotted=False)
        elif linetype == 3:
            connector = self._draw_dotted_spline(x_coords, y_coords, color)
        elif linetype == 4:
            connector = self._draw_spline(x_coords, y_coords, color)
        else:
            raise ValueError(f"Invalid linetype argument: {linetype}")
        return connector

    def _draw_dotted_line(
        self, x_coords: Sequence[float], y_coords: Sequence[float], color: str
    ) -> Line2D:
        return self.figure_manager.ax.plot(
            x_coords,
            y_coords,
            zorder=constants.ZORDER_CONNECTOR,
            ls=":",
            lw=constants.LW_CONNECTOR,
            color=color,
        )[0]

    def _draw_line(
        self, x_coords: Sequence[float], y_coords: Sequence[float], color: str
    ) -> Line2D:
        return self.figure_manager.ax.plot(
            x_coords,
            y_coords,
            zorder=constants.ZORDER_CONNECTOR,
            ls="-",
            lw=constants.LW_CONNECTOR,
            color=color,
        )[0]

    def _draw_broken_line(
        self,
        x_coords: Sequence[float],
        y_coords: Sequence[float],
        color: str,
        dotted: bool = True,
    ) -> BrokenLine:
        # Portion of the line that has a gap
        linegap = constants.BROKEN_LINE_GAP
        # Ensure tuples are converted to list
        x_coords = list(x_coords)
        y_coords = list(y_coords)

        # Draw first part of line
        x1 = x_coords.copy()
        y1 = y_coords.copy()
        x1[1] = x1[0] + (x1[1] - x1[0]) * (0.5 - linegap / 2)
        y1[1] = y1[0] + (y1[1] - y1[0]) * (0.5 - linegap / 2)
        if dotted:
            line_1 = self._draw_dotted_line(x1, y1, color=color)
        else:
            line_1 = self._draw_line(x1, y1, color=color)

        # Draw second part of line
        x2 = x_coords.copy()
        y2 = y_coords.copy()
        x2[0] = x2[0] + (x2[1] - x2[0]) * (0.5 + linegap / 2)
        y2[0] = y2[0] + (y2[1] - y2[0]) * (0.5 + linegap / 2)
        if dotted:
            line_2 = self._draw_dotted_line(x2, y2, color=color)
        else:
            line_2 = self._draw_line(x2, y2, color=color)

        # Draw small orthogonal lines
        stopper_1 = self.figure_manager.ax.annotate(
            "",
            xy=(x1[1], y1[1]),
            xytext=(x1[1] + 0.001 * (x2[0] - x1[1]), y1[1] + 0.001 * (y2[0] - y1[1])),
            arrowprops=dict(
                arrowstyle="|-|",
                color=color,
                lw=constants.LW_BROKEN_LINE_STOPPER,
                shrinkA=15,
                shrinkB=15,
                mutation_scale=constants.SIZE_BROKEN_LINE_STOPPER,
                zorder=constants.ZORDER_BROKEN_LINE_STOPPER,
            ),
        )
        stopper_2 = self.figure_manager.ax.annotate(
            "",
            xy=(x2[0], y2[0]),
            xytext=(x2[0] - 0.001 * (x2[0] - x1[1]), y2[0] - 0.001 * (y2[0] - y1[1])),
            arrowprops=dict(
                arrowstyle="|-|",
                color=color,
                lw=constants.LW_BROKEN_LINE_STOPPER,
                shrinkA=15,
                shrinkB=15,
                mutation_scale=constants.SIZE_BROKEN_LINE_STOPPER,
                zorder=constants.ZORDER_BROKEN_LINE_STOPPER,
            ),
        )
        return BrokenLine(line_1, line_2, stopper_1, stopper_2)

    def _draw_dotted_spline(
        self, x_coords: Sequence[float], y_coords: Sequence[float], color: str
    ) -> list[Line2D]:
        # Create a cubic spline interpolation of the points
        cs = CubicSpline(x_coords, y_coords, bc_type="clamped")
        x_spline = np.linspace(x_coords[0], x_coords[-1], 100)
        y_spline = cs(x_spline)

        # Draw the spline as a dotted line
        return self.figure_manager.ax.plot(
            x_spline,
            y_spline,
            zorder=constants.ZORDER_CONNECTOR,
            ls=":",
            lw=constants.LW_CONNECTOR,
            color=color,
        )

    def _draw_spline(
        self, x_coords: Sequence[float], y_coords: Sequence[float], color: str
    ) -> list[Line2D]:
        # Create a cubic spline interpolation of the points
        cs = CubicSpline(x_coords, y_coords, bc_type="clamped")
        x_spline = np.linspace(x_coords[0], x_coords[-1], 100)
        y_spline = cs(x_spline)

        # Draw the spline as a solid line
        return self.figure_manager.ax.plot(
            x_spline,
            y_spline,
            zorder=constants.ZORDER_CONNECTOR,
            ls="-",
            lw=constants.LW_CONNECTOR,
            color=color,
        )

    @staticmethod
    def _get_stopper_differences(
        margins: dict[str, tuple],
        figsize: tuple[float, float],
        angle: float,
    ) -> tuple[float, float]:
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
    def _get_whitespace_cover_width(
        margins: dict[str, tuple],
        figsize: tuple[float, float],
    ) -> float:
        cover_width = (
            constants.MERGED_PLATEAU_COVER_WIDTH
            * (margins["y"][1] - margins["y"][0])
            / figsize[1]
        )
        return cover_width


@dataclass
class PathObject:
    """
    Container for the Matplotlib artists that make up a single reaction path.

    Attributes
    ----------
    connections : dict of str to Line2D, BrokenLine, or None
        Connector artists between energy levels, keyed by the midpoint
        x-coordinate of each segment as a formatted string (e.g. ``"1.5"``).
    plateaus : dict of str to LineCollection
        Horizontal energy bar artists, keyed by their x-coordinate
        as a formatted string (e.g. ``"1.0"``).
    """

    connections: dict
    plateaus: dict
    labels: dict

    def remove(self):
        for _, connection in self.connections.items():
            connection.remove()
        for _, plateau in self.plateaus.items():
            try:
                plateau.remove()
            except AttributeError:
                pass
        for _, label in self.labels.items():
            label.remove()

    def remove_labels(self):
        for _, label in self.labels.items():
            label.remove()
        self.labels = {}


@dataclass
class BrokenLine:
    """
    Container for the four artists that make up a broken connector line.

    A broken line is drawn as two half-segments with small orthogonal
    tick marks at the break point, indicating a discontinuity in the
    reaction coordinate.

    Attributes
    ----------
    line_part_1 : Line2D
        The first half of the connector, from the start to the break.
    line_part_2 : Line2D
        The second half of the connector, from the break to the end.
    stopper_1 : Annotation
        Orthogonal tick mark at the end of ``line_part_1``.
    stopper_2 : Annotation
        Orthogonal tick mark at the start of ``line_part_2``.
    """

    line_part_1: Line2D
    line_part_2: Line2D
    stopper_1: Annotation
    stopper_2: Annotation

    def remove(self):
        self.line_part_1.remove()
        self.line_part_2.remove()
        self.stopper_1.remove()
        self.stopper_2.remove()


@dataclass
class MergedPlateau:
    plateau_left: LineCollection
    plateau_right: LineCollection
    stopper_left: Annotation
    stopper_right: Annotation
    whitespace: Rectangle
    """
    Container for the Matplotlib artists that make up a merged plateau pair.

    Holds the two shortened half-plateau lines, the diagonal stopper tick
    marks drawn in the gap between them, and the white rectangle that
    covers the original overlapping plateau segments.

    Attributes
    ----------
    plateau_left : LineCollection
        The left half-plateau artist, ending at the left edge of the gap.
    plateau_right : LineCollection
        The right half-plateau artist, starting at the right edge of the gap.
    stopper_left : Annotation
        Diagonal tick mark at the right end of ``plateau_left``.
    stopper_right : Annotation
        Diagonal tick mark at the left end of ``plateau_right``.
    whitespace : Rectangle
        White rectangle covering the gap between the two half-plateaus,
        used to hide any underlying plateau or connector artifacts.
    """

    def remove(self):
        self.plateau_left.remove()
        self.plateau_right.remove()
        self.stopper_left.remove()
        self.stopper_right.remove()
        self.whitespace.remove()

    def recalculate_gap(
        self,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
        angle: float,
    ) -> None:
        """Recompute stopper positions and whitespace height after a layout change.

        Called whenever the figure size or axis margins are updated (e.g. after
        a new path is added) to keep the stopper tick marks and covering rectangle
        correctly sized in display coordinates.

        Parameters
        ----------
        margins : dict of str to tuple
            Current axis margin data as returned by ``LayoutManager.adjust_xy_limits``.
        figsize : tuple of float
            Current figure size in inches as ``(width, height)``.
        angle : float
            Angle of the stopper tick marks in degrees from the vertical,
            as originally passed to ``merge_plateaus``.
        """
        delta_x, delta_y = DifferenceManager._get_axis_break_stopper_differences(
            margins,
            figsize,
            angle,
        )
        x_left, y_left = self.stopper_left.xy
        x_right, y_right = self.stopper_right.xy
        self.stopper_left.set_position((x_left + delta_x, y_left + delta_y))
        self.stopper_right.set_position((x_right - delta_x, y_right - delta_y))
        cover_width = DifferenceManager._get_axis_break_whitespace_cover_width(
            margins, figsize
        )
        self.whitespace.set_height(cover_width)
        y_whitespace = self.whitespace.get_y()
        self.whitespace.set_y(y_whitespace - cover_width / 2)

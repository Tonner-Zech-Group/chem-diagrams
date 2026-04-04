from __future__ import annotations

from typing import TYPE_CHECKING

import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

if TYPE_CHECKING:
    from collections.abc import Sequence

    from matplotlib.axes import Axes
    from matplotlib.figure import Figure
    from matplotlib.text import Text

from . import constants
from .managers import (
    BarManager,
    DifferenceBar,
    FigureManager,
    ImageManager,
    LayoutManager,
    NumberManager,
    PathManager,
    PathObject,
    StyleManager,
    StyleObjects,
)
from .validation import Validators


class EnergyDiagram:
    """
    Create and manage chemical reaction energy diagrams.

    This class provides a high-level interface for constructing
    reaction energy profiles, including reaction paths, images,
    energy difference bars, labels, legends, and numerical
    annotations. Layout, scaling, and styling are handled
    automatically based on the plotted data.

    Parameters
    ----------
    extra_x_margin : tuple of float or list of float, optional
        Additional horizontal margins in data coordinate units
        added to the plot limits as (left, right).
        Default is (0, 0).
    extra_y_margin : tuple of float or list of float, optional
        Additional vertical margins in relative units added to
        the plot limits as (bottom, top). Default is (0, 0).
    width_limit : float or None, optional
        Maximum figure width in inches. When None, the width scales
        freely with the number of reaction states. Default is None.
    figsize : tuple of float or list of float or None, optional
        Explicit figure size in inches as (width, height).
        If None, the size is determined automatically.
    fontsize : int, optional
        Base font size used throughout the diagram.
    verbose : bool, optional
        If True, prints additional information.
    style : str, optional
        Diagram style preset.
    dpi : int, optional
        Figure resolution in dots per inch. Default is 150.

    Attributes
    ----------
    ax : matplotlib.axes.Axes
        The underlying Matplotlib axes object.
    fig : matplotlib.figure.Figure
        The underlying Matplotlib figure object.
    lines : dict of str to PathObject
        Dictionary of reaction paths mapped to their corresponding
        Matplotlib line objects.
    ax_objects : StyleObjects
        Container of Matplotlib objects related to styling.
    bars : list of DifferenceBar
        List of energy difference bar objects in the diagram.
    numbers : dict
        Dictionary containing energy annotation text objects.
    images : dict
        Dictionary containing image artists, keyed by image or series name.

    Methods
    -------
    draw_path(x_data, y_data, color, linetypes=None, ...)
        Add a reaction path to the diagram.

    add_path_labels(path_name, labels, ...)
        Add text labels below the energy levels of a specific path.    

    merge_plateaus(x, path_name_left, path_name_right, ...)
        Visually merge two coincident plateaus at a shared x-position.

    draw_difference_bar(x, y_start_end, description, ...)
        Draw an energy difference bar between two energy levels.

    set_xlabels(labels, labelplaces=None, fontsize=None, ...)
        Set x-axis labels for reaction states.

    set_diagram_style(style)
        Change the visual style of the diagram.

    add_xaxis_break(x, gap_scale=1, stopper_scale=1, angle=30)
        Add a break marker on the x-axis at a given position.

    add_yaxis_break(y, gap_scale=1, stopper_scale=1, angle=30)
        Add a break marker on the y-axis at a given position.

    legend(loc='best', fontsize=None)
        Add a legend for labeled reaction paths.

    add_numbers_naive(...)
        Add energy value annotations directly above states.

    add_numbers_stacked(...)
        Add stacked energy annotations to avoid overlap.

    add_numbers_auto(...)
        Automatically distribute energy annotations.

    add_numbers_average(...)
        Add averaged energy annotations.

    add_image_in_plot(img_path, position, ...)
        Place a single image at an explicit position within the diagram.

    add_image_series_in_plot(img_paths, img_x_places=None, ...)
        Place a series of images along the diagram, one per x-position.

    show()
        Display the figure.

    Notes
    -----
    The class coordinates layout, styling, path management,
    numbering, and annotation through dedicated internal
    manager components.
    """

    ############################################################
    # Methods for drawing the general plot
    ############################################################

    def __init__(
        self,
        extra_x_margin: tuple[float, float] | list[float] = (0, 0),
        extra_y_margin: tuple[float, float] | list[float] = (0, 0),
        width_limit: float | None = None,
        figsize: tuple[float, float] | list[float] | None = None,
        fontsize: int = constants.STD_FONTSIZE,
        verbose: bool = False,
        style: str = "open",
        dpi: int = 150,
    ):
        self._figure_manager = FigureManager(fontsize=fontsize, dpi=dpi)
        self._path_manager = PathManager(self._figure_manager)
        self._number_manager = NumberManager(self._figure_manager)
        self._style_manager = StyleManager(self._figure_manager, style=style)
        self._layout_manager = LayoutManager(
            self._figure_manager,
            extra_x_margin=extra_x_margin,
            extra_y_margin=extra_y_margin,
            width_limit=width_limit,
            figsize=figsize,
        )
        self._bar_manager = BarManager(self._figure_manager)
        self._image_manager = ImageManager(self._figure_manager)
        self.verbose = verbose
        self.margins = self._layout_manager.adjust_xy_limits(self._path_manager.path_data)
        self.figsize = self._layout_manager.scale_figure(self._path_manager.path_data)
        self.set_xlabels([])

    def draw_difference_bar(
        self,
        x: float,
        y_start_end: tuple[float, float] | list[float],
        description: str,
        diff: float | None = None,
        left_side: bool = False,
        add_difference: bool = True,
        n_decimals: int = 0,
        fontsize: int | None = None,
        color: str = "black",
        arrowstyle: str = "|-|",
        x_whiskers: Sequence[float | None] = (None, None),
        whiskercolor: str | None = None,
    ) -> EnergyDiagram:
        """Draw a vertical energy difference bar between two energy levels.

        Renders a double-headed arrow that spans from one energy level
        to another at a given x-position, with a text label showing
        the energy difference - the latter being calculated automatically.
        Optional horizontal whiskers can be drawn from the energy
        levels to the bar.

        Parameters
        ----------
        x : float
            The x-coordinate at which to draw the bar.
        y_start_end : tuple of float or list of float
            A two-element sequence ``(y_start, y_end)`` specifying the
            bottom and top energy values spanned by the bar.
        description : str
            Text label placed beside the bar, typically the energy
            difference symbol (e.g. ``"ΔE: "``).
        diff : float or None, optional
            Horizontal offset in data coordinates between the bar and
            its text label. When None the offset is computed
            automatically based on the figure width. Default is None.
        left_side : bool, optional
            If True the bar and label are placed to the left of ``x``
            instead of to the right. Default is False.
        add_difference: bool, optional
            If True, the difference between y_start and y_end
            gets automatically added to the description. Default
            is True.
        n_decimals : int, optional
            Number of decimal places to show for the energy difference.
            Default is 0.
        fontsize : int or None, optional
            Font size for the description label. When None the
            diagram's base font size is used. Default is None.
        color : str, optional
            Color of the difference bar. Default is ``"black"``.
        arrowstyle : str, optional
            Matplotlib arrow style string for the double-headed arrow.
            Default is ``"|-|"``.
        x_whiskers : tuple or list of float or None, optional
            A two-element sequence ``(x_bottom, x_top)`` giving the
            starting x-coordinates for optional horizontal whisker
            lines drawn from the bottom and top energy levels to the
            bar. Use None for either element to omit that whisker.
            Default is ``(None, None)``.
        whiskercolor : str or None, optional
            Color of the whisker lines. When None the whiskers use the
            same color as the bar. Default is None.

        Returns
        -------
        EnergyDiagram
            Returns *self* to allow method chaining.
        """
        self._bar_manager.draw_difference_bar(
            x,
            y_start_end,
            description,
            self.margins,
            self.figsize,
            diff=diff,
            left_side=left_side,
            add_difference=add_difference,
            n_decimals=n_decimals,
            fontsize=fontsize,
            color=color,
            arrowstyle=arrowstyle,
            x_whiskers=x_whiskers,
            whiskercolor=whiskercolor,
        )
        return self

    def legend(self, loc: str = "best", fontsize: int | None = None) -> EnergyDiagram:
        """Add a legend for all named reaction paths.

        Generates legend entries for every path that was drawn with a
        ``path_name``. Each entry shows a colored patch matching the
        path color and the corresponding name.

        Parameters
        ----------
        loc : str, optional
            Legend location, as any Matplotlib ``loc`` string
            (e.g. ``"best"``, ``"upper right"``). Default is
            ``"best"``.
        fontsize : int or None, optional
            Font size of the legend text. When None the diagram's base
            font size is used. Default is None.

        Returns
        -------
        EnergyDiagram
            Returns *self* to allow method chaining.
        """
        Validators.validate_number(fontsize, "fontsize", allow_none=True, min_value=0)
        if fontsize is None:
            fontsize = self._figure_manager.fontsize
        patches = []
        for path_name, path_info in self._path_manager.path_data.items():
            if path_info["has_name"]:
                patches.append(mpatches.Patch(color=path_info["color"], label=path_name))
        self._figure_manager.ax.legend(handles=patches, fontsize=fontsize, loc=loc)
        return self

    def show(self) -> None:
        """Display the energy diagram figure.

        Finalizes the figure layout and calls ``matplotlib.pyplot.show()``.
        """
        figsize = self._layout_manager.scale_figure(self._path_manager.path_data)
        if self.verbose:
            print(f"Figure size is {round(figsize[0], 2)} x {round(figsize[1], 2)} inches.")
        plt.show()

    ############################################################
    # Path-related methods
    ############################################################

    def draw_path(
        self,
        x_data: Sequence[float],
        y_data: Sequence[float],
        color: str,
        linetypes: Sequence[int] | None = None,
        path_name: str | None = None,
        show_numbers: bool = True,
        width_plateau: float | None = None,
        lw_plateau: float | str = "plateau",
    ) -> EnergyDiagram:
        """Add a reaction path to the energy diagram.

        Draws a series of horizontal energy levels connected by
        transitions. Each segment between adjacent levels is drawn
        with the connector style specified by ``linetypes``.

        Parameters
        ----------
        x_data : sequence of float
            X-coordinates for each reaction state (energy level).
            Must have the same length as ``y_data``.
        y_data : sequence of float
            Y-coordinates (energy values) for each reaction state.
            Must have the same length as ``x_data``.
        color : str
            Color of the energy levels and connectors for this path,
            as any Matplotlib color string (e.g. ``"blue"``,
            ``"#FF5733"``).
        linetypes : sequence of int or int or None, optional
            Connector style(s) for the segments between consecutive
            energy levels. Must have length ``len(x_data) - 1``, or
            be a single integer applied to all segments. Allowed
            values:

            *  ``0``  : no connector
            *  ``1``  : dotted line (default)
            *  ``-1`` : broken dotted line
            *  ``2``  : solid line
            *  ``-2`` : broken solid line
            *  ``3``  : dotted cubic spline
            *  ``4``  : solid cubic spline

            When None, all segments use a dotted line (``1``).
        path_name : str or None, optional
            A name for this path used as the legend label. When None
            the path is not added to the legend. Default is None.
        show_numbers : bool, optional
            If False, energy values along this path are excluded from
            any subsequent ``add_numbers_*`` calls. Default is True.
        width_plateau : float or None, optional
            Width of the horizontal energy level bars in data coordinate
            units. When None, a default width is applied. Default is None.
        lw_plateau : float, str, or None, optional
            Line width for the horizontal energy level bars. Can be a
            float in points, or a string referring to a predefined
            value (``"plateau"`` or ``"connector"``). Default is ``"plateau"``.

        Returns
        -------
        EnergyDiagram
            Returns *self* to allow method chaining.
        """
        self._path_manager.draw_path(
            x_data,
            y_data,
            color,
            linetypes=linetypes,
            path_name=path_name,
            show_numbers=show_numbers,
            width_plateau=width_plateau,
            lw_plateau=lw_plateau,
        )
        self.margins = self._layout_manager.adjust_xy_limits(self._path_manager.path_data)
        self.figsize = self._layout_manager.scale_figure(self._path_manager.path_data)
        self._recalculate_xlabels()
        self._recalculate_axis_breaks()
        self._recalculate_merged_plateaus()
        self._recalculate_path_labels()
        return self

    def add_path_labels(
        self,
        path_name: str,
        labels: Sequence[str],
        fontsize: int | None = None,
        weight: str = "normal",
        color: str | None = None,
    ) -> EnergyDiagram:
        """Add text labels below the energy levels of a specific path.

        Parameters
        ----------
        path_name : str
            Name of the path to which the labels should be added.
        labels : sequence of str
            A sequence of text labels, one for each energy level in the path.
            If None is passed for a label, no label is drawn for that level.
            Must have the same length as the number of energy levels in the path.
        fontsize : int or None, optional
            Font size for the labels. When None the diagram's base font size
            is used. Default is None.
        weight : str, optional
            Font weight for the labels, e.g. ``"bold"`` or ``"normal"``.
            Default is ``"normal"``.
        color : str or None, optional
            Color for the labels. When None, uses the same color as the path.
            Default is None.

        Returns
        -------
        EnergyDiagram
            Returns *self* to allow method chaining.

        Raises
        ------
        ValueError
            If the specified path does not exist or if the number of labels
            does not match the number of energy levels in the path.
        """
        self._path_manager.add_path_labels(
            margins=self.margins,
            figsize=self.figsize,
            path_name=path_name,
            labels=labels,
            fontsize=fontsize,
            weight=weight,
            color=color,
        )
        if self._image_manager.has_image_series:
            self._image_manager.recalculate_image_series(
                self.margins,
                self.figsize,
                self._path_manager.path_data,
                self._number_manager.mpl_objects,
                self._style_manager.mpl_objects.x_labels,
                self._path_manager.mpl_objects,
            )
        if self._number_manager.numberings_added:
            self._number_manager._recalculate_numbers(
                path_data=self._path_manager.path_data,
                margins=self.margins,
                figsize=self.figsize,
                path_mpl_objects=self._path_manager.mpl_objects,
            )
        return self

    def _recalculate_path_labels(self):
        self._path_manager._recalculate_path_labels(
            margins=self.margins,
            figsize=self.figsize,
        )

    def merge_plateaus(
        self,
        x: int,
        path_name_left: str,
        path_name_right: str,
        gap_scale: float = 1,
        stopper_scale: float = 1,
        angle: float = 30,
    ) -> EnergyDiagram:
        """Visually merge two coincident plateaus at a shared x-position.

        When two paths have identical energy levels at the same x-coordinate,
        this method replaces both full-width plateaus with two shorter half-plateaus
        separated by a small gap. Diagonal stopper tick marks are drawn into the gap
        to indicate that the two levels are degenerate. The resulting split is
        recalculated automatically whenever a new path is added.

        Both paths must already exist and must have the same y-value at ``x``.

        Parameters
        ----------
        x : int
            The x-coordinate at which both paths share an energy level.
        path_name_left : str
            Name of the path whose plateau will appear on the left side of the gap.
        path_name_right : str
            Name of the path whose plateau will appear on the right side of the gap.
        gap_scale : float, optional
            Multiplicative scaling factor for the width of the gap between the two
            half-plateaus. Default is ``1``.
        stopper_scale : float, optional
            Multiplicative scaling factor for the size of the diagonal stopper tick
            marks drawn in the gap. Default is ``1``.
        angle : float, optional
            Angle of the stopper tick marks in degrees from the vertical.
            Default is ``30``.

        Returns
        -------
        EnergyDiagram
            Returns *self* to allow method chaining.

        Raises
        ------
        ValueError
            If either path does not exist, does not have a value at ``x``, or
            the two paths do not share the same y-value at ``x``.
        """
        self._path_manager.merge_plateaus(
            margins=self.margins,
            figsize=self.figsize,
            x=x,
            path_name_left=path_name_left,
            path_name_right=path_name_right,
            gap_scale=gap_scale,
            stopper_scale=stopper_scale,
            angle=angle,
        )
        return self

    def _recalculate_merged_plateaus(self):
        self._path_manager._recalculate_merged_plateaus(self.margins, self.figsize)

    ############################################################
    # Style-related methods
    ############################################################

    def set_xlabels(
        self,
        labels: Sequence,
        labelplaces: Sequence[float] | None = None,
        fontsize: int | None = None,
        weight: str = "bold",
        in_plot: bool = False,
    ) -> EnergyDiagram:
        """Set text labels for the reaction states along the x-axis.

        Labels are placed below the horizontal energy bars by default.
        If ``in_plot`` is True they are rendered inside the plot area
        directly below the lowest state.

        Parameters
        ----------
        labels : sequence
            Ordered sequence of label strings, one per reaction state
            (i.e. one per unique x-position in the plotted paths).
        labelplaces : sequence of float or None, optional
            Explicit x-coordinates at which to place each label.
            When None the labels are naively placed starting at
            x = 0. Default is None.
        fontsize : int or None, optional
            Font size for the labels. When None the diagram's base
            font size is used. Default is None.
        weight : str, optional
            Font weight for the labels, e.g. ``"bold"`` or
            ``"normal"``. Default is ``"bold"``.
        in_plot : bool, optional
            If True, labels are drawn inside the plot area below the
            lowest state rather than below the x-axis. Default
            is False.

        Returns
        -------
        EnergyDiagram
            Returns *self* to allow method chaining.
        """
        self._style_manager.set_xlabels(
            self.margins,
            self.figsize,
            self._path_manager.path_data,
            labels,
            labelplaces=labelplaces,
            fontsize=fontsize,
            weight=weight,
            in_plot=in_plot,
        )
        if self._image_manager.has_image_series:
            self._image_manager.recalculate_image_series(
                self.margins,
                self.figsize,
                self._path_manager.path_data,
                self._number_manager.mpl_objects,
                self._style_manager.mpl_objects.x_labels,
                self._path_manager.mpl_objects,
            )
        return self

    def _recalculate_xlabels(self):
        try:
            self.set_xlabels(**self._style_manager.labelproperties)
        except AttributeError:
            pass

    def set_diagram_style(self, style: str) -> EnergyDiagram:
        """Change the overall visual style of the diagram.

        Applies a named style preset that controls the appearance of
        the plot background, spines, tick marks, and other decorative
        elements.

        Parameters
        ----------
        style : str
            Name of the style preset to apply. Supported values
            are ``"boxed"``, ``"halfboxed"``, ``"open"``, ``"twosided"``
            and ``"borderless"``. Default style is ``"open"``.

        Returns
        -------
        EnergyDiagram
            Returns *self* to allow method chaining.
        """
        self._layout_manager.adjust_xy_limits(self._path_manager.path_data)
        self._style_manager.set_diagram_style(style)
        try:
            self.set_xlabels(
                **self._style_manager.labelproperties  # type: ignore[arg-type]
            )
        except AttributeError:
            pass
        return self

    def add_xaxis_break(
        self,
        x: float,
        gap_scale: float = 1,
        stopper_scale: float = 1,
        angle: float = 30,
    ) -> None:
        """Add a break marker on the x-axis at a given position.

        Draws a pair of diagonal stopper lines over a white gap rectangle on
        the x-axis (or axes spine) to indicate a discontinuity in the x scale.

        Not compatible with the ``"open"`` diagram style.

        Parameters
        ----------
        x : float
            Position along the x-axis (in data coordinates) where the break
            should be placed.
        gap_scale : float, optional
            Multiplicative scaling factor for the width of the white gap that
            covers the axis spine. Default is ``1``.
        stopper_scale : float, optional
            Multiplicative scaling factor for the size of the diagonal stopper
            tick marks. Default is ``1``.
        angle : float, optional
            Angle of the stopper tick marks in degrees from the vertical.
            Default is ``30``.
        """
        self._style_manager.add_xaxis_break(
            margins=self.margins,
            figsize=self.figsize,
            x=x,
            gap_scale=gap_scale,
            stopper_scale=stopper_scale,
            angle=angle,
        )

    def add_yaxis_break(
        self,
        y: float,
        gap_scale: float = 1,
        stopper_scale: float = 1,
        angle: float = 30,
    ) -> None:
        """Add a break marker on the y-axis at a given position.

        Draws a pair of diagonal stopper lines over a white gap rectangle on
        the y-axis spine to indicate a discontinuity in the y scale.

        Parameters
        ----------
        y : float
            Position along the y-axis (in data coordinates) where the break
            should be placed.
        gap_scale : float, optional
            Multiplicative scaling factor for the height of the white gap that
            covers the axis spine. Default is ``1``.
        stopper_scale : float, optional
            Multiplicative scaling factor for the size of the diagonal stopper
            tick marks. Default is ``1``.
        angle : float, optional
            Angle of the stopper tick marks in degrees from the horizontal.
            Default is ``30``.
        """
        self._style_manager.add_yaxis_break(
            margins=self.margins,
            figsize=self.figsize,
            y=y,
            gap_scale=gap_scale,
            stopper_scale=stopper_scale,
            angle=angle,
        )

    def _recalculate_axis_breaks(self):
        if self._style_manager.has_axes_breaks:
            self._style_manager.recalculate_axis_breaks(self.margins, self.figsize)

    ############################################################
    # Methods for plotting numbers
    ############################################################

    def add_numbers_naive(
        self,
        x_min_max: tuple[float, float] | list[float] | float | None = None,
        fontsize: int | None = None,
        n_decimals: int = 0,
    ) -> EnergyDiagram:
        """Annotate energy levels with their values, placed directly above each bar.

        This is the simplest numbering strategy: each energy value is
        printed at its x-position, just above the corresponding
        horizontal bar, with no attempt to resolve overlapping labels.
        Paths where ``show_numbers=False`` was passed to
        :meth:`draw_path` are excluded.

        Parameters
        ----------
        x_min_max : tuple of float, list of float, float, or None, optional
            Restricts annotation to energy states whose x-coordinate
            falls within the interval ``[x_min, x_max]``.  Supply a
            two-element sequence for an interval, a single float to
            annotate only the state at that exact x-value, or None to
            annotate all states. Default is None.
        fontsize : int or None, optional
            Font size for the annotations. When None the diagram's
            base font size is used. Default is None.
        n_decimals : int, optional
            Number of decimal places to show for the energy values.
            Default is 0.

        Returns
        -------
        EnergyDiagram
            Returns *self* to allow method chaining.
        """
        self._number_manager.add_numbers_naive(
            self._path_manager.path_data,
            self.margins,
            self.figsize,
            x_min_max,
            fontsize=fontsize,
            n_decimals=n_decimals,
        )
        if self._image_manager.has_image_series:
            self._image_manager.recalculate_image_series(
                self.margins,
                self.figsize,
                self._path_manager.path_data,
                self._number_manager.mpl_objects,
                self._style_manager.mpl_objects.x_labels,
                self._path_manager.mpl_objects,
            )
        return self

    def add_numbers_stacked(
        self,
        x_min_max: tuple[float, float] | list[float] | float | None = None,
        fontsize: int | None = None,
        sort_by_energy: bool = True,
        no_overlap_with_nonnumbered: bool = True,
        n_decimals: int = 0,
    ) -> EnergyDiagram:
        """Annotate energy levels with stacked labels above the highest state.

        When multiple paths share the same x-position the labels are
        arranged vertically (stacked) so they do not collide. Paths
        where ``show_numbers=False`` was passed to :meth:`draw_path`
        are excluded from numbering but, unless ``no_overlap_with_nonnumbered``
        is False, their energy bars are still treated as obstacles that
        stacked labels must avoid.

        Parameters
        ----------
        x_min_max : tuple of float, list of float, float, or None, optional
            Restricts annotation to energy states within the interval
            ``[x_min, x_max]``. Supply a two-element sequence, a
            single float for an exact match, or None for all states.
            Default is None.
        fontsize : int or None, optional
            Font size for the annotations. When None the diagram's
            base font size is used. Default is None.
        sort_by_energy : bool, optional
            If True, labels at the same x-position are sorted by
            energy value before stacking, keeping them in order.
            Default is True.
        no_overlap_with_nonnumbered : bool, optional
            If True, labels are also offset to avoid colliding with
            energy bars belonging to paths that have ``show_numbers=False``.
            Default is True.
        n_decimals : int, optional
            Number of decimal places to show for the energy values.
            Default is 0.

        Returns
        -------
        EnergyDiagram
            Returns *self* to allow method chaining.
        """
        self._number_manager.add_numbers_stacked(
            self._path_manager.path_data,
            self.margins,
            self.figsize,
            self._path_manager.mpl_objects,
            x_min_max,
            fontsize=fontsize,
            sort_by_energy=sort_by_energy,
            no_overlap_with_nonnumbered=no_overlap_with_nonnumbered,
            n_decimals=n_decimals,
        )
        if self._image_manager.has_image_series:
            self._image_manager.recalculate_image_series(
                self.margins,
                self.figsize,
                self._path_manager.path_data,
                self._number_manager.mpl_objects,
                self._style_manager.mpl_objects.x_labels,
                self._path_manager.mpl_objects,
            )
        return self

    def add_numbers_auto(
        self,
        x_min_max: tuple[float, float] | list[float] | float | None = None,
        fontsize: int | None = None,
        n_decimals: int = 0,
    ) -> EnergyDiagram:
        """Annotate energy levels with automatically placed labels.

        Chooses label placement (above which bar) automatically
        for each energy state to minimize visual clutter, taking into
        account the relative positions of all paths. Paths
        where ``show_numbers=False`` was passed to :meth:`draw_path`
        are excluded from numbering.

        Parameters
        ----------
        x_min_max : tuple of float, list of float, float, or None, optional
            Restricts annotation to energy states within the interval
            ``[x_min, x_max]``. Supply a two-element sequence, a
            single float for an exact match, or None for all states.
            Default is None.
        fontsize : int or None, optional
            Font size for the annotations. When None the diagram's
            base font size is used. Default is None.
        n_decimals : int, optional
            Number of decimal places to show for the energy values.
            Default is 0.

        Returns
        -------
        EnergyDiagram
            Returns *self* to allow method chaining.
        """
        self._number_manager.add_numbers_auto(
            self._path_manager.path_data,
            self.margins,
            self.figsize,
            path_mpl_objects=self._path_manager.mpl_objects,
            x_min_max=x_min_max,
            fontsize=fontsize,
            n_decimals=n_decimals,
        )
        if self._image_manager.has_image_series:
            self._image_manager.recalculate_image_series(
                self.margins,
                self.figsize,
                self._path_manager.path_data,
                self._number_manager.mpl_objects,
                self._style_manager.mpl_objects.x_labels,
                self._path_manager.mpl_objects,
            )
        return self

    def add_numbers_average(
        self,
        x_min_max: tuple[float, float] | list[float] | float | None = None,
        fontsize: int | None = None,
        color: str = "black",
        n_decimals: int = 0,
    ) -> EnergyDiagram:
        """Annotate energy states with the average value across all paths.

        At each x-position the mean energy of all visible paths is
        computed and a single label is rendered. This is useful when
        multiple paths are close together and a single representative
        value is preferred over individual labels. Paths where
        ``show_numbers=False`` was passed to :meth:`draw_path` are
        excluded from the average.

        Parameters
        ----------
        x_min_max : tuple of float, list of float, float, or None, optional
            Restricts annotation to energy states within the interval
            ``[x_min, x_max]``. Supply a two-element sequence, a
            single float for an exact match, or None for all states.
            Default is None.
        fontsize : int or None, optional
            Font size for the annotations. When None the diagram's
            base font size is used. Default is None.
        color : str, optional
            Color of the annotation text. Default is ``"black"``.

        Returns
        -------
        EnergyDiagram
            Returns *self* to allow method chaining.
        """
        self._number_manager.add_numbers_average(
            self._path_manager.path_data,
            self.margins,
            self.figsize,
            x_min_max=x_min_max,
            fontsize=fontsize,
            color=color,
            n_decimals=n_decimals,
        )
        if self._image_manager.has_image_series:
            self._image_manager.recalculate_image_series(
                self.margins,
                self.figsize,
                self._path_manager.path_data,
                self._number_manager.mpl_objects,
                self._style_manager.mpl_objects.x_labels,
                self._path_manager.mpl_objects,
            )
        return self

    ############################################################
    # Methods for plotting images
    ############################################################

    def add_image_in_plot(
        self,
        img_path: str,
        position: tuple[float, float] | list[float],
        img_name: str | None = None,
        horizontal_alignment: str = "center",
        vertical_alignment: str = "center",
        width: float | None = None,
        height: float | None = None,
        framed: bool = False,
        frame_color: str = "black",
    ) -> EnergyDiagram:
        """
        Place a single image at an explicit data-coordinate position.

        The image is scaled to the requested ``width`` and/or ``height`` in
        data coordinates, preserving the aspect ratio when only one dimension
        is supplied. The rendered artist is stored in ``self.images`` under
        ``img_name``.

        Parameters
        ----------
        img_path : str
            File path to the image (any format supported by Matplotlib).
        position : tuple of float or list of float
            The (x, y) anchor point in data coordinates.
        img_name : str or None, optional
            Key under which the artist is stored. An automatic key is
            assigned when None. Default is None.
        horizontal_alignment : str, optional
            Horizontal anchor of ``position``: ``"left"``, ``"center"``,
            or ``"right"``. Default ``"center"``.
        vertical_alignment : str, optional
            Vertical anchor of ``position``: ``"top"``, ``"center"``,
            or ``"bottom"``. Default ``"center"``.
        width : float or None, optional
            Image width in data coordinate units. Default is None.
        height : float or None, optional
            Image height in data coordinate units. Default is None.
        framed : bool, optional
            If True, draws a rectangular border around the image. Default False.
        frame_color : str, optional
            Color of the frame border. Default ``"black"``.
        """
        self._image_manager.add_image_in_plot(
            img_path,
            position,
            margins=self.margins,
            figsize=self.figsize,
            img_name=img_name,
            horizontal_alignment=horizontal_alignment,
            vertical_alignment=vertical_alignment,
            width=width,
            height=height,
            framed=framed,
            frame_color=frame_color,
        )
        return self

    def add_image_series_in_plot(
        self,
        img_paths: Sequence[str],
        img_x_places: Sequence[float] | None = None,
        y_placement: Sequence[str] | str = "auto",
        y_offsets: Sequence[float] | float = 0,
        img_series_name: str | None = None,
        width: Sequence[float | None] | float | None = None,
        height: Sequence[float | None] | float | None = None,
        framed: Sequence[bool] | bool = False,
        frame_colors: Sequence[str] | str = "black",
    ) -> EnergyDiagram:
        """
        Place a series of images, one per x-position, avoiding visual collisions.

        For each image the method finds free vertical space above or below the
        nearest energy bar, number annotation, and x-axis label. Placement is
        chosen automatically or forced to ``"top"``/``"bottom"`` via
        ``y_placement``. The series artists are stored in ``self.images`` under
        ``img_series_name``.

        Parameters
        ----------
        img_paths : sequence of str
            Ordered file paths for each image in the series.
        img_x_places : sequence of float or None, optional
            x-coordinates for each image. Defaults to ``[0, 1, 2, ...]``.
        y_placement : sequence of str or str, optional
            Vertical placement strategy per image: ``"top"``, ``"bottom"``,
            or ``"auto"``. Default ``"auto"``.
        y_offsets : sequence of float or float, optional
            Additional vertical offset applied after collision avoidance.
            Default 0.
        img_series_name : str or None, optional
            Key under which artists are stored. Auto-assigned when None.
        width : sequence or float or None, optional
            Image widths in data coordinate units.
        height : sequence or float or None, optional
            Image heights in data coordinate units.
        framed : sequence of bool or bool, optional
            Whether to draw a border around each image. Default False.
        frame_colors : sequence of str or str, optional
            Border colors. Default ``"black"``.
        """
        self._image_manager.add_image_series_in_plot(
            img_paths,
            margins=self.margins,
            figsize=self.figsize,
            path_data=self._path_manager.path_data,
            number_mpl_objects=self._number_manager.mpl_objects,
            xlabel_mpl_objects=self._style_manager.mpl_objects.x_labels,
            path_mpl_objects=self._path_manager.mpl_objects,
            img_x_places=img_x_places,
            y_placement=y_placement,
            y_offsets=y_offsets,
            img_series_name=img_series_name,
            width=width,
            height=height,
            framed=framed,
            frame_colors=frame_colors,
        )
        return self

    ############################################################
    # Getters
    ############################################################

    @property
    def ax(self) -> Axes:
        """matplotlib.axes.Axes: The underlying Axes object for the diagram.

        Can be used to apply any additional Matplotlib customizations
        directly, such as setting axis labels, adding annotations, or
        adjusting tick marks.
        """
        return self._figure_manager.ax

    @property
    def fig(self) -> Figure:
        """matplotlib.figure.Figure: The underlying Figure object for the diagram.

        Can be used to save the figure, adjust figure-level properties
        such as DPI or size, or pass it to external Matplotlib routines.
        """
        return self._figure_manager.fig

    @property
    def lines(self) -> dict[str, PathObject]:
        """dict of str to PathObject: Matplotlib line objects for each reaction path.

        Keys are the path names supplied via the ``path_name`` argument
        of :meth:`draw_path`. Each value is a ``PathObject`` containing
        the rendered Matplotlib line and connector artists for that path.
        Paths drawn without a name are keyed by an internal identifier.
        """
        return self._path_manager.mpl_objects

    @property
    def ax_objects(self) -> StyleObjects:
        """StyleObjects: Matplotlib artists related to diagram styling.

        Contains the spine, tick, and background artists that are
        managed by the style manager. Useful for fine-grained style
        adjustments after calling :meth:`set_diagram_style`.
        """
        return self._style_manager.mpl_objects

    @property
    def bars(self) -> list[DifferenceBar]:
        """list of DifferenceBar: Energy difference bar objects in the diagram.

        Each entry corresponds to one :meth:`draw_difference_bar` call
        and holds the arrow, label text, and optional whisker artists.
        The list is ordered by the sequence in which bars were added.
        """
        return self._bar_manager.mpl_objects

    @property
    def numbers(self) -> dict[str, dict[str, Text]]:
        """dict of str to dict of str to Text: Energy annotation text objects.

        Outer keys are path names; inner keys are string representations
        of the x-coordinates at which annotations were placed. Each
        value is a Matplotlib ``Text`` artist. Populated after calling
        any of the ``add_numbers_*`` methods.
        """
        return self._number_manager.mpl_objects

    @property
    def images(self) -> dict:
        """dict: Image artists stored by the image manager.

        Keys are image or series names (as supplied via ``img_name`` or
        ``img_series_name``). Standalone images map directly to an
        ``ImageObject``; series map to a nested dict keyed by x-coordinate.
        Populated after calling :meth:`add_image_in_plot` or
        :meth:`add_image_series_in_plot`.
        """
        return self._image_manager.mpl_objects

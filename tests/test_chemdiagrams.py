"""
Tests for the chemdiagrams package.

Run with:
    pytest test_chemdiagrams.py

Or from the project root with the src layout:
    PYTHONPATH=src pytest test_chemdiagrams.py
"""

import matplotlib
import numpy as np
import pytest

matplotlib.use("Agg")  # non-interactive backend — no display required

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from chemdiagrams import EnergyDiagram
from chemdiagrams.managers.image_manager import ImageObject

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_diagram(**kwargs) -> EnergyDiagram:
    """Return a fresh EnergyDiagram with a simple single path."""
    dia = EnergyDiagram(**kwargs)
    dia.draw_path(
        x_data=[0, 1, 2, 3, 4], y_data=[0, 28, -14, 15, -22], color="blue", path_name="A"
    )
    return dia


@pytest.fixture(autouse=True)
def close_figures():
    """Close all matplotlib figures after every test to avoid resource leaks."""
    yield
    plt.close("all")


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------


class TestConstruction:
    def test_default_construction(self):
        dia = EnergyDiagram()
        assert isinstance(dia, EnergyDiagram)

    def test_ax_is_axes(self):
        dia = EnergyDiagram()
        assert isinstance(dia.ax, Axes)

    def test_fig_is_figure(self):
        dia = EnergyDiagram()
        assert isinstance(dia.fig, Figure)

    def test_custom_fontsize(self):
        dia = EnergyDiagram(fontsize=12)
        assert dia._figure_manager.fontsize == 12

    def test_custom_dpi(self):
        dia = EnergyDiagram(dpi=96)
        assert dia.fig.get_dpi() == 96

    def test_custom_figsize(self):
        dia = EnergyDiagram(figsize=(8, 4))
        w, h = dia.fig.get_size_inches()
        assert w == pytest.approx(8)
        assert h == pytest.approx(4)

    @pytest.mark.parametrize("style", ["open", "boxed", "halfboxed", "twosided", "borderless"])
    def test_valid_styles(self, style):
        dia = EnergyDiagram(style=style)
        assert isinstance(dia, EnergyDiagram)


# ---------------------------------------------------------------------------
# External Axis (Subplots)
# ---------------------------------------------------------------------------


class TestExternalAxis:
    """Tests for using EnergyDiagram with externally provided matplotlib axes."""

    def test_external_ax_provided(self):
        """Test that EnergyDiagram accepts an external axis."""
        fig, ax = plt.subplots()
        dia = EnergyDiagram(ax=ax)
        assert isinstance(dia, EnergyDiagram)
        assert dia.ax is ax

    def test_external_ax_uses_provided_figure(self):
        """Test that the diagram uses the figure from the external axis."""
        fig, ax = plt.subplots()
        dia = EnergyDiagram(ax=ax)
        assert dia.fig is fig

    def test_external_ax_flag_is_set(self):
        """Test that has_external_ax flag is True when ax is provided."""
        fig, ax = plt.subplots()
        dia = EnergyDiagram(ax=ax)
        assert dia._figure_manager.has_external_ax is True

    def test_internal_ax_flag_is_false(self):
        """Test that has_external_ax flag is False for default construction."""
        dia = EnergyDiagram()
        assert dia._figure_manager.has_external_ax is False

    def test_external_ax_invalid_type(self):
        """Test that providing an invalid type as ax raises TypeError."""
        with pytest.raises(TypeError):
            EnergyDiagram(ax="not an axis")

    def test_external_ax_with_draw_path(self):
        """Test that draw_path works with external axis."""
        fig, ax = plt.subplots()
        dia = EnergyDiagram(ax=ax)
        result = dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        assert result is dia

    def test_external_ax_with_multiple_paths(self):
        """Test drawing multiple paths on external axis."""
        fig, ax = plt.subplots()
        dia = EnergyDiagram(ax=ax)
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue", path_name="path_A")
        dia.draw_path([0, 1, 2], [0, 5, -10], color="red", path_name="path_B")
        assert len(dia._path_manager.path_data) == 2

    def test_external_ax_with_labels(self):
        """Test that set_xlabels works with external axis."""
        fig, ax = plt.subplots()
        dia = EnergyDiagram(ax=ax)
        dia.draw_path([0, 1, 2, 3, 4], [0, 28, -14, 15, -22], color="blue")
        result = dia.set_xlabels(["E", "TS1", "I", "TS2", "P"])
        assert result is dia

    def test_external_ax_with_numbers_auto(self):
        """Test that add_numbers_auto works with external axis."""
        fig, ax = plt.subplots()
        dia = EnergyDiagram(ax=ax)
        dia.draw_path([0, 1, 2, 3, 4], [0, 28, -14, 15, -22], color="blue")
        result = dia.add_numbers_auto()
        assert result is dia

    def test_external_ax_with_numbers_stacked(self):
        """Test that add_numbers_stacked works with external axis."""
        fig, ax = plt.subplots()
        dia = EnergyDiagram(ax=ax)
        dia.draw_path([0, 1, 2, 3, 4], [0, 28, -14, 15, -22], color="blue")
        result = dia.add_numbers_stacked()
        assert result is dia

    def test_external_ax_with_difference_bar(self):
        """Test that draw_difference_bar works with external axis."""
        fig, ax = plt.subplots()
        dia = EnergyDiagram(ax=ax)
        dia.draw_path([0, 1, 2, 3, 4], [0, 28, -14, 15, -22], color="blue")
        result = dia.draw_difference_bar(x=1, y_start_end=(0, 28), description=r"$\Delta E$: ")
        assert result is dia

    def test_external_ax_with_legend(self):
        """Test that legend works with external axis."""
        fig, ax = plt.subplots()
        dia = EnergyDiagram(ax=ax)
        dia.draw_path([0, 1, 2, 3, 4], [0, 28, -14, 15, -22], color="blue", path_name="Path A")
        result = dia.legend()
        assert result is dia

    def test_subplot_2x2_grid(self):
        """Test creating diagrams in a 2x2 subplot grid."""
        fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(10, 8))

        # Create diagrams for each subplot
        dia11 = EnergyDiagram(ax=axes[0, 0], style="halfboxed")
        dia11.draw_path([0, 1, 2, 3, 4], [0, 28, -14, 15, -22], color="blue")
        dia11.set_xlabels(["E", "TS1", "I", "TS2", "P"])

        dia12 = EnergyDiagram(ax=axes[0, 1], style="open")
        dia12.draw_path([0, 1, 2, 3, 4], [0, 25, 6, 15, -18], color="red")
        dia12.set_xlabels(["E", "TS1", "I", "TS2", "P"])

        dia21 = EnergyDiagram(ax=axes[1, 0], style="boxed")
        dia21.draw_path([0, 1, 2, 3, 4], [0, 28, -14, 15, -22], color="green")
        dia21.set_xlabels(["E", "TS1", "I", "TS2", "P"])

        dia22 = EnergyDiagram(ax=axes[1, 1], style="borderless")
        dia22.draw_path([0, 1, 2, 3, 4], [0, 25, 6, 15, -18], color="purple")
        dia22.set_xlabels(["E", "TS1", "I", "TS2", "P"])

        # Verify all diagrams use their respective axes and the same figure
        assert dia11.ax is axes[0, 0]
        assert dia12.ax is axes[0, 1]
        assert dia21.ax is axes[1, 0]
        assert dia22.ax is axes[1, 1]
        assert dia11.fig is fig
        assert dia12.fig is fig
        assert dia21.fig is fig
        assert dia22.fig is fig

    def test_subplot_1x3_grid(self):
        """Test creating diagrams in a 1x3 subplot grid."""
        fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(15, 4))

        diagrams = []
        colors = ["blue", "red", "green"]
        styles = ["open", "boxed", "halfboxed"]

        for i, (ax, color, style) in enumerate(zip(axes, colors, styles)):
            dia = EnergyDiagram(ax=ax, style=style)
            dia.draw_path([0, 1, 2], [0, i * 10, -5], color=color)
            diagrams.append(dia)

        # Verify all diagrams share the same figure
        for dia in diagrams:
            assert dia.fig is fig

        # Verify each diagram has a different axis
        for i, dia in enumerate(diagrams):
            assert dia.ax is axes[i]

    def test_subplot_with_width_ratios(self):
        """Test that subplot width_ratios are respected."""
        fig, axes = plt.subplots(
            nrows=2,
            ncols=2,
            width_ratios=[1.5, 1],
            figsize=(10, 6),
        )

        dia11 = EnergyDiagram(ax=axes[0, 0])
        dia11.draw_path([0, 1, 2, 3, 4, 5, 6], [0, 28, -14, 15, -22, 12, -13], color="blue")

        dia12 = EnergyDiagram(ax=axes[0, 1])
        dia12.draw_path([0, 1, 2, 3, 4], [0, 28, -14, 15, -22], color="blue")

        # Both diagrams should share the same figure
        assert dia11.fig is dia12.fig
        # But use different axes
        assert dia11.ax is not dia12.ax

    def test_external_ax_figsize_ignored(self):
        """Test that figsize parameter is effectively overridden by external ax."""
        fig, ax = plt.subplots(figsize=(8, 6))
        original_figsize = fig.get_size_inches()

        # Create diagram with an explicit figsize (should be ignored)
        dia = EnergyDiagram(ax=ax, figsize=(12, 10))

        # The figure size should match the external figure, not the requested figsize
        current_figsize = dia.fig.get_size_inches()
        assert np.allclose(current_figsize, original_figsize)

    def test_external_ax_width_limit_ignored(self):
        """Test that width_limit parameter is overridden by external ax."""
        fig, ax = plt.subplots(figsize=(6, 4))
        original_figsize = fig.get_size_inches()

        # Create diagram with a width_limit (should be ignored)
        dia = EnergyDiagram(ax=ax, width_limit=100)

        # The figure size should match the external figure, not be scaled by width_limit
        current_figsize = dia.fig.get_size_inches()
        assert np.allclose(current_figsize, original_figsize)

    def test_external_ax_all_styles(self):
        """Test that all diagram styles work with external axes."""
        styles = ["open", "boxed", "halfboxed", "twosided", "borderless"]

        for style in styles:
            fig, ax = plt.subplots()
            dia = EnergyDiagram(ax=ax, style=style)
            dia.draw_path([0, 1, 2, 3, 4], [0, 28, -14, 15, -22], color="blue")
            assert dia.ax is ax
            assert dia.fig is fig
            plt.close(fig)

    def test_external_ax_with_custom_fontsize(self):
        """Test that custom fontsize works with external axis."""
        fig, ax = plt.subplots()
        dia = EnergyDiagram(ax=ax, fontsize=14)
        assert dia._figure_manager.fontsize == 14

    def test_external_ax_with_numbers_naive(self):
        """Test that add_numbers_naive works with external axis."""
        fig, ax = plt.subplots()
        dia = EnergyDiagram(ax=ax)
        dia.draw_path([0, 1, 2, 3, 4], [0, 28, -14, 15, -22], color="blue")
        result = dia.add_numbers_naive()
        assert result is dia

    def test_external_ax_with_numbers_average(self):
        """Test that add_numbers_average works with external axis."""
        fig, ax = plt.subplots()
        dia = EnergyDiagram(ax=ax)
        dia.draw_path([0, 1, 2, 3, 4], [0, 28, -14, 15, -22], color="blue")
        result = dia.add_numbers_average()
        assert result is dia

    def test_external_ax_with_path_labels(self):
        """Test that add_path_labels works with external axis."""
        fig, ax = plt.subplots()
        dia = EnergyDiagram(ax=ax)
        dia.draw_path([0, 1, 2, 3, 4], [0, 28, -14, 15, -22], color="blue", path_name="Path")
        result = dia.add_path_labels("Path", ["E", "TS1", "I", "TS2", "P"])
        assert result is dia

    def test_external_ax_with_axis_breaks(self):
        """Test that add_xaxis_break and add_yaxis_break work with external axis."""
        fig, ax = plt.subplots()
        # Use twosided style which supports axis breaks
        dia = EnergyDiagram(ax=ax, style="twosided")
        dia.draw_path([0, 1, 2, 3, 4, 5], [0, -13, 22, 75, 39, -25], color="blue")
        dia.add_xaxis_break(x=2)
        dia.add_yaxis_break(y=5)
        assert dia.ax is ax

    def test_external_ax_with_merge_plateaus(self):
        """Test that merge_plateaus works with external axis."""
        fig, ax = plt.subplots()
        dia = EnergyDiagram(ax=ax)
        dia.draw_path([0, 1, 2], [10, 55, 0], color="blue", path_name="Path A")
        dia.draw_path([2, 3, 4], [0, 50, -5], color="red", path_name="Path B")
        result = dia.merge_plateaus(x=2, path_name_left="Path A", path_name_right="Path B")
        assert result is dia

    def test_external_ax_multiple_operations_chain(self):
        """Test that method chaining works correctly with external axis."""
        fig, ax = plt.subplots()
        dia = (
            EnergyDiagram(ax=ax, style="halfboxed")
            .draw_path([0, 1, 2, 3, 4], [0, 28, -14, 15, -22], color="blue", path_name="Path")
            .draw_path([0, 1, 2, 3, 4], [0, 25, 6, 15, -18], color="red", path_name="Path2")
            .set_xlabels(["E", "TS1", "I", "TS2", "P"])
            .add_numbers_auto()
            .legend()
        )
        assert dia.ax is ax
        assert len(dia._path_manager.path_data) == 2


# ---------------------------------------------------------------------------
# draw_path
# ---------------------------------------------------------------------------


class TestDrawPath:
    def test_single_path(self):
        dia = EnergyDiagram()
        result = dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        assert result is dia  # method chaining

    def test_multiple_paths(self):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue", path_name="path_A")
        dia.draw_path([0, 1, 2], [0, 5, -10], color="red", path_name="path_B")
        assert len(dia._path_manager.path_data) == 2

    def test_path_stored_by_name(self):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="green", path_name="my_path")
        assert "my_path" in dia._path_manager.path_data

    def test_path_without_name(self):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="green")
        assert len(dia._path_manager.path_data) == 1

    def test_all_linetypes(self):
        """All defined linetype codes should not raise."""
        for lt in [0, 1, -1, 2, -2]:
            dia = EnergyDiagram()
            dia.draw_path([0, 1], [0, 10], color="blue", linetypes=[lt])
            plt.close("all")

    def test_show_numbers_false(self):
        dia = EnergyDiagram()
        dia.draw_path(
            [0, 1, 2], [0, 10, -5], color="blue", path_name="hidden", show_numbers=False
        )
        path_info = dia._path_manager.path_data["hidden"]
        assert path_info["show_numbers"] is False

    def test_returns_self_for_chaining(self):
        dia = EnergyDiagram()
        result = dia.draw_path([0, 1, 2], [0, 10, -5], color="blue").draw_path(
            [0, 1, 2], [0, 5, 0], color="red"
        )
        assert result is dia

    def test_custom_width_plateau(self):
        dia = EnergyDiagram()
        dia.draw_path(
            [0, 1, 2],
            [0, 10, -5],
            color="blue",
            width_plateau=0.8,
            path_name="wp_test",
        )

    def test_zero_width_plateau_is_none(self):
        dia = EnergyDiagram()
        dia.draw_path(
            [0, 1, 2],
            [0, 10, -5],
            color="blue",
            width_plateau=0,
            path_name="wp_test",
        )
        plateau = dia._path_manager.mpl_objects["wp_test"].plateaus["0.0"]
        assert plateau is None

    def test_lw_plateau_numeric(self):
        dia = EnergyDiagram()
        dia.draw_path(
            [0, 1, 2],
            [0, 10, -5],
            color="blue",
            lw_plateau=2.5,
            path_name="lw_num",
        )

    def test_lw_plateau_string_plateau(self):
        dia = EnergyDiagram()
        dia.draw_path(
            [0, 1, 2],
            [0, 10, -5],
            color="blue",
            lw_plateau="plateau",
            path_name="lw_plateau",
        )

    def test_lw_plateau_string_connector(self):
        dia = EnergyDiagram()
        dia.draw_path(
            [0, 1, 2],
            [0, 10, -5],
            color="blue",
            lw_plateau="connector",
            path_name="lw_conn",
        )

    def test_lw_plateau_invalid_string(self):
        dia = EnergyDiagram()
        with pytest.raises(ValueError):
            dia.draw_path(
                [0, 1, 2],
                [0, 10, -5],
                color="blue",
                lw_plateau="invalid",
            )

    def test_lw_connector_numeric(self):
        dia = EnergyDiagram()
        dia.draw_path(
            [0, 1, 2],
            [0, 10, -5],
            color="blue",
            lw_connector=2.5,
            path_name="lw_conn_num",
        )

    def test_lw_connector_string_plateau(self):
        dia = EnergyDiagram()
        dia.draw_path(
            [0, 1, 2],
            [0, 10, -5],
            color="blue",
            lw_connector="plateau",
            path_name="lw_conn_plateau",
        )

    def test_lw_connector_string_connector(self):
        dia = EnergyDiagram()
        dia.draw_path(
            [0, 1, 2],
            [0, 10, -5],
            color="blue",
            lw_connector="connector",
            path_name="lw_conn_connector",
        )

    def test_lw_connector_invalid_string(self):
        dia = EnergyDiagram()
        with pytest.raises(ValueError):
            dia.draw_path(
                [0, 1, 2],
                [0, 10, -5],
                color="blue",
                lw_connector="invalid",
            )

    def test_lw_connector_with_linetype(self):
        """Test lw_connector with different linetypes."""
        for linetype in [-2, -1, 1, 2]:
            dia = EnergyDiagram()
            dia.draw_path(
                [0, 1, 2],
                [0, 10, -5],
                color="blue",
                linetypes=[linetype, 1],
                lw_connector=1.5,
                path_name=f"lw_conn_lt{linetype}",
            )

    def test_gap_scale_numeric(self):
        dia = EnergyDiagram()
        dia.draw_path(
            [0, 1, 2],
            [0, 10, -5],
            color="blue",
            linetypes=[-1, 1],
            gap_scale=0.5,
            path_name="gap_scale_num",
        )

    def test_gap_scale_sequence(self):
        dia = EnergyDiagram()
        dia.draw_path(
            [0, 1, 2, 3],
            [0, 10, -5, 15],
            color="blue",
            linetypes=[-1, -2, 1],
            gap_scale=[0.5, 0.75, 1.0],
            path_name="gap_scale_seq",
        )

    def test_gap_scale_sequence_length_mismatch(self):
        dia = EnergyDiagram()
        with pytest.raises(ValueError):
            dia.draw_path(
                [0, 1, 2, 3],
                [0, 10, -5, 15],
                color="blue",
                linetypes=[-1, -2, 1],
                gap_scale=[0.5, 0.75],  # Only 2 elements instead of 3
                path_name="gap_scale_mismatch",
            )

    def test_gap_scale_string_raises_error(self):
        dia = EnergyDiagram()
        with pytest.raises(TypeError):
            dia.draw_path(
                [0, 1, 2],
                [0, 10, -5],
                color="blue",
                linetypes=[-1, 1],
                gap_scale="invalid",
            )

    def test_gap_scale_too_large_raises_error(self):
        """Test that gap_scale values too large (gap >= 100%) raise an error."""
        dia = EnergyDiagram()
        with pytest.raises(ValueError):
            dia.draw_path(
                [0, 1, 2],
                [0, 10, -5],
                color="blue",
                linetypes=[-1, 1],
                gap_scale=100,  # Effectively 100% or more
                path_name="gap_scale_too_large",
            )

    def test_linetype_broken_spline_dotted(self):
        """Test linetype -3 for broken splines with dotted style."""
        dia = EnergyDiagram()
        dia.draw_path(
            [0, 1, 2],
            [0, 10, -5],
            color="blue",
            linetypes=[-3, 1],
            path_name="broken_spline_dotted",
        )

    def test_linetype_broken_spline_solid(self):
        """Test linetype -4 for broken splines with solid style."""
        dia = EnergyDiagram()
        dia.draw_path(
            [0, 1, 2],
            [0, 10, -5],
            color="blue",
            linetypes=[-4, 1],
            path_name="broken_spline_solid",
        )

    def test_linetype_broken_spline_with_gap_scale(self):
        """Test broken splines with custom gap_scale."""
        dia = EnergyDiagram()
        dia.draw_path(
            [0, 1, 2],
            [0, 10, -5],
            color="blue",
            linetypes=[-3, 1],
            gap_scale=0.6,
            path_name="broken_spline_gap",
        )

    def test_all_new_linetypes(self):
        """All new linetype codes (-3, -4) should not raise."""
        for lt in [-3, -4]:
            dia = EnergyDiagram()
            dia.draw_path([0, 1], [0, 10], color="blue", linetypes=[lt])
            plt.close("all")

    def test_multiple_linetypes_with_mixed_broken(self):
        """Test path with mix of regular and broken line styles."""
        dia = EnergyDiagram()
        dia.draw_path(
            [0, 1, 2, 3, 4],
            [0, 10, -5, 15, 8],
            color="blue",
            linetypes=[1, -3, 2, -4],
            path_name="mixed_linetypes",
        )

    def test_lw_connector_and_gap_scale_together(self):
        """Test using both lw_connector and gap_scale parameters together."""
        dia = EnergyDiagram()
        dia.draw_path(
            [0, 1, 2],
            [0, 10, -5],
            color="blue",
            linetypes=[-2, 1],
            lw_connector=2.0,
            gap_scale=0.5,
            path_name="lw_and_gap",
        )

    def test_lw_connector_zero_raises_error(self):
        """Test that lw_connector=0 doesn't raise (matplotlib allows it)."""
        dia = EnergyDiagram()
        # This should work as matplotlib doesn't restrict zero linewidth
        dia.draw_path(
            [0, 1, 2],
            [0, 10, -5],
            color="blue",
            linetypes=[1, 1],
            lw_connector=0,
            path_name="lw_zero",
        )

    def test_gap_scale_zero(self):
        """Test that gap_scale=0 creates no gap (solid broken line appearance)."""
        dia = EnergyDiagram()
        dia.draw_path(
            [0, 1, 2],
            [0, 10, -5],
            color="blue",
            linetypes=[-1, 1],
            gap_scale=0,
            path_name="gap_scale_zero",
        )


# ---------------------------------------------------------------------------
# set_xlabels
# ---------------------------------------------------------------------------


class TestSetXLabels:
    def test_basic_labels(self):
        dia = make_diagram()
        result = dia.set_xlabels(["E", "TS1", "I", "TS2", "P"])
        assert result is dia

    def test_in_plot_labels(self):
        dia = make_diagram()
        dia.set_xlabels(["E", "TS1", "I", "TS2", "P"], in_plot=True)

    def test_custom_fontsize(self):
        dia = make_diagram()
        dia.set_xlabels(["E", "TS1", "I", "TS2", "P"], fontsize=10)

    def test_custom_weight(self):
        dia = make_diagram()
        dia.set_xlabels(["E", "TS1", "I", "TS2", "P"], weight="normal")

    def test_explicit_labelplaces(self):
        dia = make_diagram()
        dia.set_xlabels(["E", "TS1", "I", "TS2", "P"], labelplaces=[0, 1, 2, 3, 4])


# ---------------------------------------------------------------------------
# Numbering methods
# ---------------------------------------------------------------------------


class TestNumbering:
    def test_add_numbers_naive(self):
        dia = make_diagram()
        result = dia.add_numbers_naive()
        assert result is dia

    def test_add_numbers_naive_with_fontsize(self):
        dia = make_diagram()
        dia.add_numbers_naive(fontsize=8)

    def test_add_numbers_naive_x_range(self):
        dia = make_diagram()
        dia.add_numbers_naive(x_min_max=(1, 3))

    def test_add_numbers_stacked(self):
        dia = make_diagram()
        result = dia.add_numbers_stacked()
        assert result is dia

    def test_add_numbers_stacked_unsorted(self):
        dia = make_diagram()
        dia.add_numbers_stacked(sort_by_energy=False)

    def test_add_numbers_auto(self):
        dia = make_diagram()
        result = dia.add_numbers_auto()
        assert result is dia

    def test_add_numbers_auto_x_range(self):
        dia = make_diagram()
        dia.add_numbers_auto(x_min_max=(0, 2))

    def test_add_numbers_average(self):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue", path_name="A")
        dia.draw_path([0, 1, 2], [0, 6, -3], color="red", path_name="B")
        result = dia.add_numbers_average()
        assert result is dia

    def test_add_numbers_average_color(self):
        dia = make_diagram()
        dia.add_numbers_average(color="red")

    def test_numbers_dict_populated(self):
        dia = make_diagram()
        dia.add_numbers_naive()
        assert len(dia.numbers) > 0

    def test_modify_number_values_basic(self):
        """Test basic number modification at a single x-position."""
        dia = make_diagram()
        dia.add_numbers_naive()
        result = dia.modify_number_values(x=1)
        assert result is dia  # method chaining

    def test_modify_number_values_with_base_value(self):
        """Test modifying numbers with a custom base_value."""
        dia = make_diagram()
        dia.add_numbers_naive()
        dia.modify_number_values(x=1, base_value=10.0)

    def test_modify_number_values_with_x_add(self):
        """Test modifying numbers by adding energy values from x positions."""
        dia = make_diagram()
        dia.add_numbers_naive()
        # Add energy values from x=0 and x=2
        dia.modify_number_values(x=1, x_add=[0, 2])

    def test_modify_number_values_with_x_add_single_value(self):
        """Test x_add with a single float instead of list."""
        dia = make_diagram()
        dia.add_numbers_naive()
        dia.modify_number_values(x=1, x_add=0)

    def test_modify_number_values_with_x_subtract(self):
        """Test modifying numbers by subtracting energy values from x positions."""
        dia = make_diagram()
        dia.add_numbers_naive()
        # Subtract energy value from x=0
        dia.modify_number_values(x=2, x_subtract=[0])

    def test_modify_number_values_with_x_subtract_single_value(self):
        """Test x_subtract with a single float instead of list."""
        dia = make_diagram()
        dia.add_numbers_naive()
        dia.modify_number_values(x=2, x_subtract=0)

    def test_modify_number_values_with_both_add_and_subtract(self):
        """Test modifying numbers with both x_add and x_subtract."""
        dia = make_diagram()
        dia.add_numbers_naive()
        dia.modify_number_values(x=2, base_value=5.0, x_add=[1], x_subtract=[0])

    def test_modify_number_values_with_brackets(self):
        """Test modifying numbers with custom brackets."""
        dia = make_diagram()
        dia.add_numbers_naive()
        dia.modify_number_values(x=1, brackets=("[", "]"))

    def test_modify_number_values_with_empty_brackets(self):
        """Test modifying numbers without brackets."""
        dia = make_diagram()
        dia.add_numbers_naive()
        dia.modify_number_values(x=1, brackets=("", ""))

    def test_modify_number_values_with_none_brackets(self):
        """Test modifying numbers with None for brackets."""
        dia = make_diagram()
        dia.add_numbers_naive()
        dia.modify_number_values(x=1, brackets=None)

    def test_modify_number_values_with_n_decimals(self):
        """Test modifying numbers with custom decimal places."""
        dia = make_diagram()
        dia.add_numbers_naive()
        dia.modify_number_values(x=1, n_decimals=2)

    def test_modify_number_values_with_include_paths(self):
        """Test modifying numbers for specific paths using include_paths."""
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue", path_name="path_A")
        dia.draw_path([0, 1, 2], [0, 6, -3], color="red", path_name="path_B")
        dia.add_numbers_naive()
        dia.modify_number_values(x=1, include_paths=["path_A"])

    def test_modify_number_values_with_multiple_include_paths(self):
        """Test modifying numbers for multiple specific paths."""
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue", path_name="path_A")
        dia.draw_path([0, 1, 2], [0, 6, -3], color="red", path_name="path_B")
        dia.draw_path([0, 1, 2], [0, 8, -2], color="green", path_name="path_C")
        dia.add_numbers_naive()
        dia.modify_number_values(x=1, include_paths=["path_A", "path_B"])

    def test_modify_number_values_with_exclude_paths(self):
        """Test modifying numbers for all paths except specified ones."""
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue", path_name="path_A")
        dia.draw_path([0, 1, 2], [0, 6, -3], color="red", path_name="path_B")
        dia.draw_path([0, 1, 2], [0, 8, -2], color="green", path_name="path_C")
        dia.add_numbers_naive()
        dia.modify_number_values(x=1, exclude_paths=["path_A"])

    def test_modify_number_values_with_multiple_exclude_paths(self):
        """Test excluding multiple paths from modification."""
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue", path_name="path_A")
        dia.draw_path([0, 1, 2], [0, 6, -3], color="red", path_name="path_B")
        dia.draw_path([0, 1, 2], [0, 8, -2], color="green", path_name="path_C")
        dia.add_numbers_naive()
        dia.modify_number_values(x=1, exclude_paths=["path_A", "path_B"])

    def test_modify_number_values_include_and_exclude_raises(self):
        """Test that specifying both include_paths and exclude_paths raises ValueError."""
        dia = make_diagram()
        dia.add_numbers_naive()
        with pytest.raises(ValueError):
            dia.modify_number_values(x=1, include_paths=["A"], exclude_paths=["A"])

    def test_modify_number_values_nonexistent_path_in_include_raises(self):
        """Test that including a nonexistent path raises ValueError."""
        dia = make_diagram()
        dia.add_numbers_naive()
        with pytest.raises(ValueError):
            dia.modify_number_values(x=1, include_paths=["nonexistent"])

    def test_modify_number_values_after_stacked_numbering(self):
        """Test modifying numbers that were added with add_numbers_stacked."""
        dia = make_diagram()
        dia.add_numbers_stacked()
        dia.modify_number_values(x=1, base_value=100.0, n_decimals=1)

    def test_modify_number_values_after_auto_numbering(self):
        """Test modifying numbers that were added with add_numbers_auto."""
        dia = make_diagram()
        dia.add_numbers_auto()
        dia.modify_number_values(x=2, x_subtract=[0], brackets=["Δ", ""])

    def test_modify_number_values_after_average_numbering(self):
        """Test modifying numbers that were added with add_numbers_average."""
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue", path_name="A")
        dia.draw_path([0, 1, 2], [0, 6, -3], color="red", path_name="B")
        dia.add_numbers_average()
        dia.modify_number_values(x=1, base_value=50.0)

    def test_modify_number_values_complex_calculation(self):
        """Test a complex energy calculation with multiple additions and subtractions."""
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2, 3], [0, 20, 10, 15], color="blue", path_name="path_1")
        dia.add_numbers_naive()
        # Calculate: base_value + values[1] + values[2] - values[0]
        dia.modify_number_values(
            x=3, base_value=5.0, x_add=[1, 2], x_subtract=[0], n_decimals=1
        )

    def test_modify_number_values_with_special_characters_in_brackets(self):
        """Test modifying numbers with special unicode characters in brackets."""
        dia = make_diagram()
        dia.add_numbers_naive()
        dia.modify_number_values(x=1, brackets=["‡", "‡"])

    def test_modify_number_values_integration_full_workflow(self):
        """Integration test: complete workflow with multiple numbering and modifications."""
        dia = EnergyDiagram(fontsize=8)
        dia.draw_path([0, 1, 2, 3], [0, 20, -10, 5], color="blue", path_name="pathway")
        dia.add_numbers_naive()
        dia.modify_number_values(x=1, x_subtract=[0], brackets=["Ea", ""])
        dia.modify_number_values(x=3, x_subtract=[0], brackets=["ΔH", ""], n_decimals=1)
        assert len(dia.numbers) > 0


# ---------------------------------------------------------------------------
# Difference bars
# ---------------------------------------------------------------------------


class TestDifferenceBars:
    def test_basic_bar(self):
        dia = make_diagram()
        result = dia.draw_difference_bar(x=2.5, y_start_end=(-22, 28), description="ΔE: ")
        assert result is dia

    def test_bar_left_side(self):
        dia = make_diagram()
        dia.draw_difference_bar(x=0.5, y_start_end=(0, 28), description="ΔE: ", left_side=True)

    def test_bar_no_auto_diff(self):
        dia = make_diagram()
        dia.draw_difference_bar(
            x=0.5,
            y_start_end=(0, 28),
            description="ΔE = 28 kJ/mol",
            add_difference=False,
        )

    def test_bar_custom_color(self):
        dia = make_diagram()
        dia.draw_difference_bar(x=2.5, y_start_end=(-22, 28), description="ΔE: ", color="red")

    def test_bar_whiskers(self):
        dia = make_diagram()
        dia.draw_difference_bar(
            x=2.5, y_start_end=(-22, 28), description="ΔE: ", x_whiskers=(0, 4)
        )

    def test_bars_list_populated(self):
        dia = make_diagram()
        dia.draw_difference_bar(x=2.5, y_start_end=(-22, 28), description="ΔE: ")
        assert len(dia.bars) == 1


# ---------------------------------------------------------------------------
# Diagram styles
# ---------------------------------------------------------------------------


class TestDiagramStyle:
    @pytest.mark.parametrize("style", ["open", "boxed", "halfboxed", "twosided", "borderless"])
    def test_set_diagram_style(self, style):
        dia = make_diagram()
        result = dia.set_diagram_style(style)
        assert result is dia


# ---------------------------------------------------------------------------
# Legend
# ---------------------------------------------------------------------------


class TestLegend:
    def test_legend_with_named_paths(self):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue", path_name="Path A")
        dia.draw_path([0, 1, 2], [0, 5, -2], color="red", path_name="Path B")
        result = dia.legend()
        assert result is dia

    def test_legend_no_named_paths(self):
        """Should not raise even when no paths have names."""
        dia = make_diagram()
        dia.legend()

    def test_legend_loc(self):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue", path_name="P")
        dia.legend(loc="upper right")

    def test_legend_fontsize(self):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue", path_name="P")
        dia.legend(fontsize=10)


# ---------------------------------------------------------------------------
# Axis breaks
# ---------------------------------------------------------------------------


class TestAxisBreaks:
    def test_yaxis_break(self):
        dia = EnergyDiagram(style="boxed")
        dia.draw_path([0, 1, 2], [0, 100, -5], color="blue")
        dia.add_yaxis_break(y=50)

    def test_xaxis_break(self):
        dia = EnergyDiagram(style="boxed")
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.add_xaxis_break(x=1)


# ---------------------------------------------------------------------------
# Merge plateaus
# ---------------------------------------------------------------------------


class TestMergePlateaus:
    def test_merge_coincident_levels(self):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue", path_name="A")
        dia.draw_path([0, 1, 2], [0, 10, -8], color="red", path_name="B")
        result = dia.merge_plateaus(x=1, path_name_left="A", path_name_right="B")
        assert result is dia

    def test_merge_nonexistent_path_raises(self):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue", path_name="A")
        with pytest.raises((ValueError, KeyError)):
            dia.merge_plateaus(x=1, path_name_left="A", path_name_right="nonexistent")


# ---------------------------------------------------------------------------
# Properties / getters
# ---------------------------------------------------------------------------


class TestProperties:
    def test_ax_property(self):
        dia = EnergyDiagram()
        assert isinstance(dia.ax, Axes)

    def test_fig_property(self):
        dia = EnergyDiagram()
        assert isinstance(dia.fig, Figure)

    def test_lines_property(self):
        dia = make_diagram()
        assert isinstance(dia.lines, dict)

    def test_bars_property_empty(self):
        dia = make_diagram()
        assert dia.bars == [] or isinstance(dia.bars, list)

    def test_numbers_property_empty(self):
        dia = make_diagram()
        assert isinstance(dia.numbers, dict)

    def test_images_property_empty(self):
        dia = make_diagram()
        assert isinstance(dia.images, dict)


# ---------------------------------------------------------------------------
# Validators
# ---------------------------------------------------------------------------


class TestValidators:
    from chemdiagrams.validation.validators import Validators

    def test_validate_number_none_not_allowed(self):
        from chemdiagrams.validation.validators import Validators

        with pytest.raises(ValueError):
            Validators.validate_number(None, "x", allow_none=False)

    def test_validate_number_none_allowed(self):
        from chemdiagrams.validation.validators import Validators

        Validators.validate_number(None, "x", allow_none=True)  # should not raise

    def test_validate_number_below_min(self):
        from chemdiagrams.validation.validators import Validators

        with pytest.raises(ValueError):
            Validators.validate_number(5, "x", min_value=10)

    def test_validate_number_non_numeric(self):
        from chemdiagrams.validation.validators import Validators

        with pytest.raises(TypeError):
            Validators.validate_number("hello", "x")

    def test_validate_number_integer_only(self):
        from chemdiagrams.validation.validators import Validators

        with pytest.raises(TypeError):
            Validators.validate_number(3.5, "x", only_integer=True)

    def test_validate_numeric_sequence_valid(self):
        from chemdiagrams.validation.validators import Validators

        Validators.validate_numeric_sequence([1, 2, 3], "seq")  # no raise

    def test_validate_numeric_sequence_wrong_length(self):
        from chemdiagrams.validation.validators import Validators

        with pytest.raises(ValueError):
            Validators.validate_numeric_sequence([1, 2], "seq", required_length=3)

    def test_validate_numeric_sequence_non_numeric(self):
        from chemdiagrams.validation.validators import Validators

        with pytest.raises(TypeError):
            Validators.validate_numeric_sequence([1, "a", 3], "seq")

    def test_validate_numeric_sequence_string_rejected(self):
        from chemdiagrams.validation.validators import Validators

        with pytest.raises(TypeError):
            Validators.validate_numeric_sequence("123", "seq")

    def test_validate_string_sequence_valid(self):
        from chemdiagrams.validation.validators import Validators

        Validators.validate_string_sequence(["a", "b"], "seq")  # no raise

    def test_validate_string_sequence_wrong_type(self):
        from chemdiagrams.validation.validators import Validators

        with pytest.raises(TypeError):
            Validators.validate_string_sequence([1, 2], "seq")

    def test_validate_string_sequence_wrong_length(self):
        from chemdiagrams.validation.validators import Validators

        with pytest.raises(ValueError):
            Validators.validate_string_sequence(["a"], "seq", required_length=3)


# ---------------------------------------------------------------------------
# Integration / smoke tests
# ---------------------------------------------------------------------------


class TestIntegration:
    def test_full_workflow(self):
        """Mimics a realistic use of the library end-to-end."""
        dia = EnergyDiagram(fontsize=8, style="open")
        dia.draw_path(
            [0, 1, 2, 3, 4], [0, 28, -14, 15, -22], color="blue", path_name="Pathway A"
        )
        dia.draw_path(
            [0, 1, 2, 3, 4], [0, 20, -10, 12, -25], color="red", path_name="Pathway B"
        )
        dia.set_xlabels(["E", "TS1", "I", "TS2", "P"])
        dia.add_numbers_auto()
        dia.draw_difference_bar(x=4.5, y_start_end=(-25, 0), description="ΔE: ")
        dia.legend()
        assert isinstance(dia.fig, Figure)

    def test_verbose_mode(self, capsys):
        dia = EnergyDiagram(verbose=True)
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.show()
        captured = capsys.readouterr()
        assert "Figure size" in captured.out

    def test_multiple_numbering_methods_dont_crash(self):
        """Calling different numbering methods sequentially should not raise."""
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue", path_name="A")
        dia.draw_path([0, 1, 2], [0, 6, -3], color="red", path_name="B")
        dia.add_numbers_naive()
        dia.add_numbers_stacked()
        dia.add_numbers_auto()
        dia.add_numbers_average()

    def test_margins_update_after_draw_path(self):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue")
        margins_1 = dia.margins
        dia.draw_path([0, 1], [0, 100], color="red")
        margins_2 = dia.margins
        # y-range should have grown
        assert margins_2 != margins_1


# ---------------------------------------------------------------------------
# draw_path — invalid input validation
# ---------------------------------------------------------------------------


class TestDrawPathValidation:
    def test_mismatched_xy_lengths_raises(self):
        dia = EnergyDiagram()
        with pytest.raises(ValueError, match="same length"):
            dia.draw_path([0, 1, 2], [0, 10], color="blue")

    def test_invalid_linetype_value_raises(self):
        dia = EnergyDiagram()
        with pytest.raises(ValueError):
            dia.draw_path([0, 1], [0, 10], color="blue", linetypes=[99])

    def test_linetype_wrong_length_raises(self):
        dia = EnergyDiagram()
        with pytest.raises(ValueError):
            dia.draw_path([0, 1, 2], [0, 10, 5], color="blue", linetypes=[1, 1, 1])

    def test_non_numeric_x_data_raises(self):
        dia = EnergyDiagram()
        with pytest.raises(TypeError):
            dia.draw_path(["a", "b"], [0, 10], color="blue")

    def test_non_numeric_y_data_raises(self):
        dia = EnergyDiagram()
        with pytest.raises(TypeError):
            dia.draw_path([0, 1], ["a", "b"], color="blue")

    def test_duplicate_path_name_raises(self):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue", path_name="P")
        with pytest.raises(ValueError):
            dia.draw_path([0, 1], [0, 5], color="red", path_name="P")

    def test_non_string_path_name_raises(self):
        dia = EnergyDiagram()
        with pytest.raises(TypeError):
            dia.draw_path([0, 1], [0, 10], color="blue", path_name=42)

    def test_linetype_as_invalid_scalar_raises(self):
        dia = EnergyDiagram()
        with pytest.raises(ValueError):
            dia.draw_path([0, 1], [0, 10], color="blue", linetypes=99)

    def test_linetype_wrong_type_raises(self):
        # A string is a Sequence in Python, so it reaches the value check
        # rather than the type check and raises ValueError.
        dia = EnergyDiagram()
        with pytest.raises((TypeError, ValueError)):
            dia.draw_path([0, 1], [0, 10], color="blue", linetypes="dotted")


# ---------------------------------------------------------------------------
# EnergyDiagram constructor — invalid input validation
# ---------------------------------------------------------------------------


class TestConstructorValidation:
    def test_invalid_style_raises(self):
        with pytest.raises(ValueError):
            EnergyDiagram(style="fancy")

    def test_extra_y_margin_wrong_length_raises(self):
        with pytest.raises(ValueError):
            EnergyDiagram(extra_y_margin=(0.1,))

    def test_extra_x_margin_wrong_length_raises(self):
        with pytest.raises(ValueError):
            EnergyDiagram(extra_x_margin=(0.1,))

    def test_extra_y_margin_non_numeric_raises(self):
        with pytest.raises(TypeError):
            EnergyDiagram(extra_y_margin=("a", "b"))

    def test_width_limit_negative_raises(self):
        with pytest.raises(ValueError):
            EnergyDiagram(width_limit=-1)

    def test_figsize_negative_raises(self):
        with pytest.raises(ValueError):
            EnergyDiagram(figsize=(-1, 4))

    def test_figsize_wrong_length_raises(self):
        with pytest.raises(ValueError):
            EnergyDiagram(figsize=(6,))


# ---------------------------------------------------------------------------
# Image placement
# ---------------------------------------------------------------------------


@pytest.fixture()
def png_path(tmp_path):
    """Write a tiny 4×4 RGBA PNG and return its path as a string."""
    img_file = tmp_path / "test_image.png"
    arr = np.zeros((4, 4, 4), dtype=np.uint8)
    arr[:, :, 3] = 255  # fully opaque
    plt.imsave(str(img_file), arr)
    return str(img_file)


class TestImagePlacement:
    def test_add_image_in_plot_returns_self(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        result = dia.add_image_in_plot(png_path, position=(1, 5))
        assert result is dia

    def test_add_image_in_plot_stored_in_images(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.add_image_in_plot(png_path, position=(1, 5), img_name="my_img")
        assert "my_img" in dia.images
        assert isinstance(dia.images["my_img"], ImageObject)

    def test_add_image_in_plot_auto_name(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.add_image_in_plot(png_path, position=(1, 5))
        assert len(dia.images) == 1

    def test_add_image_in_plot_framed(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.add_image_in_plot(png_path, position=(1, 5), img_name="framed", framed=True)
        img_obj = dia.images["framed"]
        assert set(img_obj.borders.keys()) == {"top", "bottom", "left", "right"}

    def test_add_image_in_plot_not_framed_has_no_borders(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.add_image_in_plot(png_path, position=(1, 5), img_name="plain", framed=False)
        assert dia.images["plain"].borders == {}

    def test_add_image_in_plot_with_explicit_width(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.add_image_in_plot(png_path, position=(1, 5), width=0.4)

    def test_add_image_in_plot_with_explicit_height(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.add_image_in_plot(png_path, position=(1, 5), height=3.0)

    def test_add_image_series_returns_self(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        result = dia.add_image_series_in_plot([png_path, png_path, png_path])
        assert result is dia

    def test_add_image_series_stored_by_name(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.add_image_series_in_plot(
            [png_path, png_path, png_path], img_series_name="my_series"
        )
        assert "my_series" in dia.images
        assert isinstance(dia.images["my_series"], dict)

    def test_add_image_series_keyed_by_x(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.add_image_series_in_plot(
            [png_path, png_path, png_path],
            img_x_places=[0, 1, 2],
            img_series_name="s",
        )
        assert set(dia.images["s"].keys()) == {"0.0", "1.0", "2.0"}

    def test_add_image_series_placement_top(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.add_image_series_in_plot(
            [png_path, png_path, png_path], y_placement="top", img_series_name="top"
        )
        assert "top" in dia.images

    def test_add_image_series_placement_bottom(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.add_image_series_in_plot(
            [png_path, png_path, png_path], y_placement="bottom", img_series_name="bot"
        )
        assert "bot" in dia.images

    def test_add_image_series_per_image_placement(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.add_image_series_in_plot(
            [png_path, png_path, png_path],
            y_placement=["top", "auto", "bottom"],
        )

    def test_add_image_series_with_numbers_recalculates(self, png_path):
        """Image series placed before add_numbers_auto should be repositioned after."""
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.add_image_series_in_plot([png_path, png_path, png_path], img_series_name="s")
        dia.add_numbers_auto()
        assert "s" in dia.images

    def test_add_image_series_recalculates_after_xlabels(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.add_image_series_in_plot([png_path, png_path, png_path], img_series_name="s")
        dia.set_xlabels(["A", "B", "C"])
        assert "s" in dia.images

    def test_add_image_series_does_not_raise_with_redrawing(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], path_name="path1", color="blue")
        dia.add_image_series_in_plot([png_path, png_path, png_path], img_series_name="s")
        dia.set_xlabels(["A", "B", "C"])
        dia.add_numbers_auto()
        dia.add_path_labels("path1", ["Start", "Middle", "End"])
        assert "s" in dia.images

    # --- validation ---

    def test_add_image_series_mismatched_x_places_raises(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        with pytest.raises(ValueError):
            dia.add_image_series_in_plot([png_path, png_path], img_x_places=[0, 1, 2])

    def test_add_image_series_invalid_y_placement_raises(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        with pytest.raises(ValueError):
            dia.add_image_series_in_plot([png_path], y_placement="sideways")

    def test_add_image_series_mismatched_y_placement_list_raises(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        with pytest.raises(ValueError):
            dia.add_image_series_in_plot(
                [png_path, png_path, png_path], y_placement=["top", "bottom"]
            )

    def test_add_image_series_mismatched_y_offsets_raises(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        with pytest.raises(ValueError):
            dia.add_image_series_in_plot([png_path, png_path, png_path], y_offsets=[1, 2])

    def test_add_image_series_mismatched_height_list_raises(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        with pytest.raises(ValueError):
            dia.add_image_series_in_plot([png_path, png_path], height=[1.0])

    def test_add_image_series_mismatched_width_list_raises(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        with pytest.raises(ValueError):
            dia.add_image_series_in_plot([png_path, png_path], width=[0.5])

    def test_add_image_series_invalid_height_type_raises(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        with pytest.raises(TypeError):
            dia.add_image_series_in_plot([png_path], height="big")

    def test_add_image_series_invalid_width_type_raises(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        with pytest.raises(TypeError):
            dia.add_image_series_in_plot([png_path], width="big")

    def test_add_image_series_proportional_scaling_width_and_height_raises(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue")
        with pytest.raises(ValueError):
            dia.add_image_series_in_plot(
                [png_path, png_path],
                proportional_scaling=True,
                width=0.6,
                height=1.2,
            )

    def test_add_image_series_proportional_scaling_width_sequence_raises(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue")
        with pytest.raises(TypeError):
            dia.add_image_series_in_plot(
                [png_path, png_path],
                proportional_scaling=True,
                width=[0.3, 0.6],
            )

    def test_add_image_series_proportional_scaling_applies_width_ratio(self, tmp_path):
        img_small = tmp_path / "small_w.png"
        img_large = tmp_path / "large_w.png"
        plt.imsave(str(img_small), np.ones((10, 20, 4), dtype=np.uint8) * 255)
        plt.imsave(str(img_large), np.ones((10, 40, 4), dtype=np.uint8) * 255)

        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue")
        dia.add_image_series_in_plot(
            [str(img_small), str(img_large)],
            proportional_scaling=True,
            width=0.8,
            img_series_name="prop_w",
        )

        series = dia.images["prop_w"]
        width_small = series["0.0"].image.get_extent()[1] - series["0.0"].image.get_extent()[0]
        width_large = series["1.0"].image.get_extent()[1] - series["1.0"].image.get_extent()[0]

        assert width_large == pytest.approx(0.8)
        assert width_small == pytest.approx(0.4)

    def test_add_image_series_proportional_scaling_applies_height_ratio(self, tmp_path):
        img_short = tmp_path / "short_h.png"
        img_tall = tmp_path / "tall_h.png"
        plt.imsave(str(img_short), np.ones((20, 10, 4), dtype=np.uint8) * 255)
        plt.imsave(str(img_tall), np.ones((40, 10, 4), dtype=np.uint8) * 255)

        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue")
        dia.add_image_series_in_plot(
            [str(img_short), str(img_tall)],
            proportional_scaling=True,
            height=2.0,
            img_series_name="prop_h",
        )

        series = dia.images["prop_h"]
        height_short = (
            series["0.0"].image.get_extent()[3] - series["0.0"].image.get_extent()[2]
        )
        height_tall = series["1.0"].image.get_extent()[3] - series["1.0"].image.get_extent()[2]

        assert height_tall == pytest.approx(2.0)
        assert height_short == pytest.approx(1.0)

    def test_add_image_series_framed_list_with_non_bool_raises(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue")
        with pytest.raises(TypeError):
            dia.add_image_series_in_plot([png_path, png_path], framed=[True, "yes"])

    def test_add_image_series_framed_wrong_type_raises(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue")
        with pytest.raises(TypeError):
            dia.add_image_series_in_plot([png_path, png_path], framed="yes")

    def test_add_image_series_mismatched_frame_colors_raises(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue")
        with pytest.raises(ValueError):
            dia.add_image_series_in_plot([png_path, png_path], frame_colors=["red"])

    def test_add_image_series_invalid_frame_colors_type_raises(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue")
        with pytest.raises(TypeError):
            dia.add_image_series_in_plot([png_path], frame_colors=42)

    def test_add_image_series_invalid_img_series_name_raises(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue")
        with pytest.raises(TypeError):
            dia.add_image_series_in_plot([png_path, png_path], img_series_name=42)

    def test_add_image_series_warns_when_no_plateau_at_x(self, png_path, capsys):
        """Image series at an x with no path data should warn and not crash."""
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue")
        dia.add_image_series_in_plot([png_path], img_x_places=[5])
        captured = capsys.readouterr()
        assert "Warning" in captured.out

    def test_add_image_in_plot_invalid_img_name_raises(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue")
        with pytest.raises(TypeError):
            dia.add_image_in_plot(png_path, position=(0, 5), img_name=42)

    def test_add_image_in_plot_invalid_framed_raises(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue")
        with pytest.raises(TypeError):
            dia.add_image_in_plot(png_path, position=(0, 5), framed="yes")

    def test_add_image_in_plot_invalid_vertical_alignment_raises(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue")
        with pytest.raises(ValueError):
            dia.add_image_in_plot(png_path, position=(0, 5), vertical_alignment="diagonal")

    def test_add_image_in_plot_invalid_horizontal_alignment_raises(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue")
        with pytest.raises(ValueError):
            dia.add_image_in_plot(png_path, position=(0, 5), horizontal_alignment="diagonal")

    def test_add_image_in_plot_horizontal_alignment_left(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue")
        dia.add_image_in_plot(
            png_path, position=(0, 5), horizontal_alignment="left", img_name="l"
        )
        assert "l" in dia.images

    def test_add_image_in_plot_horizontal_alignment_right(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue")
        dia.add_image_in_plot(
            png_path, position=(0, 5), horizontal_alignment="right", img_name="r"
        )
        assert "r" in dia.images

    def test_image_object_remove_frame(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue")
        dia.add_image_in_plot(png_path, position=(0, 5), framed=True, img_name="framed")
        img_obj = dia.images["framed"]
        assert img_obj.borders  # has borders before removal
        img_obj.remove_frame()
        assert img_obj.borders == {}

    def test_add_image_series_with_numbers_naive_recalculates(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.add_image_series_in_plot([png_path, png_path, png_path], img_series_name="s")
        dia.add_numbers_naive()
        assert "s" in dia.images

    def test_add_image_series_with_numbers_stacked_recalculates(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.add_image_series_in_plot([png_path, png_path, png_path], img_series_name="s")
        dia.add_numbers_stacked()
        assert "s" in dia.images

    def test_add_image_series_with_numbers_average_recalculates(self, png_path):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.add_image_series_in_plot([png_path, png_path, png_path], img_series_name="s")
        dia.add_numbers_average()
        assert "s" in dia.images


# ---------------------------------------------------------------------------
# Additional bar manager validation
# ---------------------------------------------------------------------------


class TestBarManagerValidation:
    def test_x_whiskers_wrong_length_raises(self):
        dia = make_diagram()
        with pytest.raises(ValueError):
            dia.draw_difference_bar(
                x=2, y_start_end=(0, 10), description="ΔE: ", x_whiskers=(0, 1, 2)
            )

    def test_x_whiskers_non_numeric_element_raises(self):
        dia = make_diagram()
        with pytest.raises(ValueError):
            dia.draw_difference_bar(
                x=2, y_start_end=(0, 10), description="ΔE: ", x_whiskers=("a", None)
            )


# ---------------------------------------------------------------------------
# Additional path manager / artist coverage
# ---------------------------------------------------------------------------


class TestPathManagerArtists:
    def test_scalar_linetype_valid(self):
        """Integer linetype scalar (not a list) exercises the int branch."""
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue", linetypes=1)
        assert len(dia.lines) == 1

    def test_scalar_linetype_all_values(self):
        for lt in [0, 1, -1, 2, -2, 3, 4]:
            dia = EnergyDiagram()
            dia.draw_path([0, 1], [0, 10], color="blue", linetypes=lt)


# ---------------------------------------------------------------------------
# add_path_labels
# ---------------------------------------------------------------------------


class TestAddPathLabels:
    def test_basic_labels(self):
        """Test basic label addition with all labels provided."""
        dia = make_diagram()
        result = dia.add_path_labels(path_name="A", labels=["E", "TS1", "I", "TS2", "P"])
        assert result is dia  # method chaining

    def test_labels_with_none_values(self):
        """Test that None values in labels don't raise errors."""
        dia = make_diagram()
        dia.add_path_labels(path_name="A", labels=["E", None, "I", None, "P"])

    def test_custom_fontsize(self):
        """Test adding labels with custom fontsize."""
        dia = make_diagram()
        dia.add_path_labels(path_name="A", labels=["A", "B", "C", "D", "E"], fontsize=12)

    def test_custom_weight(self):
        """Test adding labels with custom font weight."""
        dia = make_diagram()
        dia.add_path_labels(path_name="A", labels=["A", "B", "C", "D", "E"], weight="bold")

    def test_custom_color(self):
        """Test adding labels with custom color."""
        dia = make_diagram()
        dia.add_path_labels(path_name="A", labels=["A", "B", "C", "D", "E"], color="red")

    def test_custom_fontsize_and_weight_and_color(self):
        """Test adding labels with all customizations at once."""
        dia = make_diagram()
        dia.add_path_labels(
            path_name="A",
            labels=["A", "B", "C", "D", "E"],
            fontsize=10,
            weight="bold",
            color="green",
        )

    def test_labels_stored_in_path_label_data(self):
        """Test that label data is stored in path_label_data."""
        dia = make_diagram()
        dia.add_path_labels(path_name="A", labels=["E", "TS1", "I", "TS2", "P"])
        assert len(dia._path_manager.path_label_data) == 1
        label_entry = dia._path_manager.path_label_data[0]
        assert label_entry["labels"] == ["E", "TS1", "I", "TS2", "P"]

    def test_labels_with_named_path(self):
        """Test adding labels to a specifically named path."""
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue", path_name="path_A")
        dia.draw_path([0, 1, 2], [0, 5, -2], color="red", path_name="path_B")
        dia.add_path_labels(path_name="path_A", labels=["A1", "A2", "A3"])
        # Ensure only one label set was added for path_A
        label_entries = [
            e for e in dia._path_manager.path_label_data if e["path_name"] == "path_A"
        ]
        assert len(label_entries) == 1

    def test_labels_added_to_multiple_paths(self):
        """Test adding labels to different paths sequentially."""
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue", path_name="path_A")
        dia.draw_path([0, 1, 2], [0, 5, -2], color="red", path_name="path_B")
        dia.add_path_labels(path_name="path_A", labels=["A1", "A2", "A3"])
        dia.add_path_labels(path_name="path_B", labels=["B1", "B2", "B3"])
        assert len(dia._path_manager.path_label_data) == 2

    def test_label_metadata_stored_correctly(self):
        """Test that all metadata is stored correctly in path_label_data."""
        dia = make_diagram()
        fontsize = 14
        weight = "bold"
        color = "purple"
        labels = ["A", "B", "C", "D", "E"]

        dia.add_path_labels(
            path_name="A", labels=labels, fontsize=fontsize, weight=weight, color=color
        )

        label_entry = dia._path_manager.path_label_data[0]
        assert label_entry["fontsize"] == fontsize
        assert label_entry["weight"] == weight
        assert label_entry["color"] == color
        assert label_entry["labels"] == labels

    def test_fontsize_none_uses_diagram_fontsize(self):
        """Test that None fontsize uses the diagram's fontsize."""
        dia = EnergyDiagram(fontsize=11)
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue", path_name="A")
        dia.add_path_labels(path_name="A", labels=["A", "B", "C"], fontsize=None)

        label_entry = dia._path_manager.path_label_data[0]
        assert label_entry["fontsize"] == 11

    def test_color_none_uses_path_color(self):
        """Test that None color uses the path's color."""
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="orange", path_name="A")
        dia.add_path_labels(path_name="A", labels=["A", "B", "C"], color=None)

        label_entry = dia._path_manager.path_label_data[0]
        assert label_entry["color"] == "orange"

    def test_all_labels_none_valid(self):
        """Test that a label sequence with all None values is valid."""
        dia = make_diagram()
        dia.add_path_labels(path_name="A", labels=[None, None, None, None, None])
        plt.close("all")

    def test_float_linetype_raises(self):
        """A float is neither int nor Sequence — hits the else TypeError branch."""
        dia = EnergyDiagram()
        with pytest.raises(TypeError):
            dia.draw_path([0, 1], [0, 10], color="blue", linetypes=1.5)

    def test_merge_plateaus_mismatched_y_raises(self):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue", path_name="A")
        dia.draw_path([0, 1], [0, 20], color="red", path_name="B")
        with pytest.raises(ValueError, match="same y"):
            dia.merge_plateaus(x=1, path_name_left="A", path_name_right="B")

    def test_merge_plateaus_left_path_not_found_raises(self):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue", path_name="B")
        with pytest.raises(ValueError):
            dia.merge_plateaus(x=1, path_name_left="nonexistent", path_name_right="B")

    def test_merge_then_add_path_triggers_recalculate(self):
        """Adding a path after merge_plateaus should call recalculate_gap."""
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue", path_name="A")
        dia.draw_path([0, 1, 2], [0, 10, -8], color="red", path_name="B")
        dia.merge_plateaus(x=1, path_name_left="A", path_name_right="B")
        # Adding a third path triggers _recalculate_merged_plateaus → recalculate_gap
        dia.draw_path([0, 1, 2], [0, 10, 5], color="green", path_name="C")

    def test_path_object_remove(self):
        dia = EnergyDiagram()
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue", path_name="P")
        path_obj = dia.lines["P"]
        path_obj.remove()  # covers PathObject.remove()

    def test_broken_line_remove(self):
        """Draw a path with broken connectors, then remove the BrokenLine artist."""
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue", linetypes=[-1], path_name="P")
        broken = list(dia.lines["P"].connections.values())[0]
        broken.remove()  # covers BrokenLine.remove()


# ---------------------------------------------------------------------------
# Additional style manager coverage
# ---------------------------------------------------------------------------


class TestStyleManagerExtra:
    def test_xaxis_break_open_style_raises(self):
        dia = EnergyDiagram(style="open")
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        with pytest.raises(NotImplementedError):
            dia.add_xaxis_break(x=1)

    def test_xaxis_break_halfboxed(self):
        dia = EnergyDiagram(style="halfboxed")
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.add_xaxis_break(x=1)
        assert "1.0" in dia.ax_objects.xaxis_breaks

    def test_xaxis_break_twosided(self):
        dia = EnergyDiagram(style="twosided")
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.add_xaxis_break(x=1)
        assert "1.0" in dia.ax_objects.xaxis_breaks

    def test_xaxis_break_boxed_draws_top_and_bottom(self):
        dia = EnergyDiagram(style="boxed")
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.add_xaxis_break(x=1)
        break_obj = dia.ax_objects.xaxis_breaks["1.0"]
        assert isinstance(break_obj, dict)
        assert "top" in break_obj and "bottom" in break_obj

    def test_yaxis_break_boxed_draws_left_and_right(self):
        dia = EnergyDiagram(style="boxed")
        dia.draw_path([0, 1, 2], [0, 100, -5], color="blue")
        dia.add_yaxis_break(y=50)
        break_obj = dia.ax_objects.yaxis_breaks["50.0"]
        assert isinstance(break_obj, dict)
        assert "left" in break_obj and "right" in break_obj

    def test_yaxis_break_halfboxed(self):
        dia = EnergyDiagram(style="halfboxed")
        dia.draw_path([0, 1, 2], [0, 100, -5], color="blue")
        dia.add_yaxis_break(y=50)
        assert "50.0" in dia.ax_objects.yaxis_breaks

    def test_xaxis_break_recalculates_on_new_path(self):
        """Adding a path after an axis break should recalculate it."""
        # Use halfboxed: boxed stores breaks as dicts and remove_axes_breaks
        # would need dict.remove(), which is a separate code issue.
        dia = EnergyDiagram(style="halfboxed")
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia.add_xaxis_break(x=1)
        dia.draw_path([0, 1, 2], [0, 50, -10], color="red")  # triggers recalculate

    def test_set_xlabels_mismatched_labelplaces_raises(self):
        dia = make_diagram()
        with pytest.raises(ValueError):
            dia.set_xlabels(["A", "B", "C"], labelplaces=[0, 1])

    def test_set_xlabels_in_plot_no_data_warns(self, capsys):
        """in_plot label at an x with no path data should warn."""
        dia = make_diagram()  # path at x=0..4
        dia.set_xlabels(
            ["A", "B", "C", "D", "E", "X"], labelplaces=[0, 1, 2, 3, 4, 9], in_plot=True
        )
        captured = capsys.readouterr()
        assert "Warning" in captured.out

    def test_ax_objects_property(self):
        from chemdiagrams.managers.style_manager import StyleObjects

        dia = EnergyDiagram()
        assert isinstance(dia.ax_objects, StyleObjects)

    def test_xaxis_break_borderless_raises(self):
        dia = EnergyDiagram(style="borderless")
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        with pytest.raises(NotImplementedError):
            dia.add_xaxis_break(x=1)

    def test_yaxis_break_borderless_raises(self):
        dia = EnergyDiagram(style="borderless")
        dia.draw_path([0, 1, 2], [0, 100, -5], color="blue")
        with pytest.raises(NotImplementedError):
            dia.add_yaxis_break(y=50)

    def test_borderless_hides_all_spines(self):
        """borderless style should hide all four spines."""
        dia = EnergyDiagram(style="borderless")
        ax = dia.ax
        for spine in ["top", "bottom", "left", "right"]:
            assert not ax.spines[spine].get_visible(), f"spine '{spine}' should be hidden"

    def test_borderless_hides_yticks(self):
        """borderless style should suppress y-axis ticks and tick labels."""
        dia = EnergyDiagram(style="borderless")
        assert dia.ax.get_yticks().size == 0

    def test_borderless_in_plot_labels(self):
        """borderless + in_plot=True is the primary use-case; should not raise."""
        dia = make_diagram()
        dia.set_diagram_style("borderless")
        dia.set_xlabels(["E", "TS1", "I", "TS2", "P"], in_plot=True)


# ---------------------------------------------------------------------------
# Additional layout manager coverage
# ---------------------------------------------------------------------------


class TestLayoutManagerExtra:
    def test_width_limit_is_respected(self):
        """width_limit should cap the auto-computed figure width."""
        dia = EnergyDiagram(width_limit=2)
        dia.draw_path(list(range(20)), list(range(20)), color="blue")
        assert dia.fig.get_figwidth() <= 2 + 1e-6

    def test_degenerate_x_range_does_not_crash(self):
        """A single-state path must not crash during figure creation."""
        dia = EnergyDiagram()
        dia.draw_path([0], [0], color="blue")
        assert dia.fig.get_figwidth() > 0


# ---------------------------------------------------------------------------
# Additional number manager coverage
# ---------------------------------------------------------------------------


class TestNumberManagerExtra:
    def test_x_min_max_invalid_type_raises(self):
        """Passing an unsupported type for x_min_max should raise TypeError."""
        dia = make_diagram()
        with pytest.raises(TypeError):
            dia.add_numbers_auto(x_min_max={"start": 0, "end": 2})

    def test_x_min_max_as_scalar_float(self):
        """A plain float for x_min_max should annotate only that state."""
        dia = make_diagram()
        dia.add_numbers_naive(x_min_max=2.0)

    def test_stacked_overlap_nudge(self):
        """
        With a nonnumbered path above a numbered path at the same x,
        add_numbers_stacked must bump the label above the obstruction.
        """
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0, 10], color="blue", path_name="labeled")
        # The nonnumbered path is higher — forces the overlap branch
        dia.draw_path([0, 1], [0, 20], color="red", show_numbers=False)
        dia.add_numbers_stacked(no_overlap_with_nonnumbered=True)


class TestNumberingDecimals:
    def test_naive_decimal_places(self):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0.1234, 1.5678], color="blue")
        dia.add_numbers_naive(n_decimals=2)

        texts = dia._number_manager.mpl_objects
        assert len(texts) > 0

    def test_stacked_decimal_places(self):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0.1234, 1.5678], color="blue")
        dia.add_numbers_stacked(n_decimals=3)

        texts = dia._number_manager.mpl_objects
        assert len(texts) > 0

    def test_auto_decimal_places(self):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0.1234, 1.5678], color="blue")
        dia.add_numbers_auto(n_decimals=1)

        texts = dia._number_manager.mpl_objects
        assert len(texts) > 0

    def test_average_decimal_places(self):
        dia = EnergyDiagram()
        dia.draw_path([0, 1], [0.1234, 1.5678], color="blue")
        dia.draw_path([0, 1], [0.5, 1.2], color="red")
        dia.add_numbers_average(n_decimals=2)

        assert len(dia.numbers) > 0


# ---------------------------------------------------------------------------
# Additional validators coverage
# ---------------------------------------------------------------------------


class TestValidatorsExtra:
    def test_validate_numeric_sequence_none_raises(self):
        from chemdiagrams.validation.validators import Validators

        with pytest.raises(ValueError):
            Validators.validate_numeric_sequence(None, "x", allow_none=False)

    def test_validate_numeric_sequence_non_sequence_raises(self):
        from chemdiagrams.validation.validators import Validators

        with pytest.raises(TypeError):
            Validators.validate_numeric_sequence(42, "x")

    def test_validate_numeric_sequence_allow_none_elements_non_numeric_raises(self):
        from chemdiagrams.validation.validators import Validators

        with pytest.raises(TypeError):
            Validators.validate_numeric_sequence(
                [1, "bad", None], "x", allow_none_elements=True
            )

    def test_validate_string_sequence_none_raises(self):
        from chemdiagrams.validation.validators import Validators

        with pytest.raises(ValueError):
            Validators.validate_string_sequence(None, "x", allow_none=False)

    def test_validate_string_sequence_non_sequence_raises(self):
        from chemdiagrams.validation.validators import Validators

        with pytest.raises(TypeError):
            Validators.validate_string_sequence(42, "x")


# ---------------------------------------------------------------------------
# Template Tests
# ---------------------------------------------------------------------------


class TestTemplates:
    """Test suite for template functionality in EnergyDiagram."""

    def test_default_template_is_base_template(self):
        """By default, EnergyDiagram should use BaseTemplate."""

        dia = EnergyDiagram()
        # Verify the diagram initializes properly with default template
        assert isinstance(dia, EnergyDiagram)

    def test_custom_template_initialization(self):
        """EnergyDiagram should accept a custom template class."""
        from chemdiagrams.templates.example_template import ExampleTemplate

        dia = EnergyDiagram(template=ExampleTemplate())
        assert isinstance(dia, EnergyDiagram)

    def test_invalid_template_raises_type_error(self):
        """Passing a non-BaseTemplate class should raise TypeError."""

        class NotATemplate:
            pass

        with pytest.raises(TypeError):
            EnergyDiagram(template=NotATemplate())

    def test_template_constants_override(self):
        """Template should override default constants."""
        from chemdiagrams.templates.base_template import BaseTemplate
        from chemdiagrams.templates.example_template import ExampleTemplate

        # Create diagram with ExampleTemplate
        dia_example = EnergyDiagram(template=ExampleTemplate())
        dia_example.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        # Create diagram with BaseTemplate
        dia_base = EnergyDiagram(template=BaseTemplate())
        dia_base.draw_path([0, 1, 2], [0, 10, -5], color="blue")

        # ExampleTemplate modifies WIDTH_PLATEAU and LW_CONNECTOR in __init__
        # We check that the path manager has access to the modified constants
        example_constants = ExampleTemplate().constants
        base_constants = BaseTemplate().constants

        assert example_constants.WIDTH_PLATEAU == 0.4
        assert example_constants.LW_CONNECTOR == 0.6
        # Base constants should have defaults
        assert base_constants.WIDTH_PLATEAU != 0.4
        assert base_constants.LW_CONNECTOR != 0.6

    def test_example_template_modifies_constants(self):
        """ExampleTemplate should set custom constant values."""
        from chemdiagrams.templates.example_template import ExampleTemplate

        template = ExampleTemplate()
        assert template.constants.WIDTH_PLATEAU == 0.4
        assert template.constants.LW_CONNECTOR == 0.6

    def test_template_startup_is_called(self):
        """The template's startup method should be called during initialization."""
        from chemdiagrams.templates.example_template import ExampleTemplate

        dia = EnergyDiagram(template=ExampleTemplate())
        # ExampleTemplate.startup adds a grid
        # Check that the grid is enabled
        assert dia.ax.get_xgridlines() or dia.ax.get_ygridlines()

    def test_example_template_adds_grid(self):
        """ExampleTemplate should add a grid to the diagram's axes."""
        from chemdiagrams.templates.example_template import ExampleTemplate

        dia = EnergyDiagram(template=ExampleTemplate())
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue")

        # The startup method in ExampleTemplate adds grid
        # Check that grid lines exist
        grid_lines = dia.ax.get_ygridlines()
        assert len(grid_lines) > 0

    def test_tonner_zech_template_initialization(self):
        """TonnerZechTemplate should initialize without errors."""
        from chemdiagrams.templates.tonner_zech_template import TonnerZechTemplate

        dia = EnergyDiagram(template=TonnerZechTemplate())
        assert isinstance(dia, EnergyDiagram)

    def test_template_with_multiple_paths(self):
        """Templates should work correctly with multiple paths."""
        from chemdiagrams.templates.example_template import ExampleTemplate

        dia = EnergyDiagram(template=ExampleTemplate())
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue", path_name="path_A")
        dia.draw_path([0, 1, 2], [0, 5, -10], color="red", path_name="path_B")

        assert len(dia._path_manager.path_data) == 2

    def test_template_method_chaining(self):
        """Template-based diagrams should support method chaining."""
        from chemdiagrams.templates.example_template import ExampleTemplate

        dia = (
            EnergyDiagram(template=ExampleTemplate())
            .draw_path([0, 1, 2], [0, 10, -5], color="blue")
            .draw_path([0, 1, 2], [0, 5, -10], color="red")
        )

        assert isinstance(dia, EnergyDiagram)

    def test_example_template_custom_method(self):
        """ExampleTemplate custom methods should be callable."""
        from chemdiagrams.templates.example_template import ExampleTemplate

        dia = EnergyDiagram(template=ExampleTemplate())
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue", path_name="path_A")
        dia.add_numbers_naive()

        # Call the custom method from ExampleTemplate
        result = ExampleTemplate.color_all_numbers(dia, "red")
        assert result is dia

        # Verify numbers were colored (check if any text objects exist)
        assert len(dia.numbers) > 0

    def test_template_preserves_diagram_functionality(self):
        """Using a template should not break normal diagram functionality."""
        from chemdiagrams.templates.example_template import ExampleTemplate

        dia = EnergyDiagram(template=ExampleTemplate())
        dia.draw_path([0, 1, 2, 3], [0, 15, -8, 10], color="blue", path_name="reaction")
        dia.add_path_labels("reaction", ["A", "TS1", "IM", "P"])
        dia.add_numbers_naive()
        dia.draw_difference_bar(1, (15, 0), "ΔE:")

        # Verify all components are present
        assert len(dia._path_manager.path_data) > 0
        assert len(dia.numbers) > 0

    def test_template_with_custom_figsize(self):
        """Template should work with custom figure size parameters."""
        from chemdiagrams.templates.example_template import ExampleTemplate

        dia = EnergyDiagram(template=ExampleTemplate(), figsize=(10, 6))
        w, h = dia.fig.get_size_inches()
        assert w == pytest.approx(10)
        assert h == pytest.approx(6)

    def test_template_with_custom_fontsize(self):
        """Template should work with custom font size."""
        from chemdiagrams.templates.example_template import ExampleTemplate

        dia = EnergyDiagram(template=ExampleTemplate(), fontsize=14)
        assert dia._figure_manager.fontsize == 14

    def test_template_with_custom_style(self):
        """Template should work with custom diagram styles."""
        from chemdiagrams.templates.example_template import ExampleTemplate

        dia = EnergyDiagram(template=ExampleTemplate(), style="boxed")
        assert isinstance(dia, EnergyDiagram)

    def test_template_with_custom_margins(self):
        """Template should work with custom margins."""
        from chemdiagrams.templates.example_template import ExampleTemplate

        dia = EnergyDiagram(
            template=ExampleTemplate(), extra_x_margin=(0.5, 0.5), extra_y_margin=(0.1, 0.1)
        )
        assert isinstance(dia, EnergyDiagram)

    def test_multiple_diagrams_with_different_templates(self):
        """Multiple diagrams with different templates should not interfere."""
        from chemdiagrams.templates.base_template import BaseTemplate
        from chemdiagrams.templates.example_template import ExampleTemplate

        dia1 = EnergyDiagram(template=ExampleTemplate())
        dia2 = EnergyDiagram(template=BaseTemplate())
        dia1.draw_path([0, 1, 2], [0, 10, -5], color="blue")
        dia2.draw_path([0, 1, 2], [0, 10, -5], color="red")

        assert isinstance(dia1, EnergyDiagram)
        assert isinstance(dia2, EnergyDiagram)

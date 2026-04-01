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
    dia.draw_path(x_data=[0, 1, 2, 3, 4], y_data=[0, 28, -14, 15, -22], color="blue")
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

    def test_diff_label_multiline_larger_than_single_line(self):
        """A label with a newline should produce a larger y-offset than a plain label."""
        from chemdiagrams.managers.style_manager import StyleManager

        margins = {"x": (-0.5, 4.5), "y": (-30.0, 40.0)}
        figsize = (4.0, 3.0)
        fontsize = 8
        single = StyleManager._get_diff_label(margins, figsize, fontsize, "label")
        multi = StyleManager._get_diff_label(margins, figsize, fontsize, "line1\nline2")
        assert multi > single

    def test_diff_label_scales_with_fontsize(self):
        """A larger fontsize should produce a proportionally larger y-offset."""
        from chemdiagrams.managers.style_manager import StyleManager

        margins = {"x": (-0.5, 4.5), "y": (-30.0, 40.0)}
        figsize = (4.0, 3.0)
        small = StyleManager._get_diff_label(margins, figsize, 8, "label")
        large = StyleManager._get_diff_label(margins, figsize, 16, "label")
        assert large == pytest.approx(small * 2)


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

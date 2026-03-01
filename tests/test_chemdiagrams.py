"""
Tests for the chemdiagrams package.

Run with:
    pytest test_chemdiagrams.py

Or from the project root with the src layout:
    PYTHONPATH=src pytest test_chemdiagrams.py
"""

import matplotlib
import pytest

matplotlib.use("Agg")  # non-interactive backend — no display required

import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from chemdiagrams import EnergyDiagram

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

    @pytest.mark.parametrize("style", ["open", "boxed", "halfboxed", "twosided"])
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
        dia.draw_path([0, 1, 2], [0, 10, -5], color="blue",
                      path_name="hidden", show_numbers=False)
        path_info = dia._path_manager.path_data["hidden"]
        assert path_info["show_numbers"] is False

    def test_returns_self_for_chaining(self):
        dia = EnergyDiagram()
        result = (
            dia
            .draw_path([0, 1, 2], [0, 10, -5], color="blue")
            .draw_path([0, 1, 2], [0, 5, 0], color="red")
        )
        assert result is dia


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
        dia.set_xlabels(["E", "TS1", "I", "TS2", "P"],
                        labelplaces=[0, 1, 2, 3, 4])


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
        result = dia.draw_difference_bar(x=2.5, y_start_end=(-22, 28),
                                         description="ΔE: ")
        assert result is dia

    def test_bar_left_side(self):
        dia = make_diagram()
        dia.draw_difference_bar(x=0.5, y_start_end=(0, 28),
                                description="ΔE: ", left_side=True)

    def test_bar_no_auto_diff(self):
        dia = make_diagram()
        dia.draw_difference_bar(x=0.5, y_start_end=(0, 28),
                                description="ΔE = 28 kJ/mol",
                                add_difference=False)

    def test_bar_custom_color(self):
        dia = make_diagram()
        dia.draw_difference_bar(x=2.5, y_start_end=(-22, 28),
                                description="ΔE: ", color="red")

    def test_bar_whiskers(self):
        dia = make_diagram()
        dia.draw_difference_bar(x=2.5, y_start_end=(-22, 28),
                                description="ΔE: ",
                                x_whiskers=(0, 4))

    def test_bars_list_populated(self):
        dia = make_diagram()
        dia.draw_difference_bar(x=2.5, y_start_end=(-22, 28), description="ΔE: ")
        assert len(dia.bars) == 1


# ---------------------------------------------------------------------------
# Diagram styles
# ---------------------------------------------------------------------------

class TestDiagramStyle:
    @pytest.mark.parametrize("style", ["open", "boxed", "halfboxed", "twosided"])
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
        dia.draw_path([0, 1, 2, 3, 4], [0, 28, -14, 15, -22],
                      color="blue", path_name="Pathway A")
        dia.draw_path([0, 1, 2, 3, 4], [0, 20, -10, 12, -25],
                      color="red", path_name="Pathway B")
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

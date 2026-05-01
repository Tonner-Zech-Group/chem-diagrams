from __future__ import annotations

from collections.abc import Sequence

import numpy as np

from ..constants import Constants
from ..validation import Validators
from .difference_manager import DifferenceManager
from .figure_manager import FigureManager


class NumberManager:
    """
    Manages energy value annotations on the diagram.

    Provides four strategies for placing numeric labels above energy
    levels: naive (directly above each bar), stacked (vertically
    arranged), auto (distribution without collision), and average
    (one label per x-position showing the mean across paths).
    Rendered Text artists are stored in ``mpl_objects`` keyed by
    path name and x-coordinate.
    """

    def __init__(
        self,
        figure_manager: FigureManager,
        constants: Constants,
    ) -> None:
        self.figure_manager = figure_manager
        self.constants = constants
        self.mpl_objects: dict[str, dict] = {}
        self.numberings_added: list[dict] = []

    ############################################################
    # Main numbering methods
    ############################################################

    def add_numbers_naive(
        self,
        path_data: dict,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
        x_min_max: tuple[float, float] | list[float] | float | None = None,
        fontsize: int | None = None,
        n_decimals: int = 0,
    ) -> None:
        # Regularize x_min_max, fontsize and get all the numbers to plot
        x_min_max = NumberManager._regularize_x_min_max(x_min_max)
        values_to_print = NumberManager._get_all_visible_numbers(path_data, x_min_max)
        Validators.validate_number(fontsize, "fontsize", min_value=0, allow_none=True)
        Validators.validate_number(n_decimals, "n_decimals", min_value=0, only_integer=True)
        if fontsize is None:
            fontsize = self.figure_manager.fontsize

        # Plot the numbers
        for value_series in values_to_print:
            for i in range(len(value_series["x"])):
                number_to_print = [
                    {
                        "y": value_series["y"][i],
                        "color": value_series["color"],
                        "name": value_series["name"],
                    }
                ]
                self._print_stacked(
                    value_series["x"][i],
                    number_to_print,
                    value_series["y"][i],
                    margins,
                    figsize,
                    fontsize,
                    n_decimals,
                )
        self.numberings_added.append(
            {
                "type": self.add_numbers_naive,
                "x_min_max": x_min_max,
                "fontsize": fontsize,
            }
        )

    def add_numbers_stacked(
        self,
        path_data: dict,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
        path_mpl_objects: dict,
        x_min_max: tuple[float, float] | list[float] | float | None = None,
        fontsize: int | None = None,
        sort_by_energy: bool = True,
        no_overlap_with_nonnumbered: bool = True,
        n_decimals: int = 0,
    ) -> None:
        # Regularize x_min_max, fontsize and get all the numbers to plot
        x_min_max = NumberManager._regularize_x_min_max(x_min_max)
        values_to_print = NumberManager._get_all_visible_numbers(path_data, x_min_max)
        Validators.validate_number(fontsize, "fontsize", min_value=0, allow_none=True)
        Validators.validate_number(n_decimals, "n_decimals", min_value=0, only_integer=True)
        if fontsize is None:
            fontsize = self.figure_manager.fontsize

        # Get a list of all x values where to print
        x_places: list | np.ndarray = []
        for value_series in values_to_print:
            x_places = np.concatenate((x_places, np.array(value_series["x"])))
        x_places = np.unique(x_places)

        # For every step, get all energies, assign the colors and sort by energy
        # If sortenergy is True then print the numbers
        for x_current in x_places:
            numbers_to_stack = NumberManager._get_numbers_to_stack_at_x(
                values_to_print, x_current, sort_by_energy=sort_by_energy
            )

            # Find y where to print
            y_print_start = max(num["y"] for num in numbers_to_stack)
            if no_overlap_with_nonnumbered:
                all_numbers_at_x = NumberManager._get_all_values_at_x(path_data, x_current)
                higher_numbers_at_x = [val for val in all_numbers_at_x if val > y_print_start]
                while True:
                    no_overlap = NumberManager._check_no_overlap(
                        self.constants,
                        y_print_start,
                        numbers_to_stack,
                        higher_numbers_at_x,
                        margins,
                        figsize,
                        fontsize,
                        path_mpl_objects,
                        x_current,
                    )
                    if no_overlap:
                        break
                    if not higher_numbers_at_x:
                        print(f"Warning: Could not accurately place numbers at x={x_current}")
                        break
                    else:
                        y_print_start = higher_numbers_at_x[0]
                        higher_numbers_at_x = higher_numbers_at_x[1:]

            # Print the numbers
            self._print_stacked(
                x_current,
                numbers_to_stack,
                y_print_start,
                margins,
                figsize,
                fontsize,
                n_decimals,
            )
        self.numberings_added.append(
            {
                "type": self.add_numbers_stacked,
                "x_min_max": x_min_max,
                "fontsize": fontsize,
                "sort_by_energy": sort_by_energy,
                "no_overlap_with_nonnumbered": no_overlap_with_nonnumbered,
            }
        )

    def add_numbers_auto(
        self,
        path_data: dict,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
        path_mpl_objects: dict,
        x_min_max: tuple[float, float] | list[float] | float | None = None,
        fontsize: int | None = None,
        n_decimals: int = 0,
    ) -> None:
        # Regularize x_min_max, fontsize and get all the numbers to plot
        Validators.validate_number(fontsize, "fontsize", min_value=0, allow_none=True)
        Validators.validate_number(n_decimals, "n_decimals", min_value=0, only_integer=True)
        if fontsize is None:
            fontsize = self.figure_manager.fontsize
        x_min_max = NumberManager._regularize_x_min_max(x_min_max)
        values_to_print = NumberManager._get_all_visible_numbers(path_data, x_min_max)
        _, diff_per_step = DifferenceManager._get_number_diffs(
            self.constants, margins, figsize, fontsize
        )

        # Get a list of all x values where to print
        x_places: list | np.ndarray = []
        for value_series in values_to_print:
            x_places = np.concatenate((x_places, np.array(value_series["x"])))
        x_places = np.unique(x_places)

        # For every step, get all energies, assign the colors and sort by energy
        for x_current in x_places:
            numbers_to_stack = NumberManager._get_numbers_to_stack_at_x(
                values_to_print, x_current
            )
            # Start with lowest to print
            n_numbers_printed = 0
            y_last_printed = -np.inf
            all_numbers_at_x = NumberManager._get_all_values_at_x(path_data, x_current)
            while n_numbers_printed < len(numbers_to_stack):
                # Append to temporary list one number after each other
                numbers_to_stack_current = []
                numbers_to_stack_current.append(numbers_to_stack[n_numbers_printed])
                # Calulate where to try to print
                y_print_start = max(
                    numbers_to_stack[n_numbers_printed]["y"],
                    y_last_printed + diff_per_step,
                )
                # Append more numbers, if they have the same value
                start_index = len(numbers_to_stack_current) + n_numbers_printed
                numbers_to_check = numbers_to_stack[start_index:]
                for number in numbers_to_check:
                    if y_print_start >= number["y"]:
                        numbers_to_stack_current.append(number)
                # Determine every value greater than where to print
                higher_numbers_at_x = [val for val in all_numbers_at_x if val > y_print_start]
                # Increse print height, until no overlap
                while True:
                    no_overlap = NumberManager._check_no_overlap(
                        self.constants,
                        y_print_start,
                        numbers_to_stack_current,
                        higher_numbers_at_x,
                        margins,
                        figsize,
                        fontsize,
                        path_mpl_objects,
                        x_current,
                    )
                    if no_overlap or not higher_numbers_at_x:
                        if not no_overlap:
                            print(
                                f"Warning: Could not accurately place numbers at x={x_current}"
                            )
                        self._print_stacked(
                            x_current,
                            numbers_to_stack_current,
                            y_print_start,
                            margins,
                            figsize,
                            fontsize,
                            n_decimals,
                        )
                        y_last_printed = (
                            y_print_start + (len(numbers_to_stack_current) - 1) * diff_per_step
                        )
                        n_numbers_printed += len(numbers_to_stack_current)
                        break
                    else:
                        # Get next possible print height
                        y_print_start = higher_numbers_at_x[0]
                        # Append all numbers if they are on the print height
                        start_index = len(numbers_to_stack_current) + n_numbers_printed
                        numbers_to_check = numbers_to_stack[start_index:]
                        for number in numbers_to_check:
                            if y_print_start >= number["y"]:
                                numbers_to_stack_current.append(number)
                        # Determine new values above
                        higher_numbers_at_x = [
                            val for val in all_numbers_at_x if val > y_print_start
                        ]
        self.numberings_added.append(
            {
                "type": self.add_numbers_auto,
                "x_min_max": x_min_max,
                "fontsize": fontsize,
            }
        )

    def add_numbers_average(
        self,
        path_data: dict,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
        x_min_max: tuple[float, float] | list[float] | float | None = None,
        fontsize: int | None = None,
        color: str = "black",
        n_decimals: int = 0,
    ) -> None:
        # Regularize x_min_max, fontsize and get all the numbers to plot
        x_min_max = NumberManager._regularize_x_min_max(x_min_max)
        values_to_print = NumberManager._get_all_visible_numbers(path_data, x_min_max)
        Validators.validate_number(fontsize, "fontsize", min_value=0, allow_none=True)
        Validators.validate_number(n_decimals, "n_decimals", min_value=0, only_integer=True)
        if fontsize is None:
            fontsize = self.figure_manager.fontsize

        # Get a list of all x values where to print
        x_places: list | np.ndarray = []
        for value_series in values_to_print:
            x_places = np.concatenate((x_places, np.array(value_series["x"])))
        x_places = np.unique(x_places)

        # For every step, get all y values, average and print
        for x_current in x_places:
            numbers_to_stack = NumberManager._get_numbers_to_stack_at_x(
                values_to_print, x_current
            )
            numbers_to_stack_y = np.array([number["y"] for number in numbers_to_stack])
            y_avg = numbers_to_stack_y.mean()
            number_to_print = [
                {
                    "y": y_avg,
                    "color": color,
                    "name": "Average",
                }
            ]
            self._print_stacked(
                x_current,
                number_to_print,
                numbers_to_stack_y.max(),
                margins,
                figsize,
                fontsize,
                n_decimals,
            )
        self.numberings_added.append(
            {
                "type": self.add_numbers_average,
                "x_min_max": x_min_max,
                "fontsize": fontsize,
                "color": color,
            }
        )

    def _recalculate_numbers(
        self,
        path_data: dict,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
        path_mpl_objects: dict,
    ) -> None:
        # Remove all numbers from the plot
        for path_numbers in self.mpl_objects.values():
            for number in path_numbers.values():
                number.remove()
        self.mpl_objects = {}
        # Recalculate all numbers that have been added
        old_numberings = self.numberings_added.copy()
        self.numberings_added = []
        for numbering in old_numberings:
            settings = numbering.copy()
            del settings["type"]
            need_path_mpl_objects = numbering["type"] in [
                self.add_numbers_stacked,
                self.add_numbers_auto,
            ]
            if need_path_mpl_objects:
                settings["path_mpl_objects"] = path_mpl_objects
            numbering["type"](
                path_data=path_data,
                margins=margins,
                figsize=figsize,
                **settings,
            )

    def modify_number_values(
        self,
        path_data: dict,
        x: float,
        base_value: float = 0.0,
        x_add: float | list[float] | None = None,
        x_subtract: float | list[float] | None = None,
        include_paths: list[str] | None = None,
        exclude_paths: list[str] | None = None,
        brackets: tuple[str, str] | list[str] | None = ("(", ")"),
        n_decimals: int = 0,
    ) -> None:
        # Sanity checks
        Validators.validate_number(x, "x")
        Validators.validate_number(base_value, "base_value")
        if x_add is not None:
            if isinstance(x_add, (int, float)):
                x_add = [x_add]
        Validators.validate_numeric_sequence(x_add, "x_add", allow_none=True)
        if x_subtract is not None:
            if isinstance(x_subtract, (int, float)):
                x_subtract = [x_subtract]
        Validators.validate_numeric_sequence(x_subtract, "x_subtract", allow_none=True)
        Validators.validate_string_sequence(include_paths, "include_paths", allow_none=True)
        Validators.validate_string_sequence(exclude_paths, "exclude_paths", allow_none=True)
        if brackets is None:
            brackets = ("", "")
        Validators.validate_string_sequence(brackets, "brackets", required_length=2)
        Validators.validate_number(n_decimals, "n_decimals", min_value=0, only_integer=True)
        if include_paths is not None and exclude_paths is not None:
            raise ValueError("Cannot specify both include_paths and exclude_paths.")

        # Get all paths that should be modified
        if include_paths is not None:
            path_names_to_modify = set(include_paths)
        elif exclude_paths is not None:
            path_names_to_modify = set(path_data.keys()) - set(exclude_paths)
        else:
            path_names_to_modify = set(path_data.keys())

        # For each path modify the number at x and update the label
        for path_name in path_names_to_modify:
            try:
                path = path_data[path_name]
            except KeyError:
                raise ValueError(f"Path '{path_name}' not found in path_data.")
            try:
                label = self.mpl_objects[path_name][f"{x:.1f}"]
                is_label_found = True
            except KeyError:
                print(
                    f"Warning (modify_number_values): No label found for path"
                    f" '{path_name}' at x={x}. Skipping modification."
                )
                is_label_found = False

            if is_label_found:
                number_new = base_value

                # Add all the values at x position specified in x_subtract and x_add
                if x_add is not None:
                    for x_val in x_add:
                        try:
                            index = path["x"].index(x_val)
                            number_new += path_data[path_name]["y"][index]
                        except ValueError:
                            print(
                                f"Warning (modify_number_values): Value at x={x_val} not"
                                f" found for path. '{path_name}'. Skipping addition."
                            )

                if x_subtract is not None:
                    for x_val in x_subtract:
                        try:
                            index = path["x"].index(x_val)
                            number_new -= path_data[path_name]["y"][index]
                        except ValueError:
                            print(
                                f"Warning (modify_number_values): Value at x={x_val} not"
                                f" found for path. '{path_name}'. Skipping subtraction."
                            )

                # Update the label text
                new_text = f"{brackets[0]}{number_new:.{n_decimals}f}{brackets[1]}"
                new_text = new_text.replace("-", self.constants.MINUS_SIGN)
                label.set_text(new_text)

    ############################################################
    # Helper methods for number placement and overlap checking
    ############################################################

    @staticmethod
    def _regularize_x_min_max(
        x_min_max: tuple[float, float] | list[float] | float | None,
    ) -> tuple[float, float]:
        # Convert x_min_max to an inclusive interval
        if x_min_max is not None:
            if isinstance(x_min_max, (Sequence)):
                Validators.validate_numeric_sequence(x_min_max, "x_min_max", required_length=2)
                x_min_max_new = (x_min_max[0], x_min_max[1])
            elif isinstance(x_min_max, (int, float)):
                x_min_max_new = (x_min_max, x_min_max)
            else:
                raise TypeError(
                    "x_min_max must be a tuple or list with length 2 or a numeric value."
                )
        else:
            x_min_max_new = (-np.inf, np.inf)
        return x_min_max_new

    @staticmethod
    def _get_all_visible_numbers(
        path_data: dict, x_min_max: tuple[float, float]
    ) -> list[dict]:
        # Create new list of values which should be printed
        values_to_print = []
        for path_name, path in path_data.items():
            # Only select data [[x...],[y...],color] in interval if show_numbers=True
            if path["show_numbers"]:
                values_to_print.append(
                    {
                        "x": [
                            path["x"][i]
                            for i in range(len(path["x"]))
                            if x_min_max[0] <= path["x"][i] <= x_min_max[1]
                        ],
                        "y": [
                            path["y"][i]
                            for i in range(len(path["x"]))
                            if x_min_max[0] <= path["x"][i] <= x_min_max[1]
                        ],
                        "color": path["color"],
                        "name": path_name,
                    }
                )
        return values_to_print

    @staticmethod
    def _get_all_values_at_x(path_data: dict, x: float) -> list[float]:
        # Select y values at ax
        numbers_at_x = []
        for path in path_data.values():
            numbers_at_x += [path["y"][i] for i in range(len(path["x"])) if path["x"][i] == x]
        return sorted(numbers_at_x)

    @staticmethod
    def _get_numbers_to_stack_at_x(
        values_to_print: Sequence[dict], x_current: float, sort_by_energy: bool = True
    ) -> list[dict]:
        # Get all values to print at a given location x
        numbers_to_stack = []
        for value_series in values_to_print:
            if x_current in value_series["x"]:
                numbers_to_stack.append(
                    {
                        "y": value_series["y"][value_series["x"].index(x_current)],
                        "color": value_series["color"],
                        "name": value_series["name"],
                    }
                )
            if sort_by_energy:
                numbers_to_stack = sorted(numbers_to_stack, key=lambda x: x["y"])
        return numbers_to_stack

    def _print_stacked(
        self,
        x: float,
        numbers_to_stack: Sequence[dict],
        y_print_start: float,
        margins: dict[str, tuple],
        figsize: tuple[float, float],
        fontsize: int,
        n_decimals: int = 0,
    ) -> None:
        """
        Render a vertical stack of energy labels at a given x-position.

        Labels are placed starting at ``y_print_start`` plus ``diff_bias``,
        with each subsequent label offset upward by ``diff_per_step``. The
        resulting Text artists are saved into ``mpl_objects`` under their
        path name and x-coordinate key.
        """
        diff_bias, diff_per_step = DifferenceManager._get_number_diffs(
            self.constants, margins, figsize, fontsize
        )
        n_printed = 0
        for number in numbers_to_stack:
            number_obj = self.figure_manager.ax.text(
                x,
                (y_print_start + diff_bias + n_printed * diff_per_step),
                f"{number['y']:.{n_decimals}f}".replace("-", self.constants.MINUS_SIGN),
                ha="center",
                va="center",
                fontsize=fontsize,
                color=number["color"],
                zorder=self.constants.ZORDER_NUMBERS,
            )
            n_printed += 1
            if number["name"] not in self.mpl_objects:
                self.mpl_objects[number["name"]] = {}
            self.mpl_objects[number["name"]][f"{x:.1f}"] = number_obj

    @staticmethod
    def _check_no_overlap(
        constants: Constants,
        y_print_start: float,
        numbers_to_stack: Sequence[dict],
        higher_numbers_at_x: Sequence[float],
        margins: dict[str, tuple],
        figsize: tuple[float, float],
        fontsize: int,
        path_mpl_objects: dict,
        x: float,
    ) -> bool:
        """
        Return True if a proposed label stack would not collide with
        any higher plateaus or path labels.
        """
        no_number_overlap = NumberManager._check_no_plateau_overlap(
            constants=constants,
            y_print_start=y_print_start,
            numbers_to_stack=numbers_to_stack,
            higher_numbers_at_x=higher_numbers_at_x,
            margins=margins,
            figsize=figsize,
            fontsize=fontsize,
        )
        no_overlap_with_path_labels = NumberManager._check_no_overlap_with_path_labels(
            constants=constants,
            y_print_start=y_print_start,
            numbers_to_stack=numbers_to_stack,
            margins=margins,
            figsize=figsize,
            fontsize=fontsize,
            path_mpl_objects=path_mpl_objects,
            x=x,
        )
        return no_number_overlap and no_overlap_with_path_labels

    @staticmethod
    def _check_no_overlap_with_path_labels(
        constants: Constants,
        y_print_start: float,
        numbers_to_stack: Sequence[dict],
        margins: dict[str, tuple],
        figsize: tuple[float, float],
        fontsize: int,
        path_mpl_objects: dict,
        x: float,
    ) -> bool:
        """
        Return True if a proposed label stack would not collide with any path labels.

        Checks the vertical position of all path labels at the given x-coordinate
        and compares it to the proposed stack position. Returns True if there is no
        overlap, False otherwise.
        """
        diff_bias, diff_per_step = DifferenceManager._get_number_diffs(
            constants, margins, figsize, fontsize
        )
        stacked_offset = (len(numbers_to_stack) - 1) * diff_per_step
        base_offset = 2 * diff_bias
        y_stacked_max = y_print_start + base_offset + stacked_offset
        no_overlap_with_path_labels = True
        for path_obj in path_mpl_objects.values():
            try:
                label_obj = path_obj.labels[f"{x:.1f}"]
                label_fontsize = label_obj.get_fontsize()
                label_y = label_obj.get_position()[1]
                labeltext = label_obj.get_text()
                diff_to_label = DifferenceManager._get_diff_img_label(
                    constants, margins, figsize, label_fontsize, labeltext
                )
                has_collision = (
                    label_y - diff_to_label < y_stacked_max
                    and label_y + diff_to_label > y_print_start
                )
                if has_collision:
                    no_overlap_with_path_labels = False
            except KeyError:
                pass
        return no_overlap_with_path_labels

    @staticmethod
    def _check_no_plateau_overlap(
        constants: Constants,
        y_print_start: float,
        numbers_to_stack: Sequence[dict],
        higher_numbers_at_x: Sequence[float],
        margins: dict[str, tuple],
        figsize: tuple[float, float],
        fontsize: int,
    ) -> bool:
        """
        Return True if a proposed label stack would not collide with any higher plateaus.

        Computes the top edge of the stacked labels (including bias and
        per-step offsets) and checks that it falls below the nearest energy
        bar above ``y_print_start``. Returns True unconditionally if there
        are no higher bars.
        """
        diff_bias, diff_per_step = DifferenceManager._get_number_diffs(
            constants, margins, figsize, fontsize
        )
        stacked_offset = (len(numbers_to_stack) - 1) * diff_per_step
        base_offset = 2 * diff_bias
        y_stacked_max = y_print_start + base_offset + stacked_offset
        # Check if a bar collides
        min_higher = min(higher_numbers_at_x) if higher_numbers_at_x else float("inf")
        # Check if there are numbers at all
        no_higher_numbers = len(higher_numbers_at_x) == 0
        return y_stacked_max < min_higher or no_higher_numbers

from __future__ import annotations
from typing import TYPE_CHECKING

import numpy as np

from collections.abc import Sequence

from ..validation import Validators
from .. import constants
from . import FigureManager


class NumberManager:
    """
    NumberManager class for handling the Numbers

    """

    def __init__(
            self,
            figure_manager: FigureManager,
        ) -> None:
        self.figure_manager = figure_manager
        self.mpl_objects = {}

    ############################################################
    # Main numbering methods
    ############################################################

    def add_numbers_naive(
            self,
            path_data: dict,
            margins: dict[str, tuple],
            figsize: tuple[float, float], 
            x_min_max: tuple[float, float] | list[float] | float | None = None
        ) -> None:
        # Regularize x_min_max and get all the numbers to plot
        x_min_max = NumberManager._regularize_x_min_max(x_min_max)
        values_to_print = NumberManager._get_all_visible_numbers(path_data, x_min_max)

        # Plot the numbers
        for value_series in values_to_print:
            for i in range(len(value_series["x"])):
                number_to_print = [{
                    "y": value_series["y"][i],
                    "color": value_series["color"],
                    "name": value_series["name"],
                }]
                self._print_stacked(
                    value_series["x"][i],
                    number_to_print,
                    value_series["y"][i],
                    margins,
                    figsize,
                )

    def add_numbers_stacked(
            self,
            path_data: dict,
            margins: dict[str, tuple],
            figsize: tuple[float, float],  
            x_min_max: tuple[float, float] | list[float] | float | None = None, 
            sort_by_energy: bool = True, 
            no_overlap_with_nonnumbered: bool = True
        ) -> None:
        # Regularize x_min_max and get all the numbers to plot
        x_min_max = NumberManager._regularize_x_min_max(x_min_max)
        values_to_print = NumberManager._get_all_visible_numbers(path_data, x_min_max)

        # Get a list of all x values where to print
        x_places = []
        for value_series in values_to_print:
            x_places = np.concatenate((x_places, np.array(value_series["x"])))
        x_places = np.unique(x_places)
        
        # For every step, get all energies, assign the colors and sort by energy if sortenergy == True then, print the numbers
        for x_current in x_places:
            numbers_to_stack = NumberManager._get_numbers_to_stack_at_x(values_to_print, x_current, sort_by_energy=sort_by_energy)

            # Find y where to print
            y_print_start = max(num["y"] for num in numbers_to_stack)
            if no_overlap_with_nonnumbered:
                all_numbers_at_x = NumberManager._get_all_values_at_x(path_data, x_current)
                higher_numbers_at_x = [
                    val for val in all_numbers_at_x 
                    if val > y_print_start
                ]
                while True:
                    if NumberManager._check_no_number_overlap(y_print_start, numbers_to_stack, higher_numbers_at_x, margins, figsize):
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
                figsize
            )

    def add_numbers_auto(
            self,
            path_data: dict,
            margins: dict[str, tuple],
            figsize: tuple[float, float],  
            x_min_max: tuple[float, float] | list[float] | float | None = None,
        ) -> None:
        # Regularize x_min_max and get all the numbers to plot
        x_min_max = NumberManager._regularize_x_min_max(x_min_max)
        values_to_print = NumberManager._get_all_visible_numbers(path_data, x_min_max)
        _, diff_per_step = NumberManager._get_diffs(margins, figsize)

        # Get a list of all x values where to print
        x_places = []
        for value_series in values_to_print:
            x_places = np.concatenate((x_places, np.array(value_series["x"])))
        x_places = np.unique(x_places)
        
        # For every step, get all energies, assign the colors and sort by energy if sortenergy == True then, print the numbers
        for x_current in x_places:
            numbers_to_stack = NumberManager._get_numbers_to_stack_at_x(values_to_print, x_current)
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
                    y_last_printed + diff_per_step
                )
                # Append more numbers, if they have the same value
                for number in numbers_to_stack[len(numbers_to_stack_current)+n_numbers_printed:]:
                    if y_print_start >= number["y"]:
                        numbers_to_stack_current.append(number)
                # Determine every value greater than where to print
                higher_numbers_at_x = [
                    val for val in all_numbers_at_x 
                    if val > y_print_start
                ]
                # Increse print height, until no overlap
                while True:
                    if NumberManager._check_no_number_overlap(y_print_start, numbers_to_stack_current, higher_numbers_at_x, margins, figsize):
                        self._print_stacked(x_current, numbers_to_stack_current, y_print_start, margins, figsize)
                        y_last_printed = y_print_start + (len(numbers_to_stack_current) - 1) * diff_per_step
                        n_numbers_printed += len(numbers_to_stack_current)
                        break
                    else:
                        # Get next possible print height
                        y_print_start = higher_numbers_at_x[0]
                        # Append all numbers if they are on the print height
                        for number in numbers_to_stack[len(numbers_to_stack_current)+n_numbers_printed:]:
                            if y_print_start >= number["y"]:
                                numbers_to_stack_current.append(number)
                        # Determine new values above
                        higher_numbers_at_x = [
                            val for val in all_numbers_at_x 
                            if val > y_print_start
                        ]

    def add_numbers_average(
            self,
            path_data: dict,
            margins: dict[str, tuple],
            figsize: tuple[float, float],  
            x_min_max: tuple[float, float] | list[float] | float | None = None,
            color: str = "black"
        ) -> None:
        
        # Regularize x_min_max and get all the numbers to plot
        x_min_max = NumberManager._regularize_x_min_max(x_min_max)
        values_to_print = NumberManager._get_all_visible_numbers(path_data, x_min_max)

        # Get a list of all x values where to print
        x_places = []
        for value_series in values_to_print:
            x_places = np.concatenate((x_places, np.array(value_series["x"])))
        x_places = np.unique(x_places)
        
        # For every step, get all y values, average and print
        for x_current in x_places:
            numbers_to_stack = NumberManager._get_numbers_to_stack_at_x(values_to_print, x_current)
            numbers_to_stack_y = np.array([
                number["y"] for number in numbers_to_stack
            ])
            y_avg = numbers_to_stack_y.mean()
            number_to_print = [{
                "y": y_avg,
                "color": color,
                "name": "Average",
            }]
            self._print_stacked(
                x_current,
                number_to_print,
                numbers_to_stack_y.max(),
                margins,
                figsize,
            )


    ############################################################
    # Internal helper methods
    ############################################################
    
    @staticmethod
    def _get_diffs(
            margins: dict[str, tuple], 
            figsize: tuple[float, float],
        ) -> tuple[float, float]:
        diff_bias = (
            (margins["y"][1] - margins["y"][0])
            / figsize[1] 
            * constants.DISTANCE_NUMBER_LINE
        )
        diff_per_step = (
            (margins["y"][1] - margins["y"][0])
            / figsize[1] 
            * constants.DISTANCE_NUMBER_NUMBER
            )
        return diff_bias, diff_per_step

    @staticmethod
    def _regularize_x_min_max(
            x_min_max: tuple[float, float] | list[float] | float | None,                        
        ) -> tuple[float, float]:

        # Convert x_min_max to an inclusive interval
        if x_min_max is not None:
            if isinstance(x_min_max, (Sequence)):
                Validators.validate_numeric_sequence(x_min_max, "x_min_max", required_length=2)
            elif isinstance(x_min_max, (int, float)):
                x_min_max = (x_min_max, x_min_max)
            else:
                raise TypeError("x_min_max must be a tuple or list with length 2 or a numeric value.")
        else:
            x_min_max = (-np.inf, np.inf)
        return x_min_max

    @staticmethod
    def _get_all_visible_numbers(
            path_data: dict, 
            x_min_max: tuple[float, float]
        ) -> list[dict]:
        # Create new list of values which should be printed
        values_to_print = []
        for path_name, path in path_data.items():
            # Only select data [[x...],[y...],color] in interval if show_numbers=True 
            if path["show_numbers"] == True:
                values_to_print.append({
                    "x": [path["x"][i] for i in range(len(path["x"])) if x_min_max[0] <= path["x"][i] <= x_min_max[1]],
                    "y": [path["y"][i] for i in range(len(path["x"])) if x_min_max[0] <= path["x"][i] <= x_min_max[1]],
                    "color": path["color"],
                    "name": path_name,
                }) 
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
            values_to_print: Sequence[dict], 
            x_current: float, 
            sort_by_energy: bool = True
        ) -> list[dict]:
        # Get all values to print at a given location x
        numbers_to_stack = []
        for value_series in values_to_print:
            if x_current in value_series["x"]:
                numbers_to_stack.append({
                    "y": value_series["y"][value_series["x"].index(x_current)],
                    "color": value_series["color"],
                    "name": value_series["name"],
                })
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
        ) -> None:
        # Print a number stack
        diff_bias, diff_per_step = NumberManager._get_diffs(margins, figsize)
        n_printed = 0
        for number in numbers_to_stack:
            number_obj = self.figure_manager.ax.text(
                            x, 
                            (y_print_start 
                            + diff_bias + n_printed * diff_per_step), 
                            round(number["y"]), 
                            ha='center', 
                            va='center', 
                            fontsize=self.figure_manager.fontsize,
                            color=number["color"]
                            )
            n_printed += 1
            if not number["name"] in self.mpl_objects:
                self.mpl_objects[number["name"]] = {}
            self.mpl_objects[number["name"]][f"{x:.1f}"] = number_obj

    @staticmethod
    def _check_no_number_overlap(
            y_print_start: float, 
            numbers_to_stack: Sequence[dict], 
            higher_numbers_at_x: Sequence[float],
            margins: dict[str, tuple],
            figsize: tuple[float, float]
        ) -> bool:
        diff_bias, diff_per_step = NumberManager._get_diffs(margins, figsize)
        stacked_offset = (len(numbers_to_stack) - 1) * diff_per_step
        base_offset = 2 * diff_bias
        y_stacked_max = y_print_start + base_offset + stacked_offset
        # Check if a bar collides
        min_higher = min(higher_numbers_at_x) if higher_numbers_at_x else float("inf")
        # Check if there are numbers at all
        no_higher_numbers = len(higher_numbers_at_x) == 0
        return y_stacked_max < min_higher or no_higher_numbers
    
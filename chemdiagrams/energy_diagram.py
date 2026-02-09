import matplotlib.pyplot as plt
from matplotlib import font_manager
import matplotlib.patches as mpatches
import numpy as np



class EnergyDiagram:
    """
    EnergyDiagram class for plotting reaction energy figures conveniently

    """
    MAX_WIDTH = 7
    HEIGHT = 3
    X_SCALE = 0.8 # Inches per x-tick
    DISTANCE_TEXT_DIFFBAR = 0.02
    DISTANCE_NUMBER_LINE = 0.03
    DISTANCE_NUMBER_NUMBER = 0.045
    

    ############################################################
    # Methods for drawing the general plot
    ############################################################

    def __init__(self, extra_x_margin=(0,0), extra_y_margin=(-0.1,0.15), figsize=None, fontsize=8, verbose=False):
        # Sanity checks
        if figsize is not None:
            assert len(figsize) == 2, "figsize argument must contain two values (x_size,y_size)."
        assert len(extra_x_margin) == 2, "extra_x_margin argument must contain two values (extra_x_min_margin, extra_x_max_margin)."
        assert len(extra_y_margin) == 2, "extra_y_margin argument must contain two values (extra_y_min_margin, extra_y_max_margin)."
        
        # Save parameters in objext
        self.fontsize = fontsize
        self.verbose = verbose
        # Initialize path data dict and mpl objects
        self.path_data = {}
        self.mpl_objects = {}
        self.mpl_objects["lines"] = {}
        self.mpl_objects["numbers"] = {}
        self.mpl_objects["bars"] = {}
        self.mpl_objects["other"] = {}

        # Initialize the diagram, get the axis and set axis limits
        self.fig = plt.figure(dpi=150)
        self.ax = self.fig.gca()
        self.ax.tick_params(which='both', direction="inout", top=False, right=False, bottom=False)
        self.ax.tick_params(which='both',labelsize=fontsize)

        # Find figure size and assert right datatype of figsize
        self.extra_x_margin = extra_x_margin
        self.extra_y_margin = extra_y_margin
        self.figsize = figsize
        figsize = self._scale_figure()

        # Set diagram lines below and remove vertical lines
        self.ax.set_axisbelow(True)
        self.ax.xaxis.grid(False)
        self.ax.yaxis.grid(False)



    def set_xlabels(self, labels, labelplaces=None):
        # Create labelplace list if none given
        if labelplaces is None:
            labelplaces = list(range(len(labels)))
        assert len(labels) == len(labelplaces), "There must be the same number of labels and labelplaces."

        # Set labels at labelplaces
        self.ax.set_xticks(labelplaces)
        self.ax.set_xticklabels(labels)
       
        # Apply bold font to x-axis tick labels
        bold_font = font_manager.FontProperties(weight='bold', size=self.fontsize) #xlabels larger than normal font
        for label in self.ax.get_xticklabels():
            label.set_fontproperties(bold_font)

    def draw_difference_bar(self, x, y_start_end, description, diff=None,left_side=False,fontsize=None, color="black"):
        # Drawing a vertical difference bar
        # Diff is the distance between the bar and the text
        assert len(y_start_end) == 2, "y_start_end argument must contain two values (y_start, y_end)."
        y_start, y_end = y_start_end
        if fontsize == None:
            fontsize = self.fontsize

        # Scale plot before drawing
        self._adjust_xy_limits()

        # Automatic scaling of diff
        if diff == None:
            diff = EnergyDiagram.DISTANCE_TEXT_DIFFBAR
            diff *= (self.ax.get_xlim()[1] + 0.5 + self.extra_x_margin[1]
                     - (self.ax.get_xlim()[0] + 0.5 + self.extra_x_margin[0]) )
            diff /= (self.fig.get_figwidth())
        
        # Adjust diff and ha to side
        if left_side:
            diff *= -1
            horizontal_alignment = "right"
        else:
            horizontal_alignment = "left"

        # Draw vertical bar
        bar = self.ax.annotate(
                    '', 
                    xy=(x, y_end), 
                    xytext=(x, y_start), 
                    arrowprops=dict(
                        arrowstyle='|-|', 
                        color=color, 
                        lw=0.7, 
                        shrinkA=0, #no whitespace above and below the Bar
                        shrinkB=0, #no whitespace above and below the Bar
                        mutation_scale=3 #scaling of the horizontal caps
                                                )
                )
                   
        # Draw text next to bar 
        text = self.ax.text(
                    x+diff, (y_start+y_end)/2,  # Adjust the x and y coordinates for text placement
                    description + str(round(y_end-y_start)),  # Text to display
                    ha=horizontal_alignment, va='center', fontsize=fontsize, color=color, 
                )

        # Save into mpl_objects dict
        bar_nr = len(self.mpl_objects["bars"]) + 1
        self.mpl_objects["bars"][bar_nr] = {
            "bar": bar,
            "text": text,
        }

    def draw_path(self, x_data, y_data, color, linetypes=None, path_name=None, show_numbers=True):
        # Create linetype information if not given
        if linetypes is None:
            linetypes = [1]*(len(y_data)-1)
        
        # Sanity checks
        assert len(x_data) == len(y_data), f"Number of x positions (right now {len(x_data)}) must equal the number of y positions (right now {len(y_data)})."
        assert len(y_data) == len(linetypes) + 1, f"Length of linetypes + 1 (right now {len(linetypes)} + 1) must equal the number of data points (right now {len(x_data)})."
        assert type(show_numbers) == bool, f"show_numbers must be of type: bool"
        assert type(path_name) == str or path_name is None, f"path_name must be of type: str or None"
        assert path_name not in list(self.path_data.keys()), f"path_name must not already exist."

        # Save data for numbering or legend
        has_label = True
        if path_name is None:
            has_label = False
            path_name = f"__NONAME{len(self.path_data)}"
        self.path_data[path_name] = {
            "x": x_data, 
            "y": y_data, 
            "color": color, 
            "has_label": has_label, 
            "show_numbers": show_numbers,
        }

        # Initialize nested dics
        self.mpl_objects["lines"][path_name] = {
            "connections": {},
            "plateaus": {}
        }
        self.mpl_objects["numbers"][path_name] = {}

        # Create lists in order to draw the lines
        x_corners = []
        y_corners = []
        linetypes = linetypes

        # Draw the lines
        for i, v in enumerate(y_data):
            x_corners.append(x_data[i]-0.25)
            x_corners.append(x_data[i]+0.25)
            y_corners.append(y_data[i])
            y_corners.append(y_data[i])
            plateau = self.ax.hlines(v, x_data[i]-0.25, x_data[i]+0.25, zorder=1, lw=1.8, color=color, capstyle='round')
            self.mpl_objects["lines"][path_name]["plateaus"][f"{x_data[i]}"] = plateau
            if i > 0:
                if linetypes[i-1] == 1:
                    connector = self._draw_line(x_corners[-3:-1],y_corners[-3:-1], color)
                elif linetypes[i-1] == 0:
                    connector = self._draw_broken_line(x_corners[-3:-1],y_corners[-3:-1], color)
                else:
                    print("Warning: Invalid linetype argument in position " + str(i) + ":" + str(linetypes[i]))
                self.mpl_objects["lines"][path_name]["connections"][f"{sum(x_corners[-3:-1]) / 2:.1f}"] = connector

        # Automatically adjust axis limits
        self._scale_figure()

    def legend(self, loc="best", fontsize=None):
        if fontsize is None:
            fontsize = self.fontsize
        patches = []
        for path_name, path_info in self.path_data.items():
            if path_info["has_label"]:
                patches.append(mpatches.Patch(color=path_info["color"], label=path_name))
        self.ax.legend(handles=patches, fontsize=fontsize, loc=loc)

    def show(self):
        figsize = self._scale_figure()
        if self.verbose == True:
            print("Figure size is is " + str(round(figsize[0],2)) + " x " + str(round(figsize[1],2)) + " inches.")
        plt.show()


    ############################################################
    # Internal helper functions for general plot drawing
    ############################################################

    def _scale_figure(self):
        # Scale only, if no figure size is predetermined
        if self.figsize is None:
            # Function for scaling the figure automatically
            self._adjust_xy_limits()

            # Determine and set width
            x_size = EnergyDiagram.X_SCALE*(self.ax.get_xlim()[1]-self.ax.get_xlim()[0])
            if x_size > EnergyDiagram.MAX_WIDTH:
                x_size = EnergyDiagram.MAX_WIDTH
            elif x_size <= 0: # Avoid a figure without size
                x_size = 1
            self.fig.set_figwidth(x_size)

            # Determine and set height
            y_size = EnergyDiagram.HEIGHT
            if y_size > x_size:
                y_size = x_size  # Avoid ugly diagrams
            self.fig.set_figheight(y_size)
            return (x_size, y_size)
        
        else:
            self._adjust_xy_limits()
            self.fig.set_figwidth(self.figsize[0])
            self.fig.set_figheight(self.figsize[1])
            return self.figsize[:]
        
    def _adjust_xy_limits(self):
        # Get all x and y values out of the path data dictionary
        x_all = [
                element
                for path in self.path_data.values()
                if path and len(path) > 0
                for element in path["x"]
            ]
        y_all = [
                element
                for path in self.path_data.values()
                if path and len(path) > 0
                for element in path["y"]
            ]
        # Add values if no path was added yet to avoid errors
        if len(x_all) == 0:
            x_all = [0]
        if len(y_all) == 0:
            y_all = [0,10]

        # Adjust the axis limits
        self.ax.set_xlim([
            min(x_all)-0.5+self.extra_x_margin[0], 
            max(x_all)+0.5+self.extra_x_margin[1]
        ])
        self.ax.set_ylim([
            min(y_all) + (max(y_all)-min(y_all)) * self.extra_y_margin[0], 
            max(y_all) + (max(y_all)-min(y_all)) * self.extra_y_margin[1]
        ])

    def _draw_broken_line(self, x_coords, y_coords, color):
        # Portion of the line that has a gap
        linegap = 0.2 
        # Ensure tuples are converted to list
        x_coords = list(x_coords)
        y_coords = list(y_coords)

        # Draw first part of line
        x1 = x_coords.copy()
        y1 = y_coords.copy()
        x1[1] = x1[0] + (x1[1]-x1[0])*(0.5-linegap/2)
        y1[1] = y1[0] + (y1[1]-y1[0])*(0.5-linegap/2)
        line_1 = self.ax.plot(x1, y1, zorder=0, ls=':', lw=1.2, color=color)

        # Draw second part of line
        x2 = x_coords.copy()
        y2 = y_coords.copy()
        x2[0] = x2[0] + (x2[1]-x2[0])*(0.5+linegap/2)
        y2[0] = y2[0] + (y2[1]-y2[0])*(0.5+linegap/2)
        line_2 = self.ax.plot(x2, y2, zorder=1, ls=':', lw=1.2, color=color)

        # Draw small orthogonal lines
        stopper_1 = self.ax.annotate('', xy=(x1[1], y1[1]), xytext=(x1[1]+0.001*(x2[0]-x1[1]), y1[1]+0.001*(y2[0]-y1[1])), 
                arrowprops=dict(arrowstyle='|-|', color=color, lw=0.9, shrinkA=15, shrinkB=15, mutation_scale=3,zorder=1)
        )
        stopper_2 = self.ax.annotate('', xy=(x2[0], y2[0]), xytext=(x2[0]-0.001*(x2[0]-x1[1]), y2[0]-0.001*(y2[0]-y1[1])), 
                arrowprops=dict(arrowstyle='|-|', color=color, lw=0.9, shrinkA=15, shrinkB=15, mutation_scale=3,zorder=1)
        )
        return {
            "line_part_1": line_1[0],
            "line_part_2": line_2[0],
            "stopper_1": stopper_1,
            "stopper_2": stopper_2
        }

    def _draw_line(self, x_coords, y_coords, color):
        return self.ax.plot(x_coords, y_coords, zorder=1, ls=':', lw=1.2, color=color)[0]

    ############################################################
    # Methods for plotting numbers
    ############################################################
    
    def add_numbers_naive(self, x_min_max=None):
        # Regularize x_min_max and get all the numbers to plot
        x_min_max = EnergyDiagram._regularize_x_min_max(x_min_max)
        values_to_print = self._get_all_visible_numbers(x_min_max)
        
        # Update axis limits before numbers and calculate ydifference 
        self._adjust_xy_limits()
        diff = (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * EnergyDiagram.DISTANCE_NUMBER_LINE

        # Plot the numbers
        for value_series in values_to_print:
            for i in range(len(value_series["x"])):
                self.ax.text(
                    value_series["x"][i], 
                    value_series["y"][i]+diff, 
                    round(value_series["y"][i]),
                    ha='center', 
                    va='center', 
                    fontsize=self.fontsize, 
                    color=value_series["color"]
                )

    def add_numbers_stacked(self, x_min_max=None, sort_by_energy=True, no_overlap_with_nonnumbered=True):
        # Regularize x_min_max and get all the numbers to plot
        x_min_max = EnergyDiagram._regularize_x_min_max(x_min_max)
        values_to_print = self._get_all_visible_numbers(x_min_max)

        # Get a list of all x values where to print
        x_places = []
        for value_series in values_to_print:
            x_places = np.concatenate((x_places, np.array(value_series["x"])))
        x_places = np.unique(x_places)
        
        # For every step, get all energies, assign the colors and sort by energy if sortenergy == True then, print the numbers
        for x_current in x_places:
            numbers_to_stack = self._get_numbers_to_stack_at_x(values_to_print, x_current, sort_by_energy=sort_by_energy)

            # Find y where to print
            y_print_start = max(num["y"] for num in numbers_to_stack)
            if no_overlap_with_nonnumbered:
                all_numbers_at_x = self._get_all_values_at_x(x_current)
                higher_numbers_at_x = [
                    val for val in all_numbers_at_x 
                    if val > y_print_start
                ]
                while True:
                    if self._check_no_number_overlap(y_print_start, numbers_to_stack, higher_numbers_at_x):
                        break
                    else:
                        y_print_start = higher_numbers_at_x[0]
                        higher_numbers_at_x = higher_numbers_at_x[1:]

            # Print the numbers
            self._print_stacked(x_current, numbers_to_stack, y_print_start)

    def add_numbers_auto(self, x_min_max=None):
        # Regularize x_min_max and get all the numbers to plot
        x_min_max = EnergyDiagram._regularize_x_min_max(x_min_max)
        values_to_print = self._get_all_visible_numbers(x_min_max)
        self._adjust_xy_limits()
        diff_per_step = (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * EnergyDiagram.DISTANCE_NUMBER_NUMBER

        # Get a list of all x values where to print
        x_places = []
        for value_series in values_to_print:
            x_places = np.concatenate((x_places, np.array(value_series["x"])))
        x_places = np.unique(x_places)
        
        # For every step, get all energies, assign the colors and sort by energy if sortenergy == True then, print the numbers
        for x_current in x_places:
            numbers_to_stack = self._get_numbers_to_stack_at_x(values_to_print, x_current)
            # Start with lowest to print
            n_numbers_printed = 0
            y_last_printed = -np.inf
            all_numbers_at_x = self._get_all_values_at_x(x_current)
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
                    if self._check_no_number_overlap(y_print_start, numbers_to_stack_current, higher_numbers_at_x):
                        self._print_stacked(x_current, numbers_to_stack_current, y_print_start)
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

    ############################################################
    # Internal helper functions for plotting numbers
    ############################################################
            
    @staticmethod
    def _regularize_x_min_max(x_min_max):
        # Convert x_min_max to an inclusive interval
        if x_min_max is not None:
            if not type(x_min_max) == int:
                assert len(x_min_max) == 2, "x_min_max can only contain two entries (x_start, y_end)."
        if x_min_max is None:
            x_min_max = (-np.inf, np.inf)
        elif type(x_min_max) == int:
            x_min_max = (x_min_max, x_min_max) 
        return x_min_max

    def _get_all_visible_numbers(self, x_min_max):
        # Create new list of values which should be printed
        values_to_print = []
        for path_name, path in self.path_data.items():
            # Only select data [[x...],[y...],color] in interval if show_numbers=True 
            if path["show_numbers"] == True:
                values_to_print.append({
                    "x": [path["x"][i] for i in range(len(path["x"])) if x_min_max[0] <= path["x"][i] <= x_min_max[1]],
                    "y": [path["y"][i] for i in range(len(path["x"])) if x_min_max[0] <= path["x"][i] <= x_min_max[1]],
                    "color": path["color"],
                    "name": path_name,
                }) 
        return values_to_print

    def _get_all_values_at_x(self, x):
        # Select y values at ax
        numbers_at_x = []
        for path in self.path_data.values():
            numbers_at_x += [path["y"][i] for i in range(len(path["x"])) if path["x"][i] == x]
        return sorted(numbers_at_x)
    
    def _get_numbers_to_stack_at_x(self, values_to_print, x_current, sort_by_energy=True):
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
    
    def _print_stacked(self, x, numbers_to_stack, y_print_start):
        # Print a number stack
        self._adjust_xy_limits()
        diff_bias = (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * EnergyDiagram.DISTANCE_NUMBER_LINE
        diff_per_step = (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * EnergyDiagram.DISTANCE_NUMBER_NUMBER
        n_printed = 0
        for number in numbers_to_stack:
            number_obj = self.ax.text(
                            x, 
                            (y_print_start 
                            + diff_bias + n_printed * diff_per_step), 
                            round(number["y"]), 
                            ha='center', 
                            va='center', 
                            fontsize=self.fontsize,
                            color=number["color"]
                            )
            n_printed += 1
            self.mpl_objects["numbers"][number["name"]][f"{int(x)}"] = number_obj

    def _check_no_number_overlap(self, y_print_start, numbers_to_stack, higher_numbers_at_x):
        #Check wheter a number stack overlaps
        self._adjust_xy_limits()
        diff_bias = (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * EnergyDiagram.DISTANCE_NUMBER_LINE
        diff_per_step = (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * EnergyDiagram.DISTANCE_NUMBER_NUMBER
        stacked_offset = (len(numbers_to_stack) - 1) * diff_per_step
        base_offset = 2 * diff_bias
        y_stacked_max = y_print_start + base_offset + stacked_offset
        # Check if a bar collides
        min_higher = min(higher_numbers_at_x) if higher_numbers_at_x else float("inf")
        # Check if there are numbers at all
        no_higher_numbers = len(higher_numbers_at_x) == 0
        return y_stacked_max < min_higher or no_higher_numbers

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
    # Functions for drawing the general plot
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
        # Initialize path data dict
        self.path_data = {}

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

    def draw_difference_bar(self, x, y_start_end, description, diff=None,left_side=False,fontsize=None):
        # Drawing a vertical difference bar
        # Diff is the distance between the bar and the text
        assert len(y_start_end) == 2, "y_start_end argument must contain two values (y_start, y_end)."
        y_start, y_end = y_start_end

        # Scale plot before drawing
        self._adjust_xy_limits()

        # Automatic scaling of diff
        if diff == None:
            diff = EnergyDiagram.DISTANCE_TEXT_DIFFBAR
            diff *= (self.ax.get_xlim()[1] + 0.5 + self.extra_x_margin[1]
                     - (self.ax.get_xlim()[0] + 0.5 + self.extra_x_margin[0]) )
            diff /= (self.fig.get_figwidth())
        
        # Extract parameters
        if fontsize == None:
            fontsize = self.fontsize
        
        # Adjust diff and ha to side
        if left_side:
            diff *= -1
            horizontal_alignment = "right"
        else:
            horizontal_alignment = "left"

        # Draw vertical bar
        self.ax.annotate('', xy=(x, y_end), xytext=(x, y_start), 
                        arrowprops=dict(arrowstyle='|-|', color='black', lw=0.7, 
                                        shrinkA=0, shrinkB=0, #no whitespace above and below the Bar
                                        mutation_scale=3 #scaling of the horizontal caps
                                        )
                        )           
        # Draw text next to bar 
        self.ax.text(
                    x+diff, (y_start+y_end)/2,  # Adjust the x and y coordinates for text placement
                    description + str(round(y_end-y_start)),  # Text to display
                    ha=horizontal_alignment, va='center', fontsize=fontsize, color='black', 
                    )

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
                        max(x_all)+0.5+self.extra_x_margin[1]])
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
        self.ax.plot(x1, y1, zorder=0, ls=':', lw=1.2, color=color)

        # Draw second part of line
        x2 = x_coords.copy()
        y2 = y_coords.copy()
        x2[0] = x2[0] + (x2[1]-x2[0])*(0.5+linegap/2)
        y2[0] = y2[0] + (y2[1]-y2[0])*(0.5+linegap/2)
        self.ax.plot(x2, y2, zorder=1, ls=':', lw=1.2, color=color)

        # Draw small orthogonal lines
        self.ax.annotate('', xy=(x1[1], y1[1]), xytext=(x1[1]+0.001*(x2[0]-x1[1]), y1[1]+0.001*(y2[0]-y1[1])), 
                arrowprops=dict(arrowstyle='|-|', color=color, lw=0.9, shrinkA=15, shrinkB=15, mutation_scale=3,zorder=1)
        )
        self.ax.annotate('', xy=(x2[0], y2[0]), xytext=(x2[0]-0.001*(x2[0]-x1[1]), y2[0]-0.001*(y2[0]-y1[1])), 
                arrowprops=dict(arrowstyle='|-|', color=color, lw=0.9, shrinkA=15, shrinkB=15, mutation_scale=3,zorder=1)
        )

    def _draw_line(self, x_coords, y_coords, color):
        self.ax.plot(x_coords, y_coords, zorder=1, ls=':', lw=1.2, color=color)

    def draw_path(self, x_data, y_data, color, linetypes=None, path_name=None, show_numbers=True):
        # Create linetype information if not given
        if linetypes is None:
            linetypes = [1]*(len(y_data)-1)
        
        # Sanity checks
        assert len(x_data) == len(y_data), f"Number of x positions (right now {len(x_data)}) must equal the number of y positions (right now {len(y_data)})."
        assert len(y_data) == len(linetypes) + 1, f"Length of linetypes + 1 (right now {len(linetypes)} + 1) must equal the number of data points (right now {len(x_data)})."
        assert type(show_numbers) == bool, f"show_numbers must be of type: bool"
        assert type(path_name) == str, f"path_name must be of type: str"
        assert path_name not in list(self.path_data.keys()), f"path_name must not already exist."

        # Save data for numbering or legend or 
        if path_name is not None or show_numbers == True:
            self.path_data[path_name if path_name else f"__NONAME{len(self.path_data)}"] = {
                                                                                "x": x_data, 
                                                                                "y": y_data, 
                                                                                "color": color, 
                                                                                "has_label": bool(path_name), 
                                                                                "show_numbers": show_numbers,
                                                                                }
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
            self.ax.hlines(v, x_data[i]-0.25, x_data[i]+0.25, zorder=1, lw=1.8, color=color, capstyle='round')
            if i > 0:
                if linetypes[i-1] == 1:
                    self._draw_line(x_corners[-3:-1],y_corners[-3:-1], color)
                elif linetypes[i-1] == 0:
                    self._draw_broken_line(x_corners[-3:-1],y_corners[-3:-1], color)
                else:
                    print("Warning: Invalid linetype argument in position " + str(i) + ":" + str(linetypes[i]))
        
        # Automatically adjust axis limits
        self._adjust_xy_limits()

    def show(self):
        figsize = self._scale_figure()
        if self.verbose == True:
            print("Figure size is is " + str(round(figsize[0],2)) + " x " + str(round(figsize[1],2)) + " inches.")
        plt.show()


    ############################################################
    # Functions for plotting numbers
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

    def _get_visible_numbers(self, x_min_max):
        # Create new list of values which should be printed
        values_to_print = []
        for path in self.path_data.values():
            # Only select data [[x...],[y...],color] in interval if show_numbers=True 
            if path["show_numbers"] == True:
                values_to_print.append({
                                        "x": [path["x"][i] for i in range(len(path["x"])) if path["x"][i] >= x_min_max[0] and path["x"][i] <= x_min_max[1]],
                                        "y": [path["y"][i] for i in range(len(path["x"])) if path["x"][i] >= x_min_max[0] and path["x"][i] <= x_min_max[1]],
                                        "color": path["color"]
                                        })
        return values_to_print
    
    def add_numbers_naive(self, x_min_max=None):
        # Regularize x_min_max and get all the numbers to plot
        x_min_max = EnergyDiagram._regularize_x_min_max(x_min_max)
        values_to_print = self._get_visible_numbers(x_min_max)
        
        # Update axis limits before numbers and calculate ydifference 
        self._adjust_xy_limits()
        diff = (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * EnergyDiagram.DISTANCE_NUMBER_LINE

        # Plot the numbers
        for value_series in values_to_print:
            for i in range(len(value_series["x"])):
                self.ax.text(value_series["x"][i], value_series["y"][i]+diff, round(value_series["y"][i]),ha='center', va='center', fontsize=self.fontsize, color=value_series["color"])

    def add_numbers_stacked(self, x_min_max=None, sort_by_energy=True):
        # Regularize x_min_max and get all the numbers to plot
        x_min_max = EnergyDiagram._regularize_x_min_max(x_min_max)
        values_to_print = self._get_visible_numbers(x_min_max)

        # Update axis limits before numbers and calculate ydifference 
        self._adjust_xy_limits()
        diff_bias = (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * EnergyDiagram.DISTANCE_NUMBER_LINE
        diff_per_step = (self.ax.get_ylim()[1] - self.ax.get_ylim()[0]) * EnergyDiagram.DISTANCE_NUMBER_NUMBER

        # Get a list of all x values where to print
        x_places = []
        for value_series in values_to_print:
            x_places = np.concatenate((x_places, np.array(value_series["x"])))
        x_places = np.unique(x_places)
        
        # For every step, get all energies, assign the colors and sort by energy if sortenergy == True then, print the numbers
        for x_current in x_places:
            numbers_to_stack = []
            for value_series in values_to_print:
                if x_current in value_series["x"]:
                    numbers_to_stack.append({
                                            "y": value_series["y"][value_series["x"].index(x_current)],
                                            "color": value_series["color"],
                                            })
                if sort_by_energy:
                    numbers_to_stack = sorted(numbers_to_stack, key=lambda x: x["y"])
            # Print the Numbers
            n_printed = 0
            for number in numbers_to_stack:
                self.ax.text(
                            x_current, 
                            max(number["y"] for number in numbers_to_stack) + diff_bias + n_printed * diff_per_step, 
                            round(number["y"]), 
                            ha='center', 
                            va='center', 
                            fontsize=self.fontsize,
                            color=number["color"]
                            )
                n_printed += 1


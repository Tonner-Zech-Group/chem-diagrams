# Methods

| Method | Description |
|--------|-------------|
| `draw_path()` | Add a reaction pathway to the diagram |
| `add_path_labels()` | Add text labels for a specific path at the respective x-positions |
| `merge_plateaus()` | Visually merge two coincident energy levels at a shared x-position |
| `draw_difference_bar()` | Draw a vertical energy difference arrow between two levels |
| `set_xlabels()` | Set text labels for the reaction states along the x-axis |
| `set_diagram_style()` | Change the overall visual style (`open`, `boxed`, `halfboxed`, `twosided`, `borderless`) |
| `add_numbers_naive()` | Annotate each energy level directly above its bar |
| `add_numbers_stacked()` | Stack labels above the highest state to avoid overlap |
| `add_numbers_auto()` | Automatically distribute labels to minimise clutter (recommended) |
| `add_numbers_average()` | Annotate with the mean energy across all paths at each x-position |
| `modify_number_values()` | Modify existing energy annotations by adding or subtracting values |
| `append_to_energy_labels()` | Append additional values to existing energy annotations |
| `add_xaxis_break()` | Add a break marker on the x-axis |
| `add_yaxis_break()` | Add a break marker on the y-axis |
| `add_image_in_plot()` | Place a single image at an explicit data-coordinate position |
| `add_image_series_in_plot()` | Place a series of images along the diagram with automatic collision avoidance |
| `legend()` | Add a legend for all named paths |
| `show()` | Display the figure |
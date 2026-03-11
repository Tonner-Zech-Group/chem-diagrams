# chemdiagrams

[![PyPI version](https://img.shields.io/pypi/v/chemdiagrams.svg)](https://pypi.org/project/chemdiagrams/)
[![Python versions](https://img.shields.io/pypi/pyversions/chemdiagrams.svg)](https://pypi.org/project/chemdiagrams/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18957965.svg)](https://doi.org/10.5281/zenodo.18957965)

A Python package for creating publication-quality reaction energy diagrams with Matplotlib.

```python
from chemdiagrams import EnergyDiagram

dia = EnergyDiagram(
    style="twosided",
    dpi=250,
    extra_y_margin=(0,0.25),
)

dia.draw_path(
    [0,1,2], [-32, 18, 0], "blue",
    path_name="Blue path",   
)

dia.draw_path(
    [2,3,4], [0, 25, -42], "red",
    path_name="Red path",
)

dia.draw_difference_bar(
    2, (-32, -42),
    r"$\Delta E_\mathrm{R}$: ",
    left_side=True,
    x_whiskers=(0,4),
    whiskercolor="red"
)
dia.bars[0].whisker_1.set_color("blue")

dia.add_image_series_in_plot(
    [penguin_II, penguin_TS, penguin, penguin_TS, penguin_II],
    y_placement="top",
    y_offsets=2
)

dia.add_numbers_average(color="black")
dia.merge_plateaus(2, "Blue path", "Red path")
dia.add_xaxis_break(2)
dia.set_xlabels(["P1", "TS1", "E", "TS2", "P2"])
dia.ax.set_ylabel(r"$\Delta E$ in kJ mol$^{-1}$", fontsize=8)
dia.legend(fontsize=5)

dia.show()
```

![Complex diagram](https://raw.githubusercontent.com/Tonner-Zech-Group/chem-diagrams/main/docs/img/example_complex.png)

## Installation

You can use the latest release by installing it from PyPi:

```bash
pip install chemdiagrams
```

**Requirements:** Python ≥ 3.10, Matplotlib ≥ 3.7, NumPy ≥ 1.23

## Features

- Multiple reaction paths on a single diagram
- Five connector styles: dotted, solid, broken dotted, broken solid, or none
- Four diagram styles: `open`, `halfboxed`, `boxed`, `twosided`
- Automatic, stacked, naïve, and averaged energy label placement
- Energy difference bars with optional whiskers
- Axis break markers for both x and y axes
- Image placement along the diagram, with automatic collision avoidance
- Full access to the underlying Matplotlib objects for fine-grained customisation
- Method chaining for compact, readable diagram construction

## Methods

| Method | Description |
|--------|-------------|
| `draw_path()` | Add a reaction pathway to the diagram |
| `draw_difference_bar()` | Draw a vertical energy difference arrow between two levels |
| `merge_plateaus()` | Visually merge two coincident energy levels at a shared x-position |
| `set_xlabels()` | Set text labels for the reaction states along the x-axis |
| `set_diagram_style()` | Change the overall visual style (`open`, `boxed`, `halfboxed`, `twosided`) |
| `add_numbers_naive()` | Annotate each energy level directly above its bar |
| `add_numbers_stacked()` | Stack labels above the highest state to avoid overlap |
| `add_numbers_auto()` | Automatically distribute labels to minimise clutter (recommended) |
| `add_numbers_average()` | Annotate with the mean energy across all paths at each x-position |
| `add_xaxis_break()` | Add a break marker on the x-axis |
| `add_yaxis_break()` | Add a break marker on the y-axis |
| `add_image_in_plot()` | Place a single image at an explicit data-coordinate position |
| `add_image_series_in_plot()` | Place a series of images along the diagram with automatic collision avoidance |
| `legend()` | Add a legend for all named paths |
| `show()` | Display the figure |

## Usage

### Drawing paths

Each call to `draw_path` adds one reaction pathway. Paths can span different x-ranges, allowing branching or incomplete pathways.

```python
dia = EnergyDiagram()

dia.draw_path(
    x_data=[0, 1, 2, 3, 4, 5],
    y_data=[0, -13, 22, 75, 39, 20],
    color="blue",
    path_name="Pathway A",      # name appears in the legend
    linetypes=[1, 1, 2, -1, 0], # connector style per segment
)

dia.draw_path(
    x_data=[0, 1, 2, 3, 5],
    y_data=[0, -25, 20, 50, 6],
    color="red",
    path_name="Pathway B",
)

dia.legend(fontsize=7)
dia.add_numbers_auto()
dia.set_xlabels(["A", "B", "C", "D", "E", "F"])
dia.ax.set_ylabel("Energy / kJ mol$^{-1}$", fontsize=8)

dia.show()
```

![Multiple paths](https://raw.githubusercontent.com/Tonner-Zech-Group/chem-diagrams/main/docs/img/example_multipaths.png)

**Connector styles** (`linetypes`):

| Value | Style |
|-------|-------|
| `1` | dotted line (default) |
| `-1` | dotted line with gap |
| `2` | solid line |
| `-2` | solid line with gap |
| `0` | no connector |

A single integer applies the same style to all segments. A list applies styles individually.

### Diagram styles

```python
dia.set_diagram_style("halfboxed")  # open | halfboxed | boxed | twosided
```

The style can be set at construction via `EnergyDiagram(style="boxed")` or changed afterwards with `set_diagram_style`.

![Diagram styles](https://raw.githubusercontent.com/Tonner-Zech-Group/chem-diagrams/main/docs/img/example_styles.png)

### X-axis labels

By default labels are placed **below** the x-axis:
```python
dia.set_xlabels(["A", "TS", "B"], fontsize=8, weight="normal")
```

Pass `in_plot=True` to render them **inside** the plot area, directly below the lowest energy state.
```python
dia.set_xlabels(["A", "TS", "B"], in_plot=True)
```

Use `labelplaces` to set explicit x-coordinates instead of the default sequential placement:
```python
dia.set_xlabels(["A", "TS", "B"], labelplaces=[0, 2, 3])
```

### Energy labels

Four numbering strategies are available. Call them after all paths have been drawn.

```python
dia.add_numbers_auto()                   # distributes labels to avoid overlaps (recommended)
dia.add_numbers_stacked()                # stacks all labels above the highest state
dia.add_numbers_naive()                  # places each label directly above its bar
dia.add_numbers_average()                # displays the mean energy across all paths

# Restrict to a range of x-values
dia.add_numbers_auto(x_min_max=(1, 4))

# Exclude a path from labelling
dia.draw_path(..., show_numbers=False)
```

### Energy difference bars

```python
dia = EnergyDiagram(style="halfboxed")
dia.draw_path(x_data=[0,1,2,3,4,5], y_data=[0,-13,22,75,39,-25], color="blue")

dia.draw_difference_bar(
    x=3,
    y_start_end=(-25, 0),
    description=r"$\Delta E_\mathrm{R}$: ",
    color="black",
    x_whiskers=(5, 0),       # draw horizontal whiskers from x=5 and x=0
    whiskercolor="blue",
    left_side=True           # text on the left
)
dia.set_xlabels(["A", "B", "C", "D", "E", "F"])
dia.add_numbers_auto()
dia.show()
```

![Difference bar](https://raw.githubusercontent.com/Tonner-Zech-Group/chem-diagrams/main/docs/img/example_diffbar.png)

### Axis breaks

```python
dia = EnergyDiagram(style="twosided")
dia.draw_path(...)

dia.add_yaxis_break(y=5)
dia.add_xaxis_break(x=2, gap_scale=2, stopper_scale=1.5, angle=60)

dia.show()
```

Note: x-axis breaks are not compatible with the `"open"` style.

### Merging degenerate plateaus

When two paths share the same energy level at the same x-position, `merge_plateaus`
replaces both full-width bars with two shorter half-bars separated by a gap, with
diagonal tick marks to indicate degeneracy.
```python
dia = EnergyDiagram()
dia.draw_path(x_data=[0, 1, 2], y_data=[0, 50, 10], color="blue", path_name="Path A")
dia.draw_path(x_data=[0, 1, 2], y_data=[0, 50, -5], color="red",  path_name="Path B")

# Both paths share y=50 at x=1
dia.merge_plateaus(
    x=1,
    path_name_left="Path A",
    path_name_right="Path B",
    gap_scale=1.0,       # width of the gap between the two half-bars
    stopper_scale=1.0,   # size of the diagonal tick marks
    angle=30,            # angle of the tick marks in degrees
)

dia.add_numbers_auto()
dia.show()
```

Both paths must already be drawn and must have exactly the same y-value at `x`.

### Figure settings

```python
dia = EnergyDiagram(
    extra_x_margin=(0, 0.5),   # additional margin in x (axis units)
    extra_y_margin=(0, 0.2),   # additional margin in y (relative units)
    figsize=(6, 4),            # explicit figure size in inches
    width_limit=7,             # maximum auto-scaled width in inches
    fontsize=10,
    style="halfboxed",
    dpi=150,
)
```

### Placing images

`add_image_in_plot` places a single image at an explicit position in data coordinates.

```python
# Single image at a fixed position
dia.add_image_in_plot(
    "path/to/image.png",
    position=(2, 30),               # (x, y) in data coordinates
    img_name="my_image",            # optional name to access the artist later via dia.images
    width=0.5,                      # width in axis units; 
                                    # if omitted, height is used to scale or width is set automatically
    height=None,                    # height in axis units
    horizontal_alignment="center",  # "center", "left", or "right" relative to position
    vertical_alignment="center",    # "center", "top", or "bottom" relative to position
    framed=True,                    # draw a border rectangle around the image
    frame_color="black",            # color of the border
)
```

`add_image_series_in_plot` places one image per reaction state, with automatic collision avoidance against energy numbers and x-axis labels.

```python
# Series of images distributed automatically along the diagram
dia.add_image_series_in_plot(
    ["img0.png", "img1.png", "img2.png", "img3.png", "img4.png"],
    img_x_places=[0, 1, 2, 3, 4],        # which x positions to place images at;
                                         # defaults to 0,1,2,... if omitted
    y_placement="auto",                  # "auto", "top", or "bottom" — can also be a list
                                         # per image, e.g. ["auto", "top", "auto", "bottom", "auto"]
                                         # "auto" automatically decides whether it is placed on top or bottom
    y_offsets=5,                         # additional vertical offset in data units, scalar or per-image list
    img_series_name="my_series",         # optional name to access artists later via dia.images
    width=0.6,                           # scalar applies to all; pass a list for per-image widths
                                         # if omitted, height is used to scale or width is set automatically
    height=None,                         # scalar applies to all; pass a list for per-image heights
    framed=False,                        # scalar or per-image list of bools
    frame_colors="black",                # scalar or per-image list of color strings
)
```

SVG and EPS formats are not supported; PNG and JPEG work best.

### Saving figures

```python
dia.fig.savefig("diagram.png", dpi=300, bbox_inches="tight")
dia.fig.savefig("diagram.pdf", bbox_inches="tight")
```

### Accessing Matplotlib objects

All artists are accessible after drawing for direct Matplotlib customisation.

```python
dia.draw_path(..., path_name="My Path")
dia.add_numbers_auto()

# Plateau and connector lines
# Keys are x-positions formatted to one decimal place
plateau   = dia.lines["My Path"].plateaus["2.0"]     # x=2
connector = dia.lines["My Path"].connections["1.5"]  # midpoint between x=1 and x=2
plateau.set_color("green")

# Energy labels
label = dia.numbers["My Path"]["2.0"]                # x=2
label.set_color("red")
label.set_fontsize(12)

# Difference bar components
dia.bars[0].text.set_color("red")
dia.bars[0].bar.arrow_patch.set_color("green")
dia.bars[0].whisker_2.set_linestyle("--")

# Style objects (axes, arrows, x-labels)
dia.ax_objects.x_labels["2.0"].set_color("purple")

# Axis arrows (twosided/open/halfopen styles)
dia.ax_objects.arrows["x_arrow"].set_color("gray")

# Axis break artists
dia.ax_objects.xaxis_breaks["2.0"].stopper_1.set_color("red")
dia.ax_objects.yaxis_breaks["5.0"].whitespace.set_facecolor("lightyellow")

# Direct Matplotlib axes access
dia.ax.set_ylabel("Energy / kJ mol$^{-1}$", fontsize=10)
dia.fig.savefig("diagram.png", dpi=300, bbox_inches="tight")

# Access a single image artist added with add_image_in_plot
img_object = dia.images["my_image"]                  # ImageObject
img_object.image.set_alpha(0.8)                      # AxesImage — any matplotlib imshow property
img_object.borders["top"].set_color("red")           # frame border lines, keyed by "top",
img_object.borders["left"].set_linewidth(2)          # "bottom", "top", "left", "right"

# Access images added with add_image_series_in_plot
series = dia.images["my_series"]                     # dict keyed by x-position as "x.x" string
img_at_x1 = series["1.0"]                            # ImageObject at x=1
img_at_x1.image.set_alpha(0.5)
img_at_x1.borders["bottom"].set_linestyle("--")

```

## Examples

A full set of examples covering all features is available in [`examples/example_use.ipynb`](https://github.com/Tonner-Zech-Group/chem-diagrams/blob/main/examples/example_use.ipynb).

## Citation

If you use chemdiagrams in published work, please consider citing the repository:

```
Tim Bastian Enders, chemdiagrams, https://github.com/Tonner-Zech-Group/chem-diagrams, https://doi.org/10.5281/zenodo.18957965
```

## License

MIT — see [LICENSE](LICENSE) for details.

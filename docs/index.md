# chemdiagrams

[![PyPI version](https://img.shields.io/pypi/v/chemdiagrams.svg)](https://pypi.org/project/chemdiagrams/)
[![Python versions](https://img.shields.io/pypi/pyversions/chemdiagrams.svg)](https://pypi.org/project/chemdiagrams/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/Tonner-Zech-Group/chem-diagrams/blob/main/LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18957965.svg)](https://doi.org/10.5281/zenodo.18957965)

A Python package for creating publication-quality reaction energy diagrams with Matplotlib.

![Title Image](https://raw.githubusercontent.com/Tonner-Zech-Group/chem-diagrams/main/docs/img/title/merged_image.png)

## Installation

You can use the latest release by installing it from PyPi:

```bash
pip install chemdiagrams
```

**Requirements:** Python ≥ 3.10, Matplotlib ≥ 3.7, NumPy ≥ 1.23

## Features

- Multiple reaction paths on a single diagram
- Seven connector styles: dotted, solid, broken dotted, broken solid, spline dotted, spline solid or none
- Five diagram styles: `open`, `halfboxed`, `boxed`, `twosided`, `borderless`
- Automatic, stacked, naïve, and averaged energy label placement (numbering)
- Energy difference bars with optional whiskers
- Axis break markers for both x and y axes
- Image placement along the diagram, with automatic collision avoidance
- Full access to the underlying Matplotlib objects for fine-grained customisation

## Methods

| Method | Description |
|--------|-------------|
| `draw_path()` | Add a reaction pathway to the diagram |
| `add_path_labels()` | Add text labels for a specific path at the respective x-positions |
| `draw_difference_bar()` | Draw a vertical energy difference arrow between two levels |
| `merge_plateaus()` | Visually merge two coincident energy levels at a shared x-position |
| `set_xlabels()` | Set text labels for the reaction states along the x-axis |
| `set_diagram_style()` | Change the overall visual style (`open`, `boxed`, `halfboxed`, `twosided`, `borderless`) |
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
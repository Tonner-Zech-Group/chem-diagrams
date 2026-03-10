# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project does not yet follow semantic versioning; a versioning policy
will be adopted before the 1.0.0 release.

## [Unreleased]

## [0.0.1] — 2025-01-01

Initial public release.

### Added

- `EnergyDiagram` class as the single public entry point for building
  reaction energy diagrams
- `draw_path()` — plot one or more reaction pathways with per-segment
  connector styles (`dotted`, `solid`, `broken dotted`, `broken solid`,
  `none`)
- `merge_plateaus()` — visually merge two degenerate energy levels at a
  shared x-position with diagonal tick marks
- `draw_difference_bar()` — vertical double-headed arrow between two
  energy levels with optional horizontal whiskers and auto-computed label
- Four diagram styles: `open`, `halfboxed`, `boxed`, `twosided`
- `set_diagram_style()` — change the style after construction
- Four energy label placement strategies: `add_numbers_naive()`,
  `add_numbers_stacked()`, `add_numbers_auto()`, `add_numbers_average()`
- `set_xlabels()` — text labels for reaction states, either below the
  axis or inside the plot area
- `add_xaxis_break()` / `add_yaxis_break()` — discontinuity markers on
  either axis
- `add_image_in_plot()` — place a single image at an explicit
  data-coordinate position with optional frame border
- `add_image_series_in_plot()` — place a series of images along the
  diagram with automatic collision avoidance against energy bars, number
  annotations, and x-axis labels
- `legend()` — legend for all named paths
- Method chaining — every mutating public method returns `self`
- Full access to the underlying Matplotlib `fig` and `ax` objects and all
  rendered artists via `dia.lines`, `dia.bars`, `dia.numbers`,
  `dia.images`, `dia.ax_objects`
- Input validation with descriptive `TypeError` / `ValueError` messages
  throughout
- CI pipeline running ruff (lint + format), mypy, and pytest across
  Python 3.10 – 3.13

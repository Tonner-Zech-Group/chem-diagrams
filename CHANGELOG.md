# Changelog

All notable changes to this project will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.4.0] — 2026-04-16

### Added

- Option to use custom templates for diagram styling and layout. Users can create their own templates by subclassing `BaseTemplate` and overriding default constants and the `startup()` method for custom diagram initialization.

## [0.3.0] — 2026-04-02

### Added

- Method for selectively modifying existing energy annotations by adding or subtracting values via `modify_number_values()`.
- Added `lw_connector` parameter to `add_path()` for custom line widths of connectors between energy levels.
- Added `gap_scale` parameter to `add_path()` for controlling the size of gaps in broken line styles.
- New line styles for paths: `-4` and `-3` for broken splines.

### Changed

- Increased constants for spacing of numbers slighly.

## [0.2.0] — 2026-04-02

### Added

- Documentation on GitHub Pages with detailed usage instructions and examples for all methods.
- Custom text labels for each path at each position.
- Spline connector styles (`spline dotted`, `spline solid`) for smoother curves between energy levels.
- Decimal placees control for energy level annotations via `n_decimals` parameter in all `add_numbers_*()` methods.

## [0.1.2] — 2026-03-28

### Changed

- Expanded README with more examples and usage instructions.

## [0.1.1] — 2026-03-15

### Changed

- Added `borderless` style option.
- Fixed placement bug of multiline x-axis labels when `in_plot=True`.

## [0.1.0] — 2026-03-11

### Changed

- Bumped version to 0.1.0 for first PyPI release
- Added `__version__` attribute to package (`chemdiagrams.__version__`)

## [0.0.1] — 2026-03-10

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

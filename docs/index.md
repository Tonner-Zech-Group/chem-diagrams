# chemdiagrams

[![PyPI version](https://img.shields.io/pypi/v/chemdiagrams.svg)](https://pypi.org/project/chemdiagrams/)
[![Python versions](https://img.shields.io/pypi/pyversions/chemdiagrams.svg)](https://pypi.org/project/chemdiagrams/)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://tonner-zech-group.github.io/chem-diagrams/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/Tonner-Zech-Group/chem-diagrams/blob/main/LICENSE)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18957965.svg)](https://doi.org/10.5281/zenodo.18957965)

A Python package for creating publication-quality reaction energy diagrams with Matplotlib.

![Title Image](https://raw.githubusercontent.com/Tonner-Zech-Group/chem-diagrams/main/docs/img/title/merged_image.png)

## Installation

You can use the latest release by installing it from PyPi:

```bash
pip install chemdiagrams
```

**Requirements:** Python ≥ 3.10, Matplotlib ≥ 3.7, NumPy ≥ 1.23, SciPy ≥ 1.10

## Features

- Multiple reaction paths on a single diagram
- Nine connector styles: dotted, solid, broken dotted, broken solid, spline dotted, spline solid, broken spline dotted, broken spline solid or none
- Five diagram styles: `open`, `halfboxed`, `boxed`, `twosided`, `borderless`
- Automatic, stacked, naïve, and averaged energy label placement (numbering)
- Custom text labels for each path at each position
- Energy difference bars with optional whiskers
- Axis break markers for both x and y axes
- Image placement along the diagram, with automatic collision avoidance
- Full access to the underlying Matplotlib objects for fine-grained customisation
"""Constants for plotting the energy diagram"""

#################################
# Bar Manager
#################################

# Default distance of text next to Bar in x units
DISTANCE_TEXT_DIFFBAR = 0.02

LW_WHISKER = 0.7
ZORDER_WHISKER = 0.8


#################################
# Figure Manager
#################################

# Standard fontsize
STD_FONTSIZE = 8


#################################
# Image Manager
#################################

# Standard width of an image in x units
IMAGE_WIDTH = 0.6

# Default distances of images (inches at sdt fontsize)
DISTANCE_IMAGE_LINE = 0.09
DISTANCE_IMAGE_LABEL = 0.12
DISTANCE_IMAGE_NUMBER = 0.15  # 0.135 pre v0.3.0

# Frame parameters
LW_IMAGE_FRAME = 0.5
ZORDER_IMAGE_FRAME = 0.5


#################################
# Layout Manager
#################################

# Default margins (x absolute, y relative)
DEFAULT_X_MARGINS = (-0.5, 0.5)
DEFAULT_Y_MARGINS = (-0.1, 0.15)

# Default height of Diagram in inches
FIG_HEIGHT = 3

# Default width in inches per x-tick
X_SCALE = 0.8

#################################
# Number Manager
#################################

# Default distance numbers above plateau (inches at sdt fontsize)
DISTANCE_NUMBER_LINE = 0.10  # 0.09 pre v0.3.0

# Default distance between numbers (inches at sdt fontsize)
DISTANCE_NUMBER_NUMBER = 0.15  # 0.135 pre v0.3.0

ZORDER_NUMBERS = 2


#################################
# Path Manager
#################################

# Plateu parameters
ZORDER_PLATEAU = 2
LW_PLATEAU = 1.8
WIDTH_PLATEAU = 0.5

# Connector parameters
ZORDER_CONNECTOR = 1
LW_CONNECTOR = 1.0

# Broken line parameters
BROKEN_LINE_GAP = 0.2
ZORDER_BROKEN_LINE_STOPPER = 1
LW_BROKEN_LINE_STOPPER = 0.8
SIZE_BROKEN_LINE_STOPPER = 3

# Merged Plateu parameters
MERGED_PLATEAU_GAP = 0.1
MERGED_PLATEAU_COVER_WIDTH = 0.05
ZORDER_MERGED_PLATEAU_COVER = 2.1
LW_MERGED_PLATEAU_STOPPER = 1.5
SIZE_MERGED_PLATEAU_STOPPER = 1.5
ZORDER_MERGED_PLATEAU_STOPPER = 2.5


#################################
# Style Manager
#################################

# Axis arrow parameters
ZORDER_AXIS_ARROWS = 3
SIZE_AXIS_ARROWS = 12

# x axis (stlye="open") parameters
ZORDER_X_AXIS = 0.5
LW_X_AXIS = 0.8
X_AXIS_OFFSET_OPENSTYLE = -0.03

# Label (in_plot=True) parameters
DISTANCE_LABEL_LINE = 0.12
DISTANCE_LABEL_NEWLINE = 0.095
ZORDER_X_LABEL = 1

# Axes break cover parameters in inches or degree
AXIS_BREAK_GAP = 0.1
AXIS_BREAK_COVER_WIDTH = 0.03
ZORDER_AXIS_BREAK_COVER = 4.5

# Axes break stopper parameters
LW_AXIS_BREAK_STOPPER = 0.8
SIZE_AXIS_BREAK_STOPPER = 2
ZORDER_AXIS_BREAK_STOPPER = 5

class Constants:
    """Default constants for plotting the energy diagram"""

    def __init__(self):
        #################################
        # High level defaults
        #################################

        self.DEFAULT_STYLE = "open"
        self.DEFAULT_FIGSIZE = None
        self.STD_FONTSIZE = 8
        self.DEFAULT_WIDTH_LIMIT = None

        #################################
        # Bar Manager
        #################################

        # Default distance of text next to Bar in x units
        self.DISTANCE_TEXT_DIFFBAR = 0.02

        self.LW_WHISKER = 0.7
        self.ZORDER_WHISKER = 0.8

        #################################
        # Figure Manager
        #################################

        self.DEFAULT_DPI = 150

        #################################
        # Image Manager
        #################################

        # Standard width of an image in x units
        self.IMAGE_WIDTH = 0.6

        # Default distances of images (inches at sdt fontsize)
        self.DISTANCE_IMAGE_LINE = 0.09
        self.DISTANCE_IMAGE_LABEL = 0.12
        self.DISTANCE_IMAGE_NUMBER = 0.15  # 0.135 pre v0.3.0
        self.ZORDER_IMAGE = 0.6
        self.IMAGE_INTERPOLATION_METHOD = "bilinear"

        # Frame parameters
        self.LW_IMAGE_FRAME = 0.5
        self.ZORDER_IMAGE_FRAME = 0.5

        #################################
        # Layout Manager
        #################################

        # Default margins (x absolute, y relative)
        self.DEFAULT_X_MARGINS = (-0.5, 0.5)
        self.DEFAULT_Y_MARGINS = (-0.1, 0.15)

        # Default height of Diagram in inches
        self.FIG_HEIGHT = 3

        # Default width in inches per x-tick
        self.X_SCALE = 0.8

        #################################
        # Number Manager
        #################################

        # Default distance numbers above plateau (inches at sdt fontsize)
        self.DISTANCE_NUMBER_LINE = 0.10  # 0.09 pre v0.3.0

        # Default distance between numbers (inches at sdt fontsize)
        self.DISTANCE_NUMBER_NUMBER = 0.15  # 0.135 pre v0.3.0

        self.ZORDER_NUMBERS = 2
        self.MINUS_SIGN = "\u2212"

        #################################
        # Path Manager
        #################################

        # Plateu parameters
        self.ZORDER_PLATEAU = 2
        self.LW_PLATEAU = 1.8
        self.WIDTH_PLATEAU = 0.5

        # Connector parameters
        self.ZORDER_CONNECTOR = 1
        self.LW_CONNECTOR = 1.0

        # Broken line parameters
        self.BROKEN_LINE_GAP = 0.2
        self.ZORDER_BROKEN_LINE_STOPPER = 1
        self.LW_BROKEN_LINE_STOPPER = 0.8
        self.SIZE_BROKEN_LINE_STOPPER = 3

        # Merged Plateu parameters
        self.MERGED_PLATEAU_GAP = 0.1
        self.MERGED_PLATEAU_COVER_WIDTH = 0.05
        self.ZORDER_MERGED_PLATEAU_COVER = 2.1
        self.LW_MERGED_PLATEAU_STOPPER = 1.5
        self.SIZE_MERGED_PLATEAU_STOPPER = 1.5
        self.ZORDER_MERGED_PLATEAU_STOPPER = 2.5

        #################################
        # Style Manager
        #################################

        # Axis arrow parameters
        self.ZORDER_AXIS_ARROWS = 3
        self.SIZE_AXIS_ARROWS = 12

        # x axis (stlye="open") parameters
        self.ZORDER_X_AXIS = 0.5
        self.LW_X_AXIS = 0.8
        self.X_AXIS_OFFSET_OPENSTYLE = -0.03

        # Label (in_plot=True) parameters
        self.DISTANCE_LABEL_LINE = 0.12
        self.DISTANCE_LABEL_NEWLINE = 0.095
        self.ZORDER_X_LABEL = 1

        # Axes break cover parameters in inches or degree
        self.AXIS_BREAK_GAP = 0.1
        self.AXIS_BREAK_COVER_WIDTH = 0.03
        self.ZORDER_AXIS_BREAK_COVER = 4.5

        # Axes break stopper parameters
        self.LW_AXIS_BREAK_STOPPER = 0.8
        self.SIZE_AXIS_BREAK_STOPPER = 2
        self.ZORDER_AXIS_BREAK_STOPPER = 5

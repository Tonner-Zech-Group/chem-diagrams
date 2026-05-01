from chemdiagrams.templates.base_template import BaseTemplate


class ExampleTemplate(BaseTemplate):
    """Simple template showcasing basic style customizations for diagrams."""

    def __init__(self):
        """
        Modyfy constants for Example style diagrams here.
        e.g. self.constants.DISTANCE_TEXT_DIFFBAR = 0.05
        """
        super().__init__()
        # Change constants here
        self.constants.WIDTH_PLATEAU = 0.4
        self.constants.LW_CONNECTOR = 0.6
        self.constants.MINUS_SIGN = "-"

    def startup(self, diagram):
        """
        Startup function to be called at the beginning of the plotting process
        Here you can modify the diagram object before any plotting is done.
        """
        diagram = super().startup(diagram)
        # Change diagram here
        diagram.set_diagram_style("open")
        diagram.ax_objects.axes["x_axis"].remove()
        diagram.ax.grid(True, which="both", axis="y", ls="--", lw=0.5, zorder=-1)
        return diagram

    # Example of a custom function to modify the diagram after plotting
    @staticmethod
    def color_all_numbers(diagram, color):
        """Set the colors of all numbers to the specified color"""
        for path_numbers in diagram.numbers.values():
            for number in path_numbers.values():
                number.set_color(color)
        return diagram

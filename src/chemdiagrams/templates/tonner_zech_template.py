from chemdiagrams.templates.base_template import BaseTemplate


class TonnerZechTemplate(BaseTemplate):
    def __init__(self):
        """
        Modyfy constants for Tonner and Zech style diagrams here.
        e.g. self.constants.DISTANCE_TEXT_DIFFBAR = 0.05
        """
        super().__init__()

    def startup(self, diagram):
        """
        Startup function to be called at the beginning of the plotting process
        Here you can modify the diagram object before any plotting is done.
        """
        diagram = super().startup(diagram)
        return diagram

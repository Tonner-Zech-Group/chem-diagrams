from ..constants import Constants


class BaseTemplate:
    """
    Base template class for energy diagrams

    This template does not change any default settings and can be used
    as a starting point for custom templates. It is also the default template
    if no other template is specified.
    """

    def __init__(self):
        self.constants = Constants()

    def startup(self, diagram):
        """Startup function to be called at the beginning of the plotting process"""
        return diagram

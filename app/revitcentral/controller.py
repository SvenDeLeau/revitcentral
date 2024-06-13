# imports
from pathlib import Path

# VIKTOR imports
from viktor.core import ViktorController, File
from viktor.views import IFCResult, IFCView

# Local imports
from .parametrization import RevitCentralParametrization


class RevitCentralController(ViktorController):
    """
    This is the controller class of the entity revitcentral.
    """

    viktor_enforce_field_constraints = True

    label = "Revit Central Converter"
    children = []
    parametrization = RevitCentralParametrization

    @IFCView("IFC view", duration_guess=1)
    def get_ifc_view(self, params, **kwargs):
        ifc = params.gemaal_parameters.user_case.file
        return IFCResult(ifc)

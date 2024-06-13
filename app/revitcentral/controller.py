# imports
from pathlib import Path

# VIKTOR imports
from viktor.core import ViktorController, File
from viktor.views import IFCResult, IFCView

# Local imports
from .parametrization import RevitCentralParametrization


class RevitCentralController(ViktorController):
    """
    This is the controller class of the entity WatKostEenGemaal.
    """

    viktor_enforce_field_constraints = True

    label = "Revit Central Converter"
    children = []
    parametrization = RevitCentralParametrization

    @IFCView("IFC view", duration_guess=1)
    def get_ifc_view(self, params, **kwargs):
        ifc = File.from_path(Path(__file__).parent / 'Project1.ifc')
        return IFCResult(ifc)

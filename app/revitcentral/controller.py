# imports
from pathlib import Path
import ifcopenshell

# VIKTOR imports
from viktor.core import ViktorController, File
from viktor.views import IFCResult, IFCView
from viktor.result import SetParamsResult

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
        ifc = File.from_path(Path(__file__).parent / 'Project1.ifc')
        model = ifcopenshell.open(Path(__file__).parent / 'Project1.ifc')
        
        return IFCResult(ifc)
    
    def set_param_ifc(self, params, **kwargs):
        updated_parameter_set = params.gemaal_parameters.user_case.new
        model = ifcopenshell.open(Path(__file__).parent / 'Project1.ifc')
        print(model.by_id(int(updated_parameter_set[0])))
    

        return SetParamsResult(updated_parameter_set)

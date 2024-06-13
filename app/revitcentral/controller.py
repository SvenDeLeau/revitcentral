# imports
from pathlib import Path
import ifcopenshell
import ifcopenshell.util.element
from tempfile import NamedTemporaryFile

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
        ifc = params.gemaal_parameters.user_case.file
        
        return IFCResult(ifc)
    
    def set_param_ifc(self, params, **kwargs):
        selected_geometries = params.gemaal_parameters.geometry_information.new

        temp_f = NamedTemporaryFile(suffix=".ifc", delete=False, mode="w")
        temp_f.write(params.gemaal_parameters.user_case.file.file.getvalue())
        model = ifcopenshell.open(Path(temp_f.name))

        geometry_table_list = []

        for element in selected_geometries:
            elem = model.by_id(int(element))
            psets = ifcopenshell.util.element.get_psets(elem)
            print(psets)
            geometry_table_dict = {
                'tag': elem.get_info()['Tag'],
                'element': psets['Text']['MHP_PRO_Name'],
                'length': psets['Dimensions']['Length']}
            
            geometry_table_list.append(geometry_table_dict)
    
        return SetParamsResult({
            "gemaal_parameters": {
                "geometry_information": {
                    "table": geometry_table_list
                }
            }
        })

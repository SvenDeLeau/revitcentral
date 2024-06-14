# imports
from pathlib import Path
import ifcopenshell
import ifcopenshell.util.element
from tempfile import NamedTemporaryFile
from viktor.api_v1 import API
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
    children = ['BeamController']
    show_children_as = 'Table'
    parametrization = RevitCentralParametrization(width=60)

    @IFCView("IFC view", duration_guess=1)
    def get_ifc_view(self, params, **kwargs):
        ifc = params.parameters.user_case.file
        return IFCResult(ifc)
    
    def set_param_ifc(self, params, entity_id, **kwargs):
        selected_geometries = params.parameters.geometry_information.new
        temp_f = NamedTemporaryFile(suffix=".ifc", delete=False, mode="w")
        temp_f.write(params.parameters.user_case.file.file.getvalue())
        model = ifcopenshell.open(Path(temp_f.name))

        geometry_table_list = []
        api = API()
        current_entity = api.get_entity(entity_id)
        childnames=[]
        childlist = current_entity.children()
            
        for child in childlist:
            childnames.append(child.name)
        
        for element in selected_geometries:
            elem = model.by_id(int(element))
            psets = ifcopenshell.util.element.get_psets(elem)
            #print(psets)
            #geometry_table_dict = {
            #    'tag': elem.get_info()['Tag'],
            #    'element': psets['Text']['MHP_PRO_Name'],
            #    'length': psets['Dimensions']['Length']}

            if elem.get_info()['Tag'] in childnames:
                next
            else:
                api.create_child_entity(parent_entity_id= entity_id, entity_type_name='BeamController', name=elem.get_info()['Tag'], params= {"input":{"length": psets['Dimensions']['Length']}}, **kwargs)
            #geometry_table_list.append(geometry_table_dict)

        return SetParamsResult(params)
        
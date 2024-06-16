# Imports
from pathlib import Path
import ifcopenshell
import ifcopenshell.util.element
from tempfile import NamedTemporaryFile
from viktor.api_v1 import API
from viktor.core import ViktorController, File
from viktor.views import IFCResult, IFCView
from viktor.result import SetParamsResult

# Local imports
from .parametrization import RevitCentralParametrization

class RevitCentralController(ViktorController):
    """
    This is the controller class for the RevitCentral entity.
    It manages IFC views and handles interactions with the VIKTOR API.
    """
    
    viktor_enforce_field_constraints = True
    label = "Revit Central Converter"
    children = ['BeamController']
    show_children_as = 'Table'
    parametrization = RevitCentralParametrization(width=60)

    @IFCView("IFC view", duration_guess=1)
    def get_ifc_view(self, params, **kwargs):
        """
        Renders the IFC view.

        :param params: Parameters containing the IFC file information.
        :param kwargs: Additional keyword arguments.
        :return: IFCResult containing the IFC file.
        """
        ifc = params.parameters.user_case.file
        return IFCResult(ifc)
    
    def set_param_ifc(self, params, entity_id, **kwargs):
        """
        Sets the parameters of the IFC file and creates child entities for new geometries.

        :param params: Parameters containing the user case and geometry information.
        :param entity_id: The ID of the current entity.
        :param kwargs: Additional keyword arguments.
        :return: SetParamsResult with updated parameters.
        """
        selected_geometries = params.parameters.geometry_information.new

        # Create a temporary IFC file
        with NamedTemporaryFile(suffix=".ifc", delete=False, mode="w") as temp_f:
            temp_f.write(params.parameters.user_case.file.file.getvalue())
            temp_f_path = temp_f.name

        # Open the IFC model
        model = ifcopenshell.open(Path(temp_f_path))

        # Initialize the API and get current entity information
        api = API()
        current_entity = api.get_entity(entity_id)
        child_names = [child.name for child in current_entity.children()]

        # Process each selected geometry
        for element in selected_geometries:
            elem = model.by_id(int(element))
            psets = ifcopenshell.util.element.get_psets(elem)
            
            # Check if the element tag is already a child entity
            if elem.get_info()['Tag'] not in child_names:
                # Create a new child entity if it doesn't exist
                api.create_child_entity(
                    parent_entity_id=entity_id,
                    entity_type_name='BeamController',
                    name=elem.get_info()['Tag'],
                    params={"input": {"length": psets['Dimensions']['Length']}},
                    **kwargs
                )

        return SetParamsResult(params)

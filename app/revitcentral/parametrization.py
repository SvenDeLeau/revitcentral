from viktor.parametrization import Parametrization, Step, BooleanField, Section, GeometryMultiSelectField, FileField, SetParamsButton

class RevitCentralParametrization(Parametrization):

      gemaal_parameters = Step("Geometry data selection", views='get_ifc_view')
      gemaal_parameters.user_case = Section("Geometry selection")
      gemaal_parameters.user_case.new = GeometryMultiSelectField("Select geometry")


      gemaal_parameters.user_case.params_button = SetParamsButton("Set params", "set_param_ifc", longpoll=True)


      gemaal_parameters.user_case.file = FileField ("IFC from Revit")

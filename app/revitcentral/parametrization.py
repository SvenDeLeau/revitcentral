from viktor.parametrization import Parametrization, Step, BooleanField, Section, GeometryMultiSelectField, FileField, NumberField

class RevitCentralParametrization(Parametrization):

      gemaal_parameters = Step("Geometry data selection", views='get_ifc_view')
      gemaal_parameters.user_case = Section("Geometry selection")
      gemaal_parameters.user_case.new = GeometryMultiSelectField("Select geometry")
      gemaal_parameters.user_case.file = FileField ("IFC from Revit")
      gemaal_parameters.user_case.numbertorevit =  NumberField('Enter a value')
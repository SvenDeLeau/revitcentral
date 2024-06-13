from viktor.parametrization import Parametrization, Step, BooleanField, Section, GeometrySelectField

class RevitCentralParametrization(Parametrization):

      gemaal_parameters = Step("Geometry data selection", views='get_ifc_view')
      gemaal_parameters.user_case = Section("Geometry selection")
      gemaal_parameters.user_case.new = GeometrySelectField("Select geometry")
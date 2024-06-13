from viktor.parametrization import Parametrization, Step, BooleanField, Section, GeometryMultiSelectField, FileField, SetParamsButton, Table, TextField, NumberField, LineBreak

class RevitCentralParametrization(Parametrization):

      gemaal_parameters = Step("Geometry data selection", views='get_ifc_view')
      gemaal_parameters.user_case = Section("Geometry selection")
      gemaal_parameters.user_case.file = FileField ("IFC from Revit")
      gemaal_parameters.user_case.numbertorevit =  NumberField('Enter a value')

      gemaal_parameters.geometry_information = Section("Geometry information")
      gemaal_parameters.geometry_information.new = GeometryMultiSelectField("Select geometry")
      gemaal_parameters.geometry_information.params_button = SetParamsButton("Generate table values", "set_param_ifc", longpoll=True)
      gemaal_parameters.geometry_information.lb = LineBreak()
      gemaal_parameters.geometry_information.table = Table('Geometry table')
      gemaal_parameters.geometry_information.table.tag = TextField('Tag')
      gemaal_parameters.geometry_information.table.element = TextField('Element')
      gemaal_parameters.geometry_information.table.length = NumberField('Length')



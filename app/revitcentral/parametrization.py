from viktor.parametrization import Parametrization, ChildEntityManager, Step, BooleanField, Section, GeometryMultiSelectField, FileField, SetParamsButton, Table, TextField, NumberField, LineBreak

class RevitPushPullParametrization(Parametrization):

      parameters = Step("Geometry data selection", views='get_ifc_view')
      parameters.user_case = Section("Geometry selection")
      parameters.user_case.file = FileField ("IFC from Revit")

      parameters.geometry_information = Section("Geometry information")
      parameters.geometry_information.new = GeometryMultiSelectField("Select geometry")
      parameters.geometry_information.params_button = SetParamsButton("Get Beam Values", "set_param_ifc", longpoll=True)
      parameters.geometry_information.lb = LineBreak()

      parameters.geometry_information.beamentitymanager = ChildEntityManager ('BeamController')



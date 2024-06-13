from viktor.parametrization import Parametrization, Step, BooleanField, Section

class RevitCentralParametrization(Parametrization):

      gemaal_parameters = Step("Selecteer opties voor het gemaal", views='get_ifc_view')
      gemaal_parameters.user_case = Section("Project fase")
      gemaal_parameters.user_case.new = BooleanField("Ik wil een nieuw gemaal bouwen")
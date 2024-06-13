from viktor.api import API, ask_for_personal_access_token
from viktor.variables import get_viktor_doc_var, set_viktor_doc_data, get_viktor_global_var
from viktor.forms import VIKTORWindow
from pyrevit import forms
from pyrevit.framework import Input
from Autodesk.Revit.UI import TaskDialog
from Autodesk.Revit.DB import Transaction, StorageType, ElementId
import json

doc = __revit__.ActiveUIDocument.Document


class PullDataWindow(VIKTORWindow):
    """VIKTOR Pull Data window"""

    def __init__(self):
        VIKTORWindow.__init__(self, "VIKTORPullWindow.xaml")

        self.urlTextBox.Text = get_viktor_doc_var("default_resource_url") or "<entity_URL>"

    def handle_input_key(self, sender, args):  # pylint: disable=W0613
        """Handle keyboard input and close the window on Escape."""
        if args.Key == Input.Key.Escape:
            self.Close()
        if args.Key == Input.Key.Enter:
            self.pull_button_click(sender, args)
            self.Close()

    @property
    def resource_url(self):
        resource_url = self.urlTextBox.Text
        if not resource_url:
            forms.alert("Entity URL must be filled in!", exitscript=True)
        return resource_url

    def cancel_button_click(self, sender, args):
        self.Close()

    def pull_button_click(self, sender, args):
        resource_url = self.resource_url
        set_viktor_doc_data(default_resource_url=self.resource_url)
        with forms.ProgressBar(title="Checking VIKTOR credentials ...", height=50) as pb:
            try:
                pb.title = "Checking VIKTOR credentials ..."
                pb.update_progress(1, 3)
                environment, workspace_id, entity_id = API.parse_resource_url(resource_url)
                token = get_viktor_global_var('VIKTOR_PAT')
                if not token:
                    token = ask_for_personal_access_token()
                api = API(environment=environment, token=token)
                api.verify()

                pb.title = "Pulling data from VIKTOR platform ..."
                pb.update_progress(2, 3)
                
                # DEBUG: Pull and display data
                data = api.get_entity_data(workspace_id=workspace_id, entity_id=entity_id)
                TaskDialog.Show("VIKTOR Pull Data", "Pulled data: {}".format(json.dumps(data, indent=4)))

                # Extracting the specific float value
                try:
                    float_value = data['parameters']['gemaal_parameters']['user_case']['numbertorevit']
                except KeyError:
                    float_value = 'N/A'

                pb.update_progress(3, 3)
                self.valueTextBox.Text = str(float_value)
                TaskDialog.Show("VIKTOR Pull Data", "Pulled float value: {}".format(float_value))

                # Example hardcoded profile data
                pulled_profile_str = "IPE200,200,100,5.6,8.5,12"  # TEMPORARY HARDCODED

                # Parsing the profile data
                profile_parts = pulled_profile_str.split(',')
                conversion_factor = 3.28084/1000  # meters to feet conversion factor
                profile_data = {
                    "h": float(profile_parts[1]) * conversion_factor,
                    "b": float(profile_parts[2]) * conversion_factor,
                    "Tw": float(profile_parts[3]) * conversion_factor,
                    "Tf": float(profile_parts[4]) * conversion_factor,
                    "r": float(profile_parts[5]) * conversion_factor
                }

                # Display the pulled profile data in the valueTextBox and a TaskDialog
                self.valueTextBox.Text = str(profile_data)
                TaskDialog.Show("VIKTOR Pull Data", "Pulled profile data: {}".format(json.dumps(profile_data, indent=4)))

                tag = 319234  # hardcoded family instance ID

                # Updating Revit family parameters
                t = Transaction(doc, "Update Beam Profile")
                t.Start()
                family_instance_id = ElementId(tag)  # Convert to ElementId
                family_instance = doc.GetElement(family_instance_id)
                if family_instance:
                    for param_name, param_value in profile_data.items():
                        param = family_instance.LookupParameter(param_name)
                        if param and param.StorageType == StorageType.Double:
                            param.Set(param_value)
                t.Commit()

            except ValueError as err:
                forms.alert(str(err), exitscript=True)

        forms.toast(
            "Data successfully pulled from VIKTOR!",
            title="VIKTOR Pull", appid="VIKTOR"
        )
        self.Close()


if __name__ == '__main__':
    PullDataWindow().show_dialog()

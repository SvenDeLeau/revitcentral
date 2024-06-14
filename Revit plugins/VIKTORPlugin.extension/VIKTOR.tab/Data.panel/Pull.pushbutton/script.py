from viktor.api import API, ask_for_personal_access_token
from viktor.variables import get_viktor_doc_var, set_viktor_doc_data, get_viktor_global_var
from viktor.forms import VIKTORWindow
from pyrevit import forms
from pyrevit.framework import Input
from Autodesk.Revit.UI import TaskDialog
from Autodesk.Revit.DB import Transaction, StorageType, ElementId
import ast
import json

doc = __revit__.ActiveUIDocument.Document


class Pullchild_dataWindow(VIKTORWindow):
    """VIKTOR Pull child_data window"""

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

                pb.title = "Pulling child_data from VIKTOR platform ..."
                pb.update_progress(2, 3)
                
                # Pull and display child_data for debugging
                child_data = api.get_all_child_entity_data(workspace_id=workspace_id, entity_id=entity_id)
                TaskDialog.Show("VIKTOR Pull child_data", "Pulled child_data: {}".format(json.dumps(child_data, indent=4)))





                pb.update_progress(3, 3)

                for index, child_entity in enumerate(child_data):
                    all_profile_child_data = []
                    all_tags = []
                    chosen_profile_str = child_data[index]['properties']['input']['chosenprofile']
                    TaskDialog.Show("VIKTOR Pull child_data", "Pulled profile child_data: {}".format(json.dumps(chosen_profile_str, indent=4)))
                    chosen_profile_str = chosen_profile_str.strip('[]')  # Remove the surrounding square brackets
                    profile_list = ast.literal_eval(chosen_profile_str)  # Convert string representation of list to actual list
                    pulled_profile_str = ",".join(map(str, profile_list))

                    # Extract the tag (family instance ID) from the child child_data
                    try:
                        tag = int(child_data[index]['name'])
                    except (KeyError, ValueError):
                        tag = None

                    if tag is None:
                        forms.alert("Could not find valid 'name' in the child_data.", exitscript=True)
                        return

                    # Parsing the profile child_data
                    profile_parts = pulled_profile_str.split(',')
                    conversion_factor = 3.28084/1000  # meters to feet conversion factor
                    profile_child_data = {
                        "h": float(profile_parts[1]) * conversion_factor,
                        "b": float(profile_parts[2]) * conversion_factor,
                        "tw": float(profile_parts[3]) * conversion_factor,
                        "tf": float(profile_parts[4]) * conversion_factor,
                        "r": float(profile_parts[5]) * conversion_factor
                    }
                    all_profile_child_data.append(profile_child_data)
                    all_tags.append(tag)

                # Display the pulled profile child_data in the valueTextBox and a TaskDialog
                self.valueTextBox.Text = str(all_profile_child_data)
                TaskDialog.Show("VIKTOR Pull child_data", "Pulled profile child_data: {}".format(json.dumps(all_profile_child_data, indent=4)))

                # Updating Revit family parameters
                t = Transaction(doc, "Update Beam Profile")
                t.Start()
                for index, elementID  in enumerate(all_tags):
                    family_instance_id = ElementId(elementID)  # Convert to ElementId
                    family_instance = doc.GetElement(family_instance_id)
                    if family_instance:
                        for param_name, param_value in all_profile_child_data[index].items():
                            param = family_instance.LookupParameter(param_name)
                            if param and param.StorageType == StorageType.Double:
                                param.Set(param_value)
                        # Set the Viktor_Change parameter to true
                        viktor_change_param = family_instance.LookupParameter("Viktor_Change")
                        if viktor_change_param and viktor_change_param.StorageType == StorageType.Integer:
                            viktor_change_param.Set(1)  # 1 corresponds to TRUE in Revit's integer parameters
                    t.Commit()

            except ValueError as err:
                forms.alert(str(err), exitscript=True)

        forms.toast(
            "child_data successfully pulled from VIKTOR!",
            title="VIKTOR Pull", appid="VIKTOR"
        )
        self.Close()

if __name__ == '__main__':
    Pullchild_dataWindow().show_dialog()

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

    ### You can customize the code from here to meet your requirements ###
    def pull_button_click(self, sender, args):
        """
        This function is executed when the "Pull" button is clicked in the confirmation window that appears after clicking on the plugin "Pull" button.
        It pulls data from the VIKTOR platform, processes it, and updates the Revit model accordingly.

        Steps:
        1. Pull child entity data from the VIKTOR workspace using the provided resource URL.
        2. Process the pulled data to extract profile information and element IDs.
        3. Inform the user about which Revit element IDs will be updated based on the pulled data.
        4. Update the Revit model using the processed data.

        :param sender: The source of the event
        :param args: The event data
        """
        resource_url = self.resource_url
        set_viktor_doc_data(default_resource_url=self.resource_url)

        with forms.ProgressBar(title="Checking VIKTOR credentials ...", height=50) as pb:
            try:
                child_entities = self.get_viktor_data(resource_url, pb)  # Pull child entity data from the VIKTOR workspace

                all_profile_data, all_element_ids = self.process_child_entities(child_entities, pb)  # Process the pulled VIKTOR child entity data

                # Inform Revit users about which element IDs will be updated based on the pulled data
                self.valueTextBox.Text = str(all_profile_data)
                TaskDialog.Show("VIKTOR Pull Data", "Changes made in the following element IDs: {}".format(json.dumps(all_element_ids, indent=4)))

                self.update_revit_model(all_profile_data, all_element_ids, pb)  # Update the Revit model based on the processed data

            except ValueError as err:
                forms.alert(str(err), exitscript=True)

        forms.toast(
            "Data successfully pulled from VIKTOR!",
            title="VIKTOR Pull", appid="VIKTOR"
        )
        self.Close()

    def get_viktor_data(self, resource_url, pb):
        """
        Connects to the VIKTOR platform and pulls data.
        
        :param resource_url: The resource URL to connect to VIKTOR
        :param pb: Progress bar for visual feedback
        :return: List of child entities from VIKTOR
        """
        pb.title = "Checking VIKTOR credentials ..."
        pb.update_progress(1, 4)
        environment, workspace_id, entity_id = API.parse_resource_url(resource_url)
        token = get_viktor_global_var('VIKTOR_PAT')
        if not token:
            token = ask_for_personal_access_token()

        api = API(environment=environment, token=token)
        api.verify()

        pb.title = "Pulling data from VIKTOR platform ..."
        pb.update_progress(2, 4)

        return api.get_all_child_entity_data(workspace_id=workspace_id, entity_id=entity_id)  # Use get_entity_data() to get all parent entity data instead

    def process_child_entities(self, child_entities, pb):
        """
        Processes child entities to extract profile data and element IDs.
        
        :param child_entities: List of child entities from VIKTOR
        :param pb: Progress bar for visual feedback
        :return: Tuple of all_profile_data and all_element_ids
        """
        pb.title = "Processing child entities ..."
        pb.update_progress(3, 4)
        
        all_profile_data = []
        all_element_ids = []

        for child_entity in child_entities:
            # Extract the chosen profile string from the child entity properties
            chosen_profile_str = child_entity['properties']['input']['chosenprofile']
            # Remove the surrounding square brackets from the profile string
            chosen_profile_str = chosen_profile_str.strip('[]')
            # Convert the string representation of the list into an actual list
            profile_list = ast.literal_eval(chosen_profile_str)
            # Join the list elements into a comma-separated string
            pulled_profile_str = ",".join(map(str, profile_list))

            try:
                # The element ID can be found under the 'name' key within each child entity
                element_id = int(child_entity['name'])
            except (KeyError, ValueError):
                element_id = None

            if element_id is None:
                forms.alert("Could not find valid 'name' in the child data.", exitscript=True)
                return

            # Split the comma-separated string into individual parts
            profile_parts = pulled_profile_str.split(',')
            conversion_factor = 3.28084 / 1000  # Revit API works explicitly with feet, so we have to convert meters to feet
            profile_data = {
                "h": float(profile_parts[1]) * conversion_factor,
                "b": float(profile_parts[2]) * conversion_factor,
                "Tw": float(profile_parts[3]) * conversion_factor,
                "Tf": float(profile_parts[4]) * conversion_factor,
                "r": float(profile_parts[5]) * conversion_factor
            }

            all_profile_data.append(profile_data)
            all_element_ids.append(element_id)

        return all_profile_data, all_element_ids

    def update_revit_model(self, all_profile_data, all_element_ids, pb):
        """
        Updates the Revit model based on profile data and element IDs.
        
        :param all_profile_data: List of profile data dictionaries
        :param all_element_ids: List of element IDs
        :param pb: Progress bar for visual feedback
        """
        pb.title = "Updating Revit model ..."
        pb.update_progress(4, 4)
        
        t = Transaction(doc, "Update Beam Profile")
        t.Start()
        for index, elementID in enumerate(all_element_ids):  # Loop over all the pulled element IDs
            family_instance_id = ElementId(elementID)
            family_instance = doc.GetElement(family_instance_id)  # GetElement is used to select the Revit element, in this case, we are selecting a family instance
            if family_instance:
                for param_name, param_value in all_profile_data[index].items():  # Loop over all the pulled profile data
                    param = family_instance.LookupParameter(param_name)  # LookupParameter can be used to find parameters that match the processed data
                    if param and param.StorageType == StorageType.Double:
                        param.Set(param_value)  # Set the matching parameter's value to the pulled and processed data
                viktor_change_param = family_instance.LookupParameter("Viktor_Change")
                if viktor_change_param and viktor_change_param.StorageType == StorageType.Integer:
                    viktor_change_param.Set(1)  # Set to 1 for TRUE in Revit's integer parameters
        t.Commit()


if __name__ == '__main__':
    PullDataWindow().show_dialog()

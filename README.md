## Revit Push Pull Plugin

### Overview

The Revit Push Pull Plugin is a proof-of-concept tool that demonstrates the integration between Autodesk Revit and the VIKTOR platform. The current implementation is just an example, showcasing one way to utilize the integration. Other implementations are possible and are up to the end user.

This plugin allows you to export an example Revit model to IFC, send it to your VIKTOR workspace, select beam elements, and perform an optimization calculation. After generating optimized profiles for the beams, you can seamlessly pull the updated profile data back into Revit to automatically update the example model.

The implementation of how you process and utilize this data is flexible and customizable, allowing you to adapt it to your specific needs.

### Installation

#### Revit Plugin Installation
Instructions on how to install the Revit plugin can be found in `revitcentral\Revit plugins\Plugin installation Readme.txt`.
The example Revit model can be found in `revitcentral\Viktor_test_project.rvt`.

#### VIKTOR App Installation
1. **Clone the Repository**:
    ```bash
    git clone https://github.com/SvenDeLeau/revitcentral.git
    cd revitcentral
    ```

2. **Install the VIKTOR SDK**:
    Follow the instructions in the [VIKTOR Documentation](https://docs.viktor.ai/docs) to install the VIKTOR SDK and set up your development environment.

3. **Install the VIKTOR App**:
    - Navigate to the directory containing the VIKTOR app.
    - Run the following command to install the VIKTOR app:
      ```bash
      viktor-cli install
      ```

4. **Deploy the VIKTOR App**:
    - After installing, start the app to your VIKTOR workspace:
      ```bash
      viktor-cli start
      ```

5. **Set Up VIKTOR API Credentials**:
    - Ensure you have the necessary API credentials set up to interact with the VIKTOR platform. Refer to the [VIKTOR API Documentation](https://docs.viktor.ai/docs/api/getting-started) for details.

### Customization and Implementation

This plugin serves as a proof of concept. The core functionality demonstrates that it is possible to push model data to VIKTOR and pull VIKTOR data into Revit. The example provided shows how to update beam profiles, but the implementation of how you process and utilize this data is left to the end user. You can customize the code to meet your specific requirements and workflow.


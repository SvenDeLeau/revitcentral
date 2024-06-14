import os
import sys

# isort: off
# isort: on
# pylint: disable=wrong-import-position

import platform

# VIKTOR imports
from viktor import InitialEntity

# Local imports
from .project.controller import ProjectController
from .revitcentral.controller import RevitCentralController
from .Beam.beamcontroller import BeamController

initial_entities = [
    InitialEntity(
        "ProjectController",
        name="Project",
        children=[
            InitialEntity("RevitCentralController", name="RevitCentralConverter"),
        ],
    )
]

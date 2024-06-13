from viktor.core import ViktorController

class ProjectController(ViktorController):

    viktor_convert_entity_field = True

    label = 'Project'
    children = ['RevitCentralController']
    show_children_as = 'Table'

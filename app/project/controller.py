from viktor.core import ViktorController

class ProjectController(ViktorController):

    viktor_convert_entity_field = True

    label = 'Project'
    children = ['SciaConverterController']
    show_children_as = 'Table'

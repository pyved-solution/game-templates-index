import random
from . import entities
from . import processors_ingame
from . import processors_menu
from . import glvars
from .glvars import pyv, ecs

"""
>>mini docs for esper/ecs<<

.create_entity()
.delete_entity(entity)
.add_component(entity, component_instance)
.remove_component(entity, ComponentType)

.try_component(entity, ComponentType)
.get_component(ComponentType)
.get_components(ComponentTypeA, ComponentTypeB, Etc)
.component_for_entity(entity, ComponentType)
.components_for_entity(entity)
.has_component(entity, ComponentType)

.add_processor(processor_instance)
.remove_processor(ProcessorType)
.process()
"""


def auto_add_processors(module_name):
    processor_objects = [
        getattr(module_name, cls)() for cls in module_name.__all__
    ]
    for processor in processor_objects:
        ecs.add_processor(processor)


# ...The three canonical gamedef functions
# -------------------------------
@pyv.declare_begin
def init_game(vmst=None):
    pyv.init(wcaption='Pyv Breaker')
    glvars.screen = s_obj = pyv.get_surface()
    glvars.set_scr_size(s_obj.get_size())
    glvars.font = pyv.new_font_obj(None, glvars.classic_ftsize)

    ecs.switch_world('ingame')
    entities.build_ingame_entities()
    auto_add_processors(processors_ingame)

    # switch to "menu" gamestate and do the same
    ecs.switch_world('menu')
    glvars.menu_message = glvars.font.render('Click anywhere to start a new game', True, 'black')
    auto_add_processors(processors_menu)


@pyv.declare_update
def upd(time_info=None):
    if glvars.prev_time_info is None:
        glvars.prev_time_info = time_info
    else:
        dt = (time_info - glvars.prev_time_info)
        glvars.prev_time_info = time_info
        ecs.process(dt)
        pyv.flip()


@pyv.declare_end
def done(vmst=None):
    pyv.close_game()
    print('gameover!')

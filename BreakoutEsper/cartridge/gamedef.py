from . import shared
from . import systems
from .world import blocks_create, player_create, ball_create
from .glvars import pyv, esper

pygame = pyv.pygame


# ---------------- tout ca pour esper -------
class Position:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y


class Renderable:
    def __init__(self):
        self.size = 18
        self.thickness = 3


class EventProcessor(esper.Processor):
    def process(self, *args, **kwargs) -> None:
        ev_li = pygame.event.get()
        for ev in ev_li:
            if ev.type == pygame.QUIT:
                pyv.vars.gameover = True

        all_pkeys = pygame.key.get_pressed()

        pairs = esper.get_component(Position)  # returns iterator for entity,component pairs
        offset = 4
        pt = pairs[0][1]
        if all_pkeys[pygame.K_DOWN]:
            pt.y += offset
        elif all_pkeys[pygame.K_UP]:
            pt.y -= offset

        elif all_pkeys[pygame.K_LEFT]:
            pt.x -= offset
        elif all_pkeys[pygame.K_RIGHT]:
            pt.x += offset

        if all_pkeys[pygame.K_SPACE]:
            print(pt.x, pt.y)


class GfxProcessor(esper.Processor):
    def __init__(self):
        self._scr = pyv.get_surface()

    def process(self, *args, **kwargs) -> None:
        self._scr.fill('antiquewhite2')
        for ent, (rend, pos) in esper.get_components(Renderable, Position):
            pygame.draw.circle(self._scr, 'orange', (pos.x, pos.y), rend.size, rend.thickness)


@pyv.declare_begin
def init_game(vmst=None):
    pyv.init()
    screen = pyv.get_surface()
    shared.screen = screen
    pyv.init(wcaption='Pyv Breaker')
    print('ecs?', esper)
    print(' +-------------------------+ ')
    # pyv.define_archetype('player', ('body', 'speed', 'controls'))
    # pyv.define_archetype('block', ('body', ))
    # pyv.define_archetype('ball', ('body', 'speed_Y', 'speed_X'))

    # blocks_create()
    # player_create()
    # ball_create()

    # pyv.bulk_add_systems(systems)

    # -----------------

    # do all the ecs stuff
    esper.switch_world('intro')

    print(esper.list_worlds())

    player = esper.create_entity()
    esper.add_component(player, Renderable())
    esper.add_component(player, Position(x=5, y=5))

    esper.add_processor(EventProcessor())
    esper.add_processor(GfxProcessor())
    # ------------------
    #  mini docs
    # ------------------
    # World.create_entity()
    # World.delete_entity(entity)
    # World.add_processor(processor_instance)
    # World.remove_processor(ProcessorType)
    # World.add_component(entity, component_instance)
    # World.remove_component(entity, ComponentType)
    # World.get_component(ComponentType)
    # World.get_components(ComponentTypeA, ComponentTypeB, Etc)
    # World.component_for_entity(entity, ComponentType)
    # World.components_for_entity(entity)
    # World.has_component(entity, ComponentType)
    # World.process()


@pyv.declare_update
def upd(time_info=None):

    # if shared.prev_time_info:
    #     dt = (time_info - shared.prev_time_info)
    # else:
    #     dt = 0
    # shared.prev_time_info = time_info
    # pyv.get_surface().fill('orange')
    # pyv.systems_proc(dt)

    ev_li = pygame.event.get()
    for ev in ev_li:
        if ev.type == pygame.QUIT:
            pyv.vars.gameover = True
    esper.process()
    pyv.flip()


@pyv.declare_end
def done(vmst=None):
    pyv.close_game()
    print('gameover!')

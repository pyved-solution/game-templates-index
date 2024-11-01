from . import shared
from . import actors
from . import glvars
from .actors import *


pyv = glvars.pyv
pyv.bootstrap_e()


def _prep_images():
    Sprsheet = pyv.gfx.Spritesheet
    grid_rez = (32, 32)
    # tileset:
    img = pyv.vars.images['tileset']
    glvars.tileset = Sprsheet(img, 2)  # use upscaling x2
    glvars.tileset.set_infos(grid_rez)
    # player:
    img = pyv.vars.images['avatar1']
    planche_avatar = Sprsheet(img, 2)  # upscaling x2
    planche_avatar.colorkey = (255, 0, 255)  # TODO in web ctx i dont know if this works
    planche_avatar.set_infos(grid_rez)
    glvars.avatar_img = planche_avatar.image_by_rank(0)
    # monster:
    mstr_img = pyv.vars.images['monster']
    glvars.monster_img = pyv.pygame.transform.scale(mstr_img, (32, 32))
    glvars.monster_img.set_colorkey((255, 0, 255))


def init(vmst=None):
    pyv.init(wcaption='Roguelike actor-based')
    shared.screen = pyv.get_surface()
    _prep_images()

    # - prev code style

    # pyv.define_archetype('player', (
    #     'position', 'controls', 'body', 'damages', 'health_point', 'enter_new_map'
    # ))
    # pyv.define_archetype('wall', ('body',))
    # pyv.define_archetype('monster', ('position', 'damages', 'health_point', 'active'))
    # pyv.define_archetype('exit', ('position',))
    # pyv.define_archetype('potion', ('position', 'effect',))
    # world.create_player()
    # world.create_exit()
    # world.create_potion()
    # world.init_images()
    # pyv.bulk_add_systems(systems)

    glvars.maze_id = maze.new_maze()
    pl_id = player.new_player()

    # pl will be added LATER, when spawned
    # pl_data = pyv.actor_state(pl_id)
    # pl_pos = pl_data.x, pl_data.y
    # pyv.actor_exec(maze.maze_id, 'add_player', pl_id, pl_pos)

    pyv.post_ev('req_regen_maze')


def update(curr_t=None):
    # when using evsys4, it was...
    # pyv.systems_proc()

    # now using evsys6
    # bind old ev system to evsys6
    for ev in pyv.evsys0.get():
        if ev.type == pyv.evsys0.QUIT:
            pyv.vars.gameover = True
        elif ev.type == pyv.evsys0.KEYDOWN:
            if ev.key == pyv.evsys0.K_ESCAPE:
                pyv.vars.gameover = True
            elif ev.key == pyv.evsys0.K_SPACE:
                pyv.post_ev('req_regen_maze')
            elif ev.key == pyv.evsys0.K_LEFT:
                pyv.post_ev("req_move_avatar", dir="left")
            elif ev.key == pyv.evsys0.K_RIGHT:
                pyv.post_ev("req_move_avatar", dir="right")
            elif ev.key == pyv.evsys0.K_UP:
                pyv.post_ev("req_move_avatar", dir="up")
            elif ev.key == pyv.evsys0.K_DOWN:
                pyv.post_ev("req_move_avatar", dir="down")

    pyv.post_ev('update', info_t=curr_t)
    pyv.post_ev('draw', screen=pyv.vars.screen)
    pyv.process_events()

    pyv.flip()


def close(vmst=None):
    pyv.close_game()
    print('roguelike: over')

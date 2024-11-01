import random
from . import glvars
from . import shared
from . import world


__all__ = [
    'pg_event_proces_sys',
    'world_generation_sys',
    'gamestate_update_sys',
    'rendering_sys',
    'physics_sys',
    'monster_ai_sys'
]


# aliases
pyv = glvars.pyv
pg = pyv.pygame
Sprsheet = pyv.gfx.Spritesheet
BoolMatrx = pyv.struct.BoolMatrix


# global vars
tileset = None
saved_player_pos = [None, None]


def pg_event_proces_sys():
    if shared.end_game_label0:
        for ev in pg.event.get():
            if ev.type == pg.KEYDOWN and ev.key == pg.K_ESCAPE:
                pyv.vars.gameover = True
        return
    avpos = pyv.find_by_archetype('player')[0]['position']
    for ev in pg.event.get():
        if ev.type == pg.KEYDOWN:
            if ev.key == pg.K_ESCAPE:
                pyv.vars.gameover = True
            elif ev.key == pg.K_UP:
                avpos[1] -= 1
                _player_push(1)
            elif ev.key == pg.K_DOWN:
                avpos[1] += 1
                _player_push(3)

            elif ev.key == pg.K_LEFT:
                avpos[0] -= 1
                _player_push(2)

            elif ev.key == pg.K_RIGHT:
                avpos[0] += 1
                _player_push(0)

            elif ev.key == pg.K_SPACE:
                # use flag so we we'll reset level, soon in the future
                player = pyv.find_by_archetype('player')[0]
                player['enter_new_map'] = True


def gamestate_update_sys():
    player = pyv.find_by_archetype('player')[0]
    classic_ftsize = 38
    if player.health_point <= 0 and (shared.end_game_label0 is None):
        ft = pyv.pygame.font.Font(None, classic_ftsize)
        shared.end_game_label0 = ft.render('Game Over', True, (255, 255, 255), 'black')
        shared.end_game_label1 = ft.render(f'You reached Level : {shared.level_count}', True, (255, 255, 255), 'black')


def rendering_sys():
    global tileset
    scr = shared.screen

    # - rest of the drawing
    if shared.end_game_label0:
        lw, lh = shared.end_game_label0.get_size()
        scr.blit(
            shared.end_game_label0, ((shared.SCR_WIDTH - lw) // 2, (shared.SCR_HEIGHT - lh) // 3)
        )
        scr.blit(
            shared.end_game_label1, ((shared.SCR_WIDTH - lw) // 2, (shared.SCR_HEIGHT - lh) // 2)
        )
        return
    _draw_all_mobs(scr)


def physics_sys():
    """
    implements the monster attack mechanic
    + it also proc any effect on the player based on what happened (potion, exit door etc)
    """
    player = pyv.find_by_archetype('player')[0]
    monster = pyv.find_by_archetype('monster')
    exit_ent = pyv.find_by_archetype('exit')[0]
    potion = pyv.find_by_archetype('potion')[0]

    for m in monster:
        if m.position == player.position:
            m.health_point -= player.damages
            player.health_point -= m.damages
            if m.health_point < 0:
                pyv.delete_entity(m)

    if player.position == exit_ent.position:
        player['enter_new_map'] = True
        shared.level_count += 1
        print('YOU REACHED LEVEL : ' + str(shared.level_count))

    if player.position == potion.position:
        if potion.effect == 'Heal':
            player.health_point = 100
            print(player.health_point)
            potion.effect = 'disabled'
        elif potion.effect == 'Poison':
            player.health_point -= 20
            print(player.health_point)
            potion.effect = 'disabled'


# ----------------------------
#  private/utility functions
# ----------------------------
def _draw_all_mobs(scrref):
    player = pyv.find_by_archetype('player')[0]
    all_mobs = pyv.find_by_archetype('monster')
    # ----------
    #  draw player/enemies
    # ----------
    av_i, av_j = player['position']
    exit_ent = pyv.find_by_archetype('exit')[0]
    potion = pyv.find_by_archetype('potion')[0]
    tuile = shared.TILESET.image_by_rank(912)
    if shared.game_state['visibility_m'].get_val(*exit_ent.position):
        scrref.blit(shared.TILESET.image_by_rank(1092),
                    (exit_ent.position[0] * shared.CELL_SIDE, exit_ent.position[1] * shared.CELL_SIDE, 32, 32))

    if shared.game_state['visibility_m'].get_val(*potion.position):
        if potion.effect == 'Heal':
            scrref.blit(shared.TILESET.image_by_rank(810),
                        (potion.position[0] * shared.CELL_SIDE, potion.position[1] * shared.CELL_SIDE, 32, 32))
        elif potion.effect == 'Poison':
            scrref.blit(shared.TILESET.image_by_rank(810),
                        (potion.position[0] * shared.CELL_SIDE, potion.position[1] * shared.CELL_SIDE, 32, 32))

    # fait une projection coordonnées i,j de matrice vers targx, targy coordonnées en pixel de l'écran
    proj_function = (lambda locali, localj: (locali * shared.CELL_SIDE, localj * shared.CELL_SIDE))
    targx, targy = proj_function(av_i, av_j)
    scrref.blit(shared.AVATAR, (targx, targy, 32, 32))
    # ----- enemies
    # for enemy_info in shared.game_state["enemies_pos2type"].items():
    for mob_ent in all_mobs:
        pos = mob_ent.position
        # pos, t = enemy_info
        if not shared.game_state['visibility_m'].get_val(*pos):
            continue
        en_i, en_j = pos[0] * shared.CELL_SIDE, pos[1] * shared.CELL_SIDE
        scrref.blit(shared.MONSTER, (en_i, en_j, 32, 32))

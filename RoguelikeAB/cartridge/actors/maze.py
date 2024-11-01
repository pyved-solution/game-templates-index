"""
contains: maze generation,
here we also defin the "maze" actor
"""
from .misc import *
from ..glvars import pyv
from .. import glvars


MAP_W, MAP_H = 24, 24  # these dimensions match map size that is,
# the size of: actor_state(maze_actor).content


# in case you need to access very ofter to data, you can declare this:
def get_maze_data():
    if glvars.maze_id is None:
        raise ValueError('tryin to access maze data, while the maze actor hasnt been created yet!')
    return pyv.actor_state(glvars.maze_id)


def new_maze():
    data = {
        'content': None,  # will contain a special item created by pyv
        'visibility_map': None,
        'player_id': None,
        'exit_actor': None,
        'monster_li': []
    }

    # - utility
    def get_terrain(this):  # like a handy alias
        obj = this.content  # type: pyv.terrain.RandomMaze
        return obj.getMatrix()

    def update_vision(this, av_pos):
        if not glvars.fov_computer:
            glvars.fov_computer = pyv.rogue.FOVCalc()
        i, j = av_pos
        this.visibility_map.set_val(i, j, True)  # av_pos always visible!

        def func_visibility(a, b):
            if this.visibility_map.is_out(a, b):
                return False
            if get_terrain(this).get_val(a, b) is None:  # cannot see through walls
                return False
            return True

        li_visible = glvars.fov_computer.calc_visible_cells_from(i, j, glvars.VISION_RANGE, func_visibility)
        for cell in li_visible:
            this.visibility_map.set_val(cell[0], cell[1], True)

    def request_player_spawn(this, new_player_pos):
        pyv.post_ev('spawn', pos=new_player_pos)

    def can_see(this, cell) -> bool:
        return this.visibility_map.get_val(*cell)

    def list_walkable_cells():  # static
        walkable_cells = list()
        for i in range(MAP_W):
            for j in range(MAP_H):
                walkable_cells.append((i, j))
        return walkable_cells

    def run_map_regen(this):
        # reset old map:
        if this.exit_actor:
            pyv.del_actor(this.exit_actor)

        #pl_ent = pyv.find_by_archetype('player')[0]
        #monsters = pyv.find_by_archetype('monster')
        #potion = pyv.find_by_archetype('potion')[0]
        #exit_ent = pyv.find_by_archetype('exit')[0]

        # why so?
        #if pl_ent['enter_new_map']:
        #    pl_ent['enter_new_map'] = False
        #    print('Level generation...')

        this.content = pyv.rogue.RandomMaze(MAP_W, MAP_H, min_room_size=3, max_room_size=5)
        # print(shared.game_state['rm'].blocking_map)

        # IMPORTANT: adding mobs comes before computing the visibility
        # shared.game_state["enemies_pos2type"].clear()
        # for monster in monsters:
        #     pyv.delete_entity(monster)
        # for _ in range(5):
        #     tmp = shared.random_maze.pick_walkable_cell()
        #     pos_key = tuple(tmp)
        #     shared.game_state["enemies_pos2type"][pos_key] = 1  # all enemies type=1
        #     world.create_monster(tmp)

        # - reset the visibility
        this.visibility_map = pyv.struct.BoolMatrix((MAP_W, MAP_H))
        this.visibility_map.set_all(False)
        this.walkable_cells = []
        pl_spawn = this.content.pick_walkable_cell()
        # TODO tp the player ??

        # pyv.find_by_archetype('player')[0]['position'] =
        # world.update_vision_and_mobs(
        #     pyv.find_by_archetype('player')[0]['position'][0],
        #     pyv.find_by_archetype('player')[0]['position'][1]
        # )
        request_player_spawn(this, pl_spawn)
        # update_vision(this)

        # extra entity: the level exit
        forbidden_loc = [
            pl_spawn,
            # what about monsters??
        ]
        while True:
            exit_test_pos = this.content.pick_walkable_cell()
            if exit_test_pos not in forbidden_loc:
                this.exit_actor = new_rogue_entity(exit_test_pos, False)
                this.exit_pos = exit_test_pos
                print('exit created @', this.exit_pos)
                break

        # while True:
        #     resultat = random.randint(0, 1)
        #     potionPos = shared.random_maze.pick_walkable_cell()
        #     if potionPos not in [pl_ent.position] + [monster.position for monster in monsters] + [
        #         exit_ent.position]:
        #         potion.position = potionPos
        #         if resultat == 0:
        #             potion.effect = 'Heal'
        #         else:
        #             potion.effect = 'Poison'
        #         break

    # - behavior
    def on_avatar_moves(this, ev):
        update_vision(this, ev.pos)

    def on_req_regen_maze(this, ev):
        print('*RECEPTION req_regen_maze* -', ev.__dict__)
        run_map_regen(this)

    def on_draw(this, ev):
        scr = ev.screen
        scr.fill(glvars.WALL_COLOR)
        # ----------
        #  draw tiles
        # ----------
        nw_corner = (0, 0)
        tmp_r4 = [None, None, None, None]
        # si tu veux afficher du sol, vraiment du sol
        # tuile = shared.TILESET.image_by_rank(912)
        dim = get_terrain(this).get_size()
        for i in range(dim[0]):
            for j in range(dim[1]):
                # ignoring walls
                matrix = get_terrain(this).get_val(i, j)
                if matrix is None:
                    continue
                tmp_r4[0], tmp_r4[1] = nw_corner
                tmp_r4[0] += i * glvars.CELL_SIDE
                tmp_r4[1] += j * glvars.CELL_SIDE
                tmp_r4[2] = tmp_r4[3] = glvars.CELL_SIDE
                if not can_see(this, (i, j)):  # hidden cell
                    pyv.draw_rect(scr, glvars.HIDDEN_CELL_COLOR, tmp_r4)
                else:  # visible tile
                    # texture:
                    # scr.blit(tuile, tmp_r4)
                    pyv.draw_rect(scr, glvars.CELL_COLOR, tmp_r4)
                    glvars.walkable_cells.append((i, j))

    return pyv.new_actor('maze', locals())

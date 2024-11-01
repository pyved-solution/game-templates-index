"""
we defined all actors for Roguelike here,
apart from the "maze" that goes to a dedicated file
"""
from .glvars import pyv
from . import glvars
from . import maze


def new_potion():
	data = {}

	return pyv.new_actor('potion', locals())


def new_player():
	data = {
		'x': 15, 'y': 15
	}

	# - utils
	def player_push(this, directio):
		# player = pyv.find_by_archetype('player')[0]
		# monsters = pyv.find_by_archetype('monster')  # TODO kick mobs? missing feat.
		# print(glvars.walkable_cells)
		future_pos = [this.x, this.y]
		deltas = {
			'right': (+1, 0),  # right
			'up': (0, -1),  # up
			'left': (-1, 0),  # left
			'down': (0, +1)   # down
		}
		future_pos[0] += deltas[directio][0]  # why this sign?
		future_pos[1] += deltas[directio][1]
		if tuple(future_pos) not in glvars.walkable_cells:  # bad name?
			# TODO kick event
			pass
		else:
			# commit new pos =>Update player vision
			this.x, this.y = future_pos
			pyv.post_ev('avatar_moves', pos=(this.x, this.y))
		# world.update_vision_and_mobs(player.position[0], player.position[1])

	# - behavior
	def on_spawn(this, ev):
		this.x, this. y = ev.pos
		pyv.post_ev('avatar_moves', pos=(this.x, this.y))

	def on_req_move_avatar(this, ev):
		print('reception', ev.__dict__)
		# TODO collision detection
		if ev.dir not in ('right', 'down', 'left', 'up'):
			return
		print('attemptin to move...')
		player_push(this, ev.dir)

	def on_draw(this, ev):
		scr = ev.screen
		# >>> player = pyv.find_by_archetype('player')[0]
		# all_mobs = pyv.find_by_archetype('monster')
		# ----------
		#  draw player/enemies
		# ----------
		av_i, av_j = this.x, this.y
		exit_i, exit_j = 23, 20
		# exit_ent = pyv.find_by_archetype('exit')[0]
		# potion = pyv.find_by_archetype('potion')[0]
		# tuile = shared.TILESET.image_by_rank(912)

		# ->draw exit
		if pyv.actor_state(maze.maze_id).visibility_map.get_val(exit_i, exit_j):
			scr.blit(glvars.tileset.image_by_rank(1092),
						(exit_i * glvars.CELL_SIDE, exit_j * glvars.CELL_SIDE, 32, 32))

		# ->draw potions
		# if shared.game_state['visibility_m'].get_val(*potion.position):
		# 	if potion.effect == 'Heal':
		# 		scrref.blit(shared.TILESET.image_by_rank(810),
		# 					(potion.position[0] * shared.CELL_SIDE, potion.position[1] * shared.CELL_SIDE, 32, 32))
		# 	elif potion.effect == 'Poison':
		# 		scrref.blit(shared.TILESET.image_by_rank(810),
		# 					(potion.position[0] * shared.CELL_SIDE, potion.position[1] * shared.CELL_SIDE, 32, 32))

		# fait une projection coordonnées i,j de matrice vers targx, targy coordonnées en pixel de l'écran
		proj_function = lambda locali, localj: (locali * glvars.CELL_SIDE, localj * glvars.CELL_SIDE)
		targx, targy = proj_function(av_i, av_j)
		scr.blit(glvars.avatar_img, (targx, targy, 32, 32))
		# ----- enemies
		# for enemy_info in shared.game_state["enemies_pos2type"].items():
		# for mob_ent in all_mobs:
		# 	pos = mob_ent.position
		# 	# pos, t = enemy_info
		# 	if not shared.game_state['visibility_m'].get_val(*pos):
		# 		continue
		# 	en_i, en_j = pos[0] * shared.CELL_SIDE, pos[1] * shared.CELL_SIDE
		# 	scrref.blit(shared.MONSTER, (en_i, en_j, 32, 32))

	return pyv.new_actor('player', locals())


# -------------- rogue_entity(can be: exit, potion, mob...) -------------------
def new_rogue_entity(pos, is_mob):
	data = {
		'x': pos[0], 'y': pos[1],
		'is_mob': is_mob
	}

	# - behavior
	def on_player_moves(this, ev):
		if not this.is_mob:
			return
		i, j = this.ref_player.old_pos
		player = pyv.find_by_archetype('player')[0]
		curr_pos = player.position

		if (i is None) or curr_pos[0] != i or curr_pos[1] != j:
			# position has changed!
			saved_player_pos[0], saved_player_pos[1] = curr_pos
			blockmap = pyv.actor_state(maze_id).blocking_map
			allmobs = pyv.find_by_archetype('monster')
			for mob_ent in allmobs:
				if not mob_ent.active:
					pass
				else:
					pathfinding_result = pyv.terrain.DijkstraPathfinder.find_path(
						blockmap, mob_ent.position, player.position
					)
					if len(pathfinding_result) > 1:  # if player moved first, he may already be on the same pos as the monster
						new_pos = pathfinding_result[1]  # index 1 --> 1 step forward!
						mob_ent.position[0], mob_ent.position[1] = new_pos  # TODO a proper "kick the player" feat.

	def on_draw(this, ev):
		pyv.draw_circle(ev.screen, 'red', (glvars.CELL_SIDE*this.x, glvars.CELL_SIDE*this.y), 8)

	return pyv.new_actor('rogue_entity', locals())

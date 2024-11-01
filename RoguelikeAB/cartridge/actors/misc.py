"""
we actors for the Roguelike here,
except from "maze" and "player" that have their own file
"""
from ..glvars import pyv
from .. import glvars


def new_potion():
	data = {}

	return pyv.new_actor('potion', locals())


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

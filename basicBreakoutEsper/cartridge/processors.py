from .glvars import pyv, ecs
from .components import *
from . import glvars


__all__ = [
	'EventProc',
	'EndgameProc',
	'PhysicsProc',
	'GraphicsProc'
]


class EventProc(ecs.Processor):
    def process(self, *args, **kwargs) -> None:
        ev_manager = pyv.legacy_evs

        for ev in ev_manager.get():
            if ev.type == ev_manager.QUIT:
                pyv.vars.gameover = True
            elif ev.type == ev_manager.KEYDOWN:
                if ev.key == ev_manager.K_ESCAPE:
                    pyv.vars.gameover = True
                elif ev.key == ev_manager.K_SPACE:
                    ball_sp = ecs.try_component(glvars.ball_entity, Speed)
                    if glvars.start_game_label:
                        glvars.start_game_label = None
                    else:
                        print('ball accelerates')
                        ball_sp.vy *= 1.08  # boost ball speed when pressing space

        all_pkeys = ev_manager.pressed_keys()
        sp_compo = ecs.try_component(glvars.player_entity, Speed)
        if all_pkeys[ev_manager.K_LEFT]:
            sp_compo.vx = -1 * glvars.PLAYER_SPEED
        elif all_pkeys[ev_manager.K_RIGHT]:
            sp_compo.vx = glvars.PLAYER_SPEED
        else:
            sp_compo.vx = 0.0


class EndgameProc(ecs.Processor):
    def process(self, *args, **kwargs):
        li_pairs = ecs.get_component(BlockSig)
        bpy = ecs.try_component(glvars.ball_entity, Body).to_rect().top

        # player has destroyed all blocks
        if len(li_pairs) == 0:  # no more blocks left
            ft = pyv.new_font_obj(None, glvars.classic_ftsize)
            glvars.end_game_label = ft.render('VICTORY!', True, 'white')

        elif bpy > glvars.scr_size[1]:  # player has lost the ball
            ft = pyv.new_font_obj(None, glvars.classic_ftsize)
            glvars.end_game_label = ft.render('GAME OVER', True, 'white')


class PhysicsProc(ecs.Processor):
    def process(self, *args, **kwargs):
        # blocks all movement if the game is over/ hasnt started yet
        if glvars.start_game_label:
            return
        if glvars.end_game_label:
            return

        dt = args[0]
        SX, SY = glvars.scr_size

        # PLAYER MOVEMENT
        pl_body = ecs.try_component(glvars.player_entity, Body)
        px, py = pl_body.x, pl_body.y
        plwidth = pl_body.w

        sp_compo = ecs.try_component(glvars.player_entity, Speed)

        targetx = px + sp_compo.vx * dt
        if not (targetx < 0 or targetx > (SX-plwidth)):
            pl_body.x = targetx

        # BALL MVT
        ball_body = ecs.try_component(glvars.ball_entity, Body)
        ball_speed = ecs.try_component(glvars.ball_entity, Speed)

        bpx, bpy = ball_body.x, ball_body.y
        ball_body.x = bpx + dt*ball_speed.vx
        ball_body.y = bpy + dt*ball_speed.vy

        if bpx < 0:
            ball_speed.vx *= -1
            ball_body.x = 0
        elif ball_body.to_rect().right > SX:
            ball_speed.vx *= -1
            ball_body.to_rect().right = SX
            ball_body.commit()
        if bpy < 0:
            ball_speed.vy *= -1
            ball_body.to_rect().top = 0
            ball_body.commit()

        # Collision vs player
        pl_speed = ecs.try_component(glvars.player_entity, Speed)
        if pl_body.to_rect().colliderect(ball_body.to_rect()):
            ball_body.to_rect().bottom = pl_body.to_rect().top  # stick to the pad
            ball_body.commit()
            ball_speed.vy *= -1
            if pl_speed.vx > 0:
                ball_speed.vx += 25  # brush Right
            elif pl_speed.vx < 0:
                ball_speed.vx -= 25  # brush Left
            # - debug: collisions with player
            # print(ball_speed.vx)

        # Collision vs block
        # ######################Collision block
        bl_to_crush = set()
        ball_rect = ball_body.to_rect()
        for ent, ref_body in ecs.get_component(Body):
            if ent not in (glvars.ball_entity, glvars.player_entity):
                block_rect = ref_body.to_rect()
                if ball_rect.colliderect(block_rect):
                    bl_to_crush.add(ent)

        if len(bl_to_crush):
            ball_speed.vy *= -1
        for z_entity in bl_to_crush:
            ecs.delete_entity(z_entity)


class GraphicsProc(ecs.Processor):
    def __init__(self):
        self._scr = pyv.get_surface()

    def process(self, *args, **kwargs) -> None:
        # bg color
        self._scr.fill('black')

        # draw player and ball
        for ent, body in ecs.get_component(Body):
            if ent == glvars.player_entity:  # draw player
                pyv.draw_rect(self._scr, 'white', body.to_rect())
            elif ent == glvars.ball_entity:  # draw ball
                pyv.draw_rect(self._scr, 'blue', ecs.try_component(ent, Body).to_rect())
            else:  # blocks
                pygrect = ecs.try_component(ent, Body).to_rect()
                pyv.draw_rect(
                    self._scr,
                    glvars.interpolate_color(pygrect[0], pygrect[1]), pygrect
                )

        # draw msg on screen, for the start / the end game
        scr_w, scr_h = glvars.scr_size
        for label in (glvars.start_game_label, glvars.end_game_label):
            if label is not None:
                lw, lh = label.get_size()
                self._scr.blit(
                    label, ((scr_w-lw)//2, (scr_h-lh)//2)
                )

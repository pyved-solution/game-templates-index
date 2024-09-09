"""
the file contains all classes used to implement the ECS pattern
"""
from . import glvars
from .glvars import pyv, ecs


pygame = pyv.pygame


class Speed:
    def __init__(self, vx=0.0, vy=0.0):
        self.vx = vx
        self.vy = vy


class Controls:
    def __init__(self):
        self.right = self.left = False


class Body:
    def __init__(self, x, y, w, h):
        self._x, self._y, self.w, self.h = x, y, w, h
        self._cached_rect = pygame.Rect(self.x, self.y, self.w, self.h)

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, val):
        self._y = val
        self._cached_rect = pygame.Rect(self._x, self._y, self.w, self.h)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, val):
        self._x = val
        self._cached_rect = pygame.Rect(self._x, self._y, self.w, self.h)

    def to_rect(self):
        return self._cached_rect

    def commit(self):
        # use the cached rect (has been modified) to update other values
        self._x, self.y = self._cached_rect.topleft


class EventProcessor(ecs.Processor):
    def process(self, *args, **kwargs) -> None:
        ev_li = pygame.event.get()
        for ev in ev_li:
            if ev.type == pygame.QUIT:
                pyv.vars.gameover = True

        all_pkeys = pygame.key.get_pressed()

        # pairs = ecs.get_component(Position)  # returns iterator for entity,component pairs
        sp_compo = ecs.try_component(glvars.player_entity, Speed)

        offset = 4

        # if all_pkeys[pygame.K_DOWN]:
        #     pt.y += offset
        # elif all_pkeys[pygame.K_UP]:
        #     pt.y -= offset

        if all_pkeys[pygame.K_LEFT]:
            sp_compo.value = -1 * glvars.PLAYER_SPEED
        elif all_pkeys[pygame.K_RIGHT]:
            sp_compo.value = glvars.PLAYER_SPEED
        else:
            sp_compo.value = 0.0


class PhysicsProcessor(ecs.Processor):
    def process(self, *args, **kwargs):
        dt = args[0]
        SX, SY = glvars.scr_size

        # PLAYER MOVEMENT
        pl_body = ecs.try_component(glvars.player_entity, Body)
        px, py = pl_body.x, pl_body.y
        plwidth = pl_body.w

        sp_compo = ecs.try_component(glvars.player_entity, Speed)

        targetx = px + sp_compo.value * dt
        if not (targetx < 0 or targetx > (SX-plwidth)):
            pl_body.x = targetx

        # BALL MVT
        ball_body = ecs.try_component(glvars.ball_entity, Body)
        speed = ecs.try_component(glvars.ball_entity, Speed)

        bpx, bpy = ball_body.x, ball_body.y
        ball_body.x = bpx + dt*speed.vx
        ball_body.y = bpy + dt*speed.vy

        if bpx < 0:
            speed.vx *= -1
            ball_body.x = 0
        elif ball_body.to_rect().right > SX:
            speed.vx *= -1
            ball_body.to_rect().right = SX
            ball_body.commit()
        if bpy < 0:
            speed.vy *= -1
            ball_body.to_rect().top = 0
            ball_body.commit()

        # Collision vs player
        if pl_body.to_rect().colliderect(ball_body.to_rect()):
            ball_body.to_rect().bottom = pl_body.to_rect().top  # stick to the pad
            ball_body.commit()
            speed.vy *= -1

        # Collision vs block
        # ######################Collision block
        to_crush = None
        ball_rect = ball_body.to_rect()
        for ent, ref_body in ecs.get_component(Body):
            if ent not in (glvars.ball_entity, glvars.player_entity):
                block_rect = ref_body.to_rect()
                if ball_rect.colliderect(block_rect):
                    to_crush = ent
                    break
        if to_crush:
            speed.vy *= -1
            ecs.delete_entity(to_crush)


class GfxProcessor(ecs.Processor):
    def __init__(self):
        self._scr = pyv.get_surface()

    def process(self, *args, **kwargs) -> None:
        # bg color
        self._scr.fill('black')

        # draw player and ball
        for ent, body in ecs.get_component(Body):
            if ent == glvars.player_entity:
                pygame.draw.rect(self._scr, 'orange', body.to_rect())
            else:  # ball
                pyv.draw_rect(self._scr, 'blue', ecs.try_component(ent, Body).to_rect())

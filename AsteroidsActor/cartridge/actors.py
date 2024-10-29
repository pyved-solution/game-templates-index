"""
game actors actor
"""
from .glvars import deg, pyv
import math
import random


__all__ = [
    'new_ship',
    'new_rockfield'
]

pygame = pyv.pygame
Vector2d = pyv.Vector2d

SHIP_DASH_RANGE = 55
SHIP_DELTA_ANGLE = 0.04
SHIP_SPEED_CAP = 192
SHIP_RAD = 5


def new_ship(pos_xy):
    actor_type, data = 'ship', {
        "pos": Vector2d(*pos_xy),
        "angle": 0,
        "speed": Vector2d(),
        "scr_size": pyv.vars.screen.get_size()
    }

    # -------- callable functions
    def ensure_ok_pos(this):
        maxw, maxh = this.scr_size
        if this.pos.x < 0:
            this.pos.x += maxw
        elif this.pos.x >= maxw:
            this.pos.x -= maxw

        if this.pos.y < 0:
            this.pos.y += maxh
        elif this.pos.y >= maxh:
            this.pos.y -= maxh

    def update_speed_vect(this):
        lg = this.speed.length()
        this.speed = Vector2d()
        this.speed.from_polar((lg, deg(this.angle)))

    # -------- behavior
    def on_thrust(this, ev):
        if this.speed.length() == 0:
            this.speed = Vector2d()
            this.speed.from_polar((5, deg(this.angle)))
        else:
            speedv_now = this.speed.length()
            speedv_now += 1
            if speedv_now > SHIP_SPEED_CAP:
                speedv_now = SHIP_SPEED_CAP
            this.speed = Vector2d()
            this.speed.from_polar((speedv_now, deg(this.angle)))

    def on_brake(this, ev):
        speedv_now = this.speed.length()
        speedv_now = speedv_now * 0.96
        if speedv_now < 5:
            this.speed = Vector2d()
        else:
            this.speed = Vector2d()
            this.speed.from_polar((speedv_now, deg(this.angle)))

    def on_ship_rotate(this, ev):
        if ev.dir == 'clockwise':
            this.angle += SHIP_DELTA_ANGLE
            update_speed_vect(this)
        elif ev.dir == 'counter-clockwise':
            this.angle -= SHIP_DELTA_ANGLE
            update_speed_vect(this)
        else:
            raise ValueError('invalid ev.dir for event "ship_rotate"')

    def on_dash(this, ev):
        tmp = Vector2d()
        tmp.from_polar((SHIP_DASH_RANGE, deg(this.angle)))
        this.pos += tmp
        ensure_ok_pos(this)

    def on_update(this, ev):
        this.pos.x += ev.dt * this.speed.x
        this.pos.y += ev.dt * this.speed.y
        ensure_ok_pos(this)

    def on_draw(this, ev):
        orientation = -this.angle
        pt_central = this.pos
        a, b, c = Vector2d(), Vector2d(), Vector2d()
        a.from_polar((1, deg(orientation - (2.0 * math.pi / 3))))
        b.from_polar((1, deg(orientation)))
        c.from_polar((1, deg(orientation + (2.0 * math.pi / 3))))
        temp = [a, b, c]
        for a_vector in temp:
            a_vector.y *= -1.0
        temp[0] = (1.2 * SHIP_RAD) * temp[0]
        temp[1] = (3 * SHIP_RAD) * temp[1]
        temp[2] = (1.2 * SHIP_RAD) * temp[2]
        pt_li = [Vector2d(*pt_central),
                 Vector2d(*pt_central),
                 Vector2d(*pt_central)]
        for i in range(3):
            pt_li[i] += temp[i]
        for pt in pt_li:
            pt.x = round(pt.x)
            pt.y = round(pt.y)
        pt_li.reverse()
        pygame.draw.polygon(ev.screen, pyv.pal.punk.brightgreen, pt_li, 2)
    return pyv.new_actor(locals())


LINE_THICKNESS = 2


def new_rockfield(quantity):
    actor_type, data = 'rockfield', {
        'content': [],
        'scr_size': pyv.vars.screen.get_size()
    }
    for _ in range(quantity):
        rand_pos = [random.randint(0, data['scr_size'][0] - 1), random.randint(0, data['scr_size'][1] - 1)]
        rand_size = random.randint(8, 55)
        rand_angle = random.uniform(0, 2 * math.pi)
        rand_speed_val = random.uniform(4, 32)
        speedvect = Vector2d()
        speedvect.from_polar((1, deg(rand_angle)))
        speedvect *= rand_speed_val
        data['content'].append(
            [rand_pos, rand_size, speedvect]
        )

    # --- computation
    def adjust_for_torus(coordx, coordy, scr_size):
        resx, resy = coordx, coordy
        if coordx < 0:
            resx = coordx + scr_size[0]
        elif coordx >= scr_size[0]:
            resx = coordx - scr_size[0]
        if coordy < 0:
            resy = coordy + scr_size[1]
        elif coordy >= scr_size[1]:
            resy = coordy - scr_size[1]
        return resx, resy

    # --- behavior
    def on_draw(this, ev):
        for rockinfo in this.content:
            pos = int(rockinfo[0][0]), int(rockinfo[0][1])
            size = rockinfo[1]
            pyv.draw_circle(ev.screen, pyv.pal.c64.lightgray, pos, size, LINE_THICKNESS)

    def on_update(this, ev):
        for k in range(len(this.content)):
            speed_vec = this.content[k][2]
            this.content[k][0][0] += ev.dt * speed_vec.x
            this.content[k][0][1] += ev.dt * speed_vec.y
            this.content[k][0][0], this.content[k][0][1] = adjust_for_torus(
                this.content[k][0][0], this.content[k][0][1], this.scr_size
            )
    return pyv.new_actor(locals())

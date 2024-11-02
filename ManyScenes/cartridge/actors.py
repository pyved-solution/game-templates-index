from .glvars import pyv
from . import glvars


# ---------- avatar --------------
def new_avatar(bx, by):
    # ---------------------------
    #  data
    # ---------------------------
    data = {
        "x": bx, "y": by,
        "delta_px": 3,  # its like the avatar's speed
        "color": 'green',
        "mobile_size": 13
    }

    # ---------------------------
    #  callable functions
    # ---------------------------
    def reset_pos(this):
        this.x, this.y = 300, 300

    # ---------------------------
    #  behavior
    # ---------------------------
    def on_move_avatar(this, ev):
        if ev.dir == "right":
            this.x += this.delta_px  # max(this.pos[1] - 5, 0)
        elif ev.dir == "left":
            this.x -= this.delta_px  # min(this.pos[1] + 5, SCREEN_HEIGHT - PADDLE_HEIGHT)
        elif ev.dir == "up":
            this.y -= this.delta_px
        elif ev.dir == "down":
            this.y += this.delta_px

    def on_update(this, ev):
        if pyv.get_world() == 'default':
            if this.x > glvars.world_dim[0] - 33:
                this.x = glvars.world_dim[0] - 50
                pyv.set_world(glvars.JUNG_WORLD_ID)
        elif pyv.get_world() == glvars.JUNG_WORLD_ID:
            if this.x < 33:
                this.x = 50
                pyv.set_world('default')

    def on_draw(this, ev):
        pyv.draw_circle(ev.screen, this.color, (this.x, this.y), this.mobile_size)

    return pyv.new_actor('avatar', locals())


# ---------- npc --------------
ref_npc = None
NPC_MSG_DURATION = 2.0  # sec


def new_npc():
    data = {
        # demo of how components can be used (2/2)
        "x": -96 + (glvars.world_dim[0] // 2), "y": 400,
        "color": "pink",
        "mobile_size": 20,
        "speak_end_date": None,
        "small_ft": None,
        "msg": None,
    }

    # - utilitary
    def say_something(this, txt_message):
        print('NPC says something!', txt_message)
        if this.small_ft is None:
            this.small_ft = pyv.new_font_obj(None, 18)
        this.msg = this.small_ft.render(txt_message, False, 'gray')
        this.speak_end_date = pyv.time() + NPC_MSG_DURATION

    # - behavior
    def on_draw(this, ev):
        pyv.draw_circle(ev.screen, this.color, (this.x, this.y), this.mobile_size)
        if this.msg:
            offsety = -50
            ahx = this.x - this.msg.get_width() // 2
            ahy = this.y + offsety
            ev.screen.blit(this.msg, (ahx, ahy))

    def on_update(this, ev):
        if (this.msg is not None) and ev.info_t > this.speak_end_date:
            this.msg = None
            this.speak_end_date = None

    return pyv.new_actor('npc', locals())

from ..glvars import pyv
from .. import glvars


# utilitary functions to ease scene initialization


def setup(map_w, map_h):
    global ref_npc
    # start with this, bc background has to be displayed first
    new_background()

    # then,
    new_avatar(map_w // 2, map_h // 2)
    ref_npc = new_npc()


# ---------- bg ------------------
HINT_TEXT = 'Use arrow keys | Go right...'
FT_SIZE = 60


def new_background():
    data = {
        'hint_msg': pyv.new_font_obj(None, FT_SIZE).render(HINT_TEXT, False, 'yellow')
    }
    def on_draw(this, ev):
        ev.screen.fill(glvars.BG_COL)
        ev.screen.blit(this.hint_msg, (256, 32))
    return pyv.new_actor('bg_default_scene', locals())


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
    def on_player_action(this, ev):
        if pyv.get_scene() == glvars.JUNG_SCENE_ID:
            if not (this.x == 300 and this.y == 300):
                reset_pos(this)  # move the avatar to a cool location
            else:
                # change scene
                pyv.set_scene(glvars.SPACE_SCENE_ID)

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
        # --- this is one way to implement the logic of the game ---
        # if the game has a great number of scene, and the behavior varies greatly, then
        # it would be best to re-define a scene-specific avatar actor
        if pyv.get_scene() == pyv.DEFAULT_SCENE:
            if this.x > glvars.scene_dim[0] - 33:
                this.x = glvars.scene_dim[0] - 50
                pyv.set_scene(glvars.JUNG_SCENE_ID)
        elif pyv.get_scene() == glvars.JUNG_SCENE_ID:
            if this.x < 33:
                this.x = 50
                pyv.set_scene(pyv.DEFAULT_SCENE)

    def on_draw(this, ev):
        pyv.draw_circle(ev.screen, this.color, (this.x, this.y), this.mobile_size)

    return pyv.new_actor('avatar', locals())


# ---------- npc --------------
ref_npc = None
NPC_MSG_DURATION = 2.0  # sec


def new_npc():
    data = {
        # demo of how components can be used (2/2)
        "x": -96 + (glvars.scene_dim[0] // 2), "y": 400,
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
            this.small_ft = pyv.new_font_obj(None, glvars.TEXT_SIZE)
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

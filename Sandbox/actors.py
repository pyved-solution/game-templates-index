"""
important remark to use sprite sheets!

 to load spritesheets you will need not only the .PNG but also a .JSON !
 this JSON file describes
 - how images are packed in your spritesheet
 - what name identifies every single image of your spritesheet

 To build a usable Spritesheet from a set of individual images, you can use this tool:
 https://www.codeandweb.com/tp-online then download both the .PNG and the .JSON
you will need to list the JSON in your list of assets (that is declared in metadat.json)
then, the data will be available from: pyv.spritesheets[key] where key is the name given to your spritesheet

if you need an animation, you may use
pyv.gfx.AnimatedSprite()
"""
from .glvars import pyv
from . import glvars


# ------------------------------------
#  we declare actors here!
# ------------------------------------
def new_color_viewer():
    data = {
        'curr_color_name': 'medium_gray',
        'square_position': (300, 96, 45, 45)
    }

    # - behavior
    def on_color_change(this, ev):
        this.curr_color_name = pyv.pal.yu.next_colorname(this.curr_color_name)
        print(' color?', this.curr_color_name)

    def on_draw(this, ev):
        pyv.draw_rect(ev.screen, pyv.pal.yu[this.curr_color_name], this.square_position)

    return pyv.actors.new_actor('color_viewer', locals())


def new_solid_background():
    data = {
        'color': pyv.pal.yu.medium_gray
    }

    def on_draw(this, ev):
        ev.screen.fill(this.color)

    return pyv.actors.new_actor('bg', locals())  # 1st argument = arbitrary name(used to debug) and 2nd arg is ALWAYS locals()


def new_entities_viewer():
    TEXT_COLOR = '#a1eeff'  # could also be 'black' or pyv.pal.c64.blue for example
    TEXT_POS = (250, 168)

    anims_description = {
        "default_anim": {"set": ["chip02.png", "chip05.png", "chip10.png"], "delay": 500}  # 500 ms per frame
    }
    # example of another "anims_description"
    # that would work well in another game, with another spite sheet:
    # {
    #   "idle": {"set": "0-5", "delay": 100},
    #   "attack": {"set": [6,7,8,9,10,11], "delay": 250}
    # }

    data = {
        'what_to_display': 'text',
        'my_rect': pyv.new_rect_obj(28, 56, 200, 200),
        'my_text': glvars.font_obj.render('hello, no timer', False, TEXT_COLOR),

        'saved_date': None, 'last_tick': None,  # to measure time

        'anim_sprite': pyv.gfx.AnimatedSprite(  # this line shows you how to use animated sprites!
            (32+glvars.screen_center[0], glvars.screen_center[1]),  # position x,y
            pyv.spritesheets['pokerchips'],  # first argument is a sprite sheet
            anims_description  # second argument is the description of anymations
        )
    }
    # start animation
    data['anim_sprite'].play("default_anim")

    # - behavior
    def on_timer_start(this, ev):
        print('timer started')
        this.saved_date = pyv.get_time()  # convenient way to retrieve current time

    def on_timer_stop(this, ev):
        print('stop')
        total_time = this.last_tick-this.saved_date
        this.my_text = glvars.font_obj.render(f'elpsed time:{total_time:.2f}', False, TEXT_COLOR)

    def on_update(this, ev):
        # has to update all animations
        delta_t = 0 if (this.last_tick is None) else ev.curr_t-this.last_tick
        this.anim_sprite.update(delta_t)
        # save date of the current tick
        this.last_tick = ev.curr_t

    def on_new_nb_pressed_keys(this, ev):
        if ev.nb == 0:
            this.what_to_display = 'text'
        elif ev.nb == 1:
            this.what_to_display = 'lion'
        elif ev.nb == 2:
            this.what_to_display = 'square'
        else:
            this.what_to_display = None

    def on_draw(this, ev):
        scr = ev.screen
        # always display the spritesheet
        scr.blit(
            this.anim_sprite.image,
            this.anim_sprite.pos
        )

        if this.what_to_display is None:
            pass  # nothing to display...
        elif this.what_to_display == 'text':
            scr.blit(this.my_text, TEXT_POS)
        elif this.what_to_display == 'lion':
            scr.blit(pyv.images['lion'], this.my_rect)
        elif this.what_to_display == 'square':
            pyv.draw_rect(scr, 'orange', this.my_rect)
        # TODO ca serait intéressant de mettre aussi l'affichage d'un sprite animé

    return pyv.actors.new_actor('e_viewer', locals())


def new_movable_rect(init_position):
    data = {
        'rect': pyv.new_rect_obj(init_position[0], init_position[1], 64, 64),
        'drag_state': False
    }

    def on_mousedown(this, ev):
        if ev.button == 1:
            print('<MOUSE CLICK,> position:', ev.pos)
            if this.rect.collidepoint(ev.pos):
                this.drag_state = True
                pyv.play_sound('woosh', repeat=1)  # as defined in metadat.json

    def on_mouseup(this, ev):
        if ev.button == 1:
            if this.drag_state:
                this.drag_state = False
                pyv.play_sound('sfx_drop')

    def on_mousemotion(this, ev):
        if this.drag_state:
            this.rect.topleft = ev.pos

    def on_draw(this, ev):
        pyv.draw_rect(ev.screen, 'purple', this.rect, 4)  # 4 stands for line width

    return pyv.actors.new_actor('movable_rect', locals())

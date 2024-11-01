from .glvars import pyv
from . import glvars


MSG_POST_CONV = 'The end | Press ESC to exit.'
MSG_POS = (150, 320)


def new_game_controller():  # game controller
    data = {
        'conversation_ongoing': True,
        'final_message': pyv.new_font_obj(None, 33).render(
            MSG_POST_CONV, False, pyv.pal.punk.flashypink
        )
    }

    def on_draw(this, ev):
        if this.conversation_ongoing:
            ev.screen.fill(glvars.CONV_BG_COLOR)
        else:
            ev.screen.fill(glvars.FINAL_BG_COLOR)
            pyv.vars.screen.blit(this.final_message, MSG_POS)

    def on_conv_finish(this, ev):
        this.conversation_ongoing = False

    pyv.new_actor('game_controller', locals())

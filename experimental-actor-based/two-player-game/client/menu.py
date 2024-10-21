import shared
from shared import SCREEN_WIDTH, SCREEN_HEIGHT, BLUE, GREEN, BLACK
from shared import pyv, pygame


__all__ = [
    'new_label',
    'new_button',
]


def new_label(msg, pos_xy, color):
    actor_type, data = 'label', {
        "label": shared.ft.render(msg, False, color),
        "x": pos_xy[0], "y": pos_xy[1],
        "visible": True
    }

    def is_visible(this):
        return this.visible

    # - behavior
    def on_draw(this, ev):
        if this.visible:
            pyv.screen.blit(this.label, (this.x, this.y))

    return pyv.new_actor(locals())


def new_button(msg, pos_xy, dim, callback_func):
    actor_type, data = 'label', {
        "label": shared.ft.render(msg, None, BLACK),
        "rect": pygame.Rect(pos_xy[0], pos_xy[1], dim[0], dim[1]),
        "cb_func": callback_func,
    }

    # - behavior
    def on_draw(this, ev):
        x, y = this.rect.topleft
        pygame.draw.rect(pyv.screen, BLACK, this.rect, 2)
        pyv.screen.blit(this.label, (x+5, y+5))

    def on_mouseclick(this, ev):
        if this.rect.collidepoint(ev.pos):
            this.cb_func()

    return pyv.new_actor(locals())

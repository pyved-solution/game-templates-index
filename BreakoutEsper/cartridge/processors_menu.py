from . import glvars
from .glvars import pyv, ecs

__all__ = [
    'GraphicsMenuProc',
    'MouseClicksProc'
]


class MouseClicksProc(ecs.Processor):
    def process(self, *args, **kwargs) -> None:
        ev_manager = pyv.legacy_evs
        for ev in ev_manager.get():
            if ev.type == ev_manager.QUIT:  # user clicked on the cross
                pyv.vars.gameover = True
            elif ev.type == ev_manager.MOUSEBUTTONDOWN:
                ecs.switch_world('ingame')


class GraphicsMenuProc(ecs.Processor):
    def __init__(self):
        self._scr = pyv.get_surface()

    def process(self, *args, **kwargs) -> None:
        # bg color
        self._scr.fill('antiquewhite2')

        # draw msg on screen, centered
        scr_w, scr_h = glvars.scr_size
        for label in (glvars.menu_message, ):
            if label is not None:
                lw, lh = label.get_size()
                self._scr.blit(
                    label, ((scr_w-lw)//2, (scr_h-lh)//2)
                )

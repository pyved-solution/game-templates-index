import katagames_sdk.engine as kataen
import glvars
from katagames_sdk.engine import enum_builder
from app import PuzzleView

pygame = kataen.import_pygame()

# sound init, with 3 channels
pygame.mixer.init()
glvars.init_sound()

GameStates = enum_builder(
    'Puzzle'
)

glvars.init_fonts_n_colors()
# glvars.loctexts.init_repo(glvars.CHOSEN_LANG)


kataen.init()
kataen.tag_multistate(GameStates, GameStates.Puzzle, is_bundled_game=True)

gctrl = kataen.get_game_ctrl()
gctrl.turn_on()


class Hijacker(kataen.EventReceiver):
    def __init__(self):
        super().__init__(True)
        self.scr = kataen.get_screen()

    def proc_event(self, ev, source):
        if ev.type == pygame.MOUSEMOTION:
            view_ref = PuzzleView.last_instance
            if view_ref.curr_dragged:
                x, y = ev.pos
                pos_topleft = (
                    x + view_ref.curr_dragged.mouse_offset[0],
                    y + view_ref.curr_dragged.mouse_offset[1]
                )
                tmp = PuzzleView.last_instance.to_gamecoords(pos_topleft)
                view_ref.last_instance.highlight_cell(tmp)
                if tmp:
                    tf = view_ref.curr_dragged
                    self.scr.blit(
                        tf.shadow_img,
                        (view_ref.org_point[0]+view_ref.box_size*tmp[0], view_ref.org_point[1]+view_ref.box_size*tmp[1])
                    )
            else:
                tmp = PuzzleView.last_instance.to_gamecoords(ev.pos)
                view_ref.last_instance.highlight_cell(tmp)


#hack_obj = Hijacker()
#hack_obj.turn_on()

gctrl.loop()

kataen.cleanup()

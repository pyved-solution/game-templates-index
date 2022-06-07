import glvars
import katagames_engine as kataen
from app.puzzle.TetColors import TetColors

pygame = kataen.pygame


class TetrominoSpr(pygame.sprite.Sprite):
    cls_cpt = 0

    def __init__(self, ref_piece):
        super().__init__()

        req_size = TetrominoSpr._calc_req_img_size(ref_piece)
        ck_pink = (0xff, 0x00, 0xff)

        # create surfaces & images
        self.image = pygame.surface.Surface(req_size)
        self.image.fill(ck_pink)
        self.image.set_colorkey(ck_pink)
        # (2)
        self.shadow_img = pygame.surface.Surface(req_size)
        self.shadow_img.fill(ck_pink)
        self.shadow_img.set_colorkey(ck_pink)

        # img creation
        TetrominoSpr.adhoc_render(self.image, ref_piece)
        TetrominoSpr.adhoc_render(self.shadow_img, ref_piece, TetColors.Gray)

        self.rect = self.image.get_rect()
        self.dragged = False
        self.mouse_offset = None

        self.__class__.cls_cpt = (self.__class__.cls_cpt + 1) % 3

    def update(self, *args, **kwargs) -> None:
        if self.dragged:
            mx, my = kataen.get_mouse_pos()
            new_pos = [
                mx + self.mouse_offset[0],
                my + self.mouse_offset[1],
            ]
            self.rect.topleft = new_pos

    @staticmethod
    def draw_lilsquare(ecran, x, y, chosencolor):
        sq_size = glvars.SQ_SIZE

        pg_color = glvars.colour_map[chosencolor]
        bd_size = glvars.BORDER_SIZE

        # dirty fix en attendant que emulateur pygame evolue!
        # bd_color = pg_color - glvars.border_fade_colour
        # TODO remettre la ligne davant qd emu- pygame est GOOD!
        bd_color = [pg_color[0] - 16, pg_color[1] - 16, pg_color[2] - 16]

        outer_rect = (x, y, sq_size, sq_size)
        inner_rect = (x + bd_size, y + bd_size, sq_size - bd_size * 2, sq_size - bd_size * 2)
        pygame.draw.rect(ecran, bd_color, outer_rect)
        pygame.draw.rect(ecran, pg_color, inner_rect)

    @staticmethod
    def adhoc_render(targ_surface, ref_tpiece, force_other_color=None):
        """
        render Tetromino on a surface
        """
        sq_li = ref_tpiece.shape["tiles"]
        if force_other_color:
            adhoc_color = force_other_color
        else:
            adhoc_color = ref_tpiece.color
        for sq in sq_li:
            TetrominoSpr.draw_lilsquare(targ_surface, glvars.SQ_SIZE * sq[0], glvars.SQ_SIZE * sq[1], adhoc_color)

    @staticmethod
    def _calc_req_img_size(ref_piece):
        dimx = (1+int(ref_piece.shape["x_adj"]))*glvars.SQ_SIZE
        dimy = (1+int(ref_piece.shape["y_adj"]))*glvars.SQ_SIZE
        return dimx, dimy

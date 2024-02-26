import pyved_engine as pyv
from ... import glvars
from ...ev_types import MyEvTypes
from ...modele_tetris import TetColor


_print_dim = False
pygame = pyv.pygame


class TetrisView(pyv.EvListener):

    def on_line_destroyed(self, ev):
        glvars.playsfx(self.sfx_crumble)

    def on_blocks_crumble(self, ev):
        glvars.playsfx(self.sfx_explo)

    BOARD_BORDER_SIZE = 5
    SCORE_PADDING = 5
    BORDER_SIZE = 4
    BORDER_FADE = pygame.Color(50, 50, 50)

    COLOR_MAP = dict()  # init in constructor

    def __init__(self, scr_size, bgcolor, fgcolor):
        super().__init__()

        # - couleurs C64
        new_palette = {
            TetColor.CLEAR: glvars.colors['c_lightpurple'],
            TetColor.RED: glvars.colors['c_skin'],
            TetColor.BLUE: glvars.colors['c_brown'],
            TetColor.GREEN: glvars.colors['c_leafgreen'],
            TetColor.YELLOW: glvars.colors['c_sunny'],
            TetColor.MAGENTA: glvars.colors['c_cherokee'],
            TetColor.CYAN: glvars.colors['c_oceanblue'],
            TetColor.ORANGE: glvars.colors['c_gray2']
        }
        self.COLOR_MAP.update(new_palette)

        # - base
        self.rows = []
        self.width = 0
        self.height = 0

        # - ext
        self.view_width, self.view_height = scr_size
        self.box_size = 10
        self.padding = (0, 0)
        self.go_font = glvars.fonts['moderne_big']
        self.sc_font = glvars.fonts['sm_monopx']

        self.font_color = fgcolor
        self.bgcolor = bgcolor

        self.score = None
        self.level = None

        self.__fond_gameover = None
        self.__label_gameover = None

        # sons
        self.sfx_explo = pyv.vars.sounds['explo_basique']
        self.sfx_crumble = pyv.vars.sounds['crumble']

    def clear(self):
        self.rows = [[TetColor.CLEAR] * self.width for _ in range(self.height)]

    def render_tile(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.rows[y][x] = color

    # Public interface to views
    def set_size(self, cols, rows):
        self.width = cols
        self.height = rows
        self.clear()
        self.calc_dimensions()

    def set_score(self, score):
        self.score = score

    def set_level(self, level):
        self.level = level

    def draw_content(self, screen):
        screen.fill(self.bgcolor)
        self.draw_board(screen)
        self.show_score(screen)

    def show_score(self, ecran):
        score_height = 0
        if self.score is not None:
            score_surf = self.sc_font.render("{:06d}".format(self.score), True, self.font_color)
            ecran.blit(score_surf, (self.BOARD_BORDER_SIZE, self.BOARD_BORDER_SIZE))
            score_height = score_surf.get_height()

        if self.level is not None:
            level_surf = self.sc_font.render("Niveau {:02d}".format(self.level), True, self.font_color)
            level_pos = (self.BOARD_BORDER_SIZE,
                         self.BOARD_BORDER_SIZE + score_height + self.SCORE_PADDING)
            ecran.blit(level_surf, level_pos)

    def show_game_over(self, ecran):
        # -- affiche simili -popup
        if not self.__fond_gameover:
            self.__fond_gameover = pygame.image.load('assets/img_bt_rouge.png')

        targetp = [self.view_width // 2, self.view_height // 2]
        targetp[0] -= self.__fond_gameover.get_size()[0] // 2
        targetp[1] -= self.__fond_gameover.get_size()[1] // 2
        ecran.blit(self.__fond_gameover, targetp)

        # -- affiche msg
        if not self.__label_gameover:
            self.__label_gameover = self.go_font.render("Jeu termine, ENTREE pr sortir", False, self.font_color)

        r = self.__label_gameover.get_rect()
        targetpos = (
            (self.view_width // 2) - (r.width // 2),
            (self.view_height // 2) - (r.height // 2)
        )
        ecran.blit(self.__label_gameover, targetpos)

    # -- Helper methods
    def get_score_size(self):
        (sw, sh) = self.sc_font.size("000000")
        (lw, lh) = self.sc_font.size("LEVEL 00")
        return max(sw, lw) + self.BOARD_BORDER_SIZE, sh + lh + self.SCORE_PADDING

    def calc_dimensions(self):
        horiz_size = (self.view_width - (self.BOARD_BORDER_SIZE * 2)) // self.width
        vert_size = (self.view_height - (self.BOARD_BORDER_SIZE * 2)) // self.height

        if vert_size > horiz_size:
            self.box_size = horiz_size
            self.padding = (self.get_score_size()[0] * 2,
                            (self.view_height
                             - self.BOARD_BORDER_SIZE
                             - (self.height * horiz_size)))
        else:
            self.box_size = vert_size
            left_padding = max(self.get_score_size()[0] * 2,
                               (self.view_width
                                - self.BOARD_BORDER_SIZE
                                - (self.width * vert_size)))
            self.padding = (left_padding, 0)

        global _print_dim

        if _print_dim:
            print(self.width, self.height)
            print(self.view_width, self.view_height)
            print(horiz_size, vert_size)
            print(self.box_size)
            print(self.padding)
            _print_dim = True

    def draw_board(self, ecran):
        board_color = self.COLOR_MAP[TetColor.CLEAR]

        x_start = self.BOARD_BORDER_SIZE + (self.padding[1] // 2)
        y_start = self.BOARD_BORDER_SIZE + (self.padding[0] // 2)

        x, y = x_start, y_start

        board_rect = (y, x, self.width * self.box_size, self.height * self.box_size)
        pygame.draw.rect(ecran, board_color, board_rect)
        for col in self.rows:
            for item in col:
                self.draw_box(ecran, x, y, item)
                y += self.box_size
            x += self.box_size
            y = y_start

    def draw_box(self, ecran, x, y, color):
        if color == TetColor.CLEAR:
            return

        pg_color = self.COLOR_MAP[color]
        bd_size = self.BORDER_SIZE
        bd_color = pg_color - self.BORDER_FADE

        outer_rect = (y, x, self.box_size, self.box_size)
        inner_rect = (y + bd_size, x + bd_size,
                      self.box_size - bd_size * 2, self.box_size - bd_size * 2)

        pygame.draw.rect(ecran, bd_color, outer_rect)
        pygame.draw.rect(ecran, pg_color, inner_rect)

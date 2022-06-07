import glvars
import katagames_engine as kataen
from ev_types import MyEvTypes

from app.puzzle.TetColors import TetColors
from app.puzzle.TetrominoSpr import TetrominoSpr


pygame = kataen.pygame
kevent = kataen.event

class PuzzleView(kevent.EventReceiver):

    BOARD_BORDER_SIZE = 5
    SCORE_PADDING = 5
    last_instance = None

    def __init__(self, board, avail, orgpoint):
        super().__init__()

        PuzzleView.last_instance = self  # used for debugging only
        self._hl_cell = None  # marquer la case en rouge, utile au debug
        self.shadow_spr_ij = None  # indique ou drop l'ombre

        # - - where is the board rel. to the whole screen - -
        self.org_point = orgpoint

        # save parameters
        self.boardmodel = board

        self._bag_model = avail

        self.font_color = glvars.colors['c_lightpurple']
        self.bgcolor = glvars.colors['c_purple']

        # dico de spr
        self._sprites = dict()
        self._create_adhoc_sprites()

        # - base
        self.rows = None
        self.clear()  # init attribute .rows
        self.curr_dragged = None

        self.scr = kataen.get_screen()

    def proc_event(self, ev, source):
        if ev.type == kevent.EngineEvTypes.PAINT:

            for spr in self._sprites.values():
                spr.update()
            self.do_paint(ev.screen)

        elif ev.type == pygame.MOUSEMOTION:

            if self.curr_dragged:
                x, y = ev.pos
                pos_topleft = (
                    x + self.curr_dragged.mouse_offset[0],
                    y + self.curr_dragged.mouse_offset[1]
                )
                tmp = self.to_gamecoords(pos_topleft)

                piece = self.get_dragged_piece_obj()
                found_loc = False
                if tmp is not None:
                    if self.boardmodel.can_put(piece, tmp):
                        self.shadow_spr_ij = tmp
                        found_loc = True
                if not found_loc:
                    self.shadow_spr_ij = None

        elif ev.type == pygame.MOUSEBUTTONDOWN:
            mpos = ev.pos

            for tmp in self._sprites.values():
                if tmp.rect.collidepoint(mpos):
                    tmp.pos_jadis = tmp.rect.topleft
                    tmp.dragged = True
                    mx, my = mpos
                    a, b = tmp.rect.topleft
                    tmp.mouse_offset = a - mx, b - my
                    self.curr_dragged = tmp
                    break

        elif (ev.type == pygame.MOUSEBUTTONUP) and self.curr_dragged:
            self._proc_mouse_up(ev.pos)
            self.curr_dragged = None
            self.shadow_spr_ij = None

        elif ev.type == MyEvTypes.NewPieces:
            self._create_adhoc_sprites()

    def _create_adhoc_sprites(self):
        for idx, piece_obj in enumerate(self._bag_model):
            key = piece_obj
            self._sprites[key] = TetrominoSpr(piece_obj)

        ordered_pieces = list()
        for k in self._sprites.keys():
            s = len(ordered_pieces)
            if not s:  # empty list
                ordered_pieces.append(k)
            else:
                cpt = 0
                while (cpt < s) and k.get_area() > ordered_pieces[cpt].get_area():
                    cpt += 1
                ordered_pieces.insert(cpt, k)

        # position sprites so we have more chances to see it clear
        csiz = glvars.SQ_SIZE
        refx, refy = self.org_point[0] + self.width*csiz, self.org_point[1]

        for idx, piece_obj in enumerate(ordered_pieces):
            tmp0 = refx + (1+3*idx) * csiz
            tmp1 = refy + 3*idx*csiz
            self._sprites[piece_obj].rect.topleft = (tmp0, tmp1)

    def get_dragged_piece_obj(self):
        if self.curr_dragged is None:
            return None
        else:
            for k, v in self._sprites.items():  # find key that corresponds to self.curr_dragged
                if v == self.curr_dragged:
                    return k

    def _proc_mouse_up(self, mouse_pos):
        drag_sprite = self.curr_dragged
        piece_obj = self.get_dragged_piece_obj()

        pos_topleft = (
            mouse_pos[0] + self.curr_dragged.mouse_offset[0],
            mouse_pos[1] + self.curr_dragged.mouse_offset[1]
        )
        # dim_spr = drag_sprite.image.get_size()
        # pos_center_square = (
        #     int(pos_of_piece_center[0] - (dim_spr[0]/2) + SQ_SIZE/2),
        #     int(pos_of_piece_center[1] - (dim_spr[1]/2) + SQ_SIZE/2),
        # )

        coords = self.to_gamecoords(pos_topleft)
        must_reset_spr = True

        if coords:
            # TETROMINO SPR WAS DROPPED!
            # test if its possible
            # - debug
            # print('found to be in the grid')

            if self.boardmodel.can_put(piece_obj, coords):
                # - debug
                # print('coords found but cant drop')
                self.boardmodel.put_piece(piece_obj, coords)
                self._bag_model.remove(piece_obj)
                del self._sprites[piece_obj]
                must_reset_spr = False

        if must_reset_spr:
            drag_sprite.rect.topleft = drag_sprite.pos_jadis
        drag_sprite.dragged = False

    def highlight_cell(self, ij=None):
        self._hl_cell = ij

    @staticmethod
    def edist(p1, p2):
        return

    def to_gamecoords(self, xy_pair):
        a, b = -self.org_point[0], -self.org_point[1]
        a += xy_pair[0]
        b += xy_pair[1]
        if a < 0 or b < 0:
            return None
        else:
            a /= glvars.SQ_SIZE
            b /= glvars.SQ_SIZE
            if a >= self.boardmodel.width or b >= self.boardmodel.height:
                return None
            else:
                return int(a), int(b)

    def clear(self):
        self.rows = [
            [TetColors.Clear] * self.height for _ in range(self.width)
        ]

    def render_tile(self, x, y, color):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.rows[x][y] = color

    # --------------------------------------------------------
    #  THREE METHODS USEFUL FOR GRAPHIC UPDATE
    # --------------------------------------------------------
    def do_paint(self, ref_screen, updatefrom_model=True):
        if updatefrom_model:
            self.boardmodel.met_a_jour_vue(self)
            # TODO faire en sorte que vue tjr à jour
            # TODO faire en sorte que la vue se dessine tt seule (et pas quil faille que le ctrl lui dise qd le faire)

        # if self.show_action is not None:
        #     self.show_action()

        ref_screen.fill(self.bgcolor)
        self.draw_board(ref_screen)

    def draw_board(self, ecran):
        board_color = glvars.colour_map[TetColors.Clear]

        x_start = self.org_point[0]
        y_start = self.org_point[1]

        x, y = x_start, y_start
        cst = glvars.SQ_SIZE
        board_rect = (x, y, self.width * cst, self.height * cst)
        pygame.draw.rect(ecran, board_color, board_rect)

        for col in self.rows:
            for item in col:
                TetrominoSpr.draw_lilsquare(ecran, x, y, item)
                y += cst
            x += cst
            y = y_start

        if self.shadow_spr_ij:
            tmpi, tmpj = self.shadow_spr_ij
            self.scr.blit(
                self.curr_dragged.shadow_img,
                (self.org_point[0] + cst * tmpi,
                 self.org_point[1] + cst * tmpj)
            )

        self.draw_grid(ecran)

        if self._hl_cell:
            i, j = self._hl_cell
            cst = glvars.SQ_SIZE
            pygame.draw.rect(
                ecran, (255, 0, 0),
                (self.org_point[0]+i*cst, self.org_point[1]+j*cst, cst, cst),
                1
            )

        # dessin des pieces en rab, dapres les sprites!
        for spr in self._sprites.values():
            ecran.blit(spr.image, spr.rect.topleft)

    def draw_grid(self, screen_ref):
        """
        Draw black lines! Fat grid
        """
        linecolor = (0x74, 0x54, 0x54)
        thickness = 1
        cst = glvars.SQ_SIZE
        for i in range(self.width+1):
            xline = cst*i
            org = (self.org_point[0]+xline, self.org_point[1])
            dest = (self.org_point[0]+xline, self.org_point[1]+self.px_height)
            pygame.draw.line(screen_ref, linecolor, org, dest, thickness)

            for j in range(self.height+1):
                yline = cst*j
                org = (self.org_point[0], self.org_point[1]+yline)
                dest = (self.org_point[0]+self.px_width, self.org_point[1]+yline)
                pygame.draw.line(screen_ref, linecolor, org, dest, thickness)

    # --------------------------------------------------------
    #  PROPERTIES
    # --------------------------------------------------------
    @property
    def width(self):
        return self.boardmodel.width

    @property
    def px_width(self):
        return self.boardmodel.width * glvars.SQ_SIZE

    @property
    def height(self):
        return self.boardmodel.height

    @property
    def px_height(self):
        return self.boardmodel.height * glvars.SQ_SIZE

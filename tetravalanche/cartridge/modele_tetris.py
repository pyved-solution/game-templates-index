from collections import defaultdict
import random

from .glvars import pyv
from .ev_types import MyEvTypes

# from katagames_sdk.engine import CogObject
# from katagames_sdk.capsule.event import FIRST_CUSTO_TYPE  # TODO fix this


class TetColor:
    CLEAR = "clear"
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"
    MAGENTA = "magenta"
    CYAN = "cyan"
    ORANGE = "orange"

    @staticmethod
    def colors():
        return TetColor.RED, TetColor.BLUE, TetColor.GREEN, TetColor.YELLOW, TetColor.MAGENTA, TetColor.CYAN, TetColor.ORANGE


# class TextView(ViewBase):
#     """Renders a board as text."""
#
#     COLOR_CHAR = {
#         Color.CLEAR: '.',
#         Color.RED: '*',
#         Color.BLUE: '#',
#         Color.GREEN: 'o',
#         Color.YELLOW: 'O',
#         Color.MAGENTA: '%',
#         Color.CYAN: '&',
#         Color.ORANGE: '$',
#     }
#
#     def __init__(self, surf=None):
#         ViewBase.__init__(self)
#
#     def show(self):
#         str_ = self.get_str()
#         print(str_)
#
#     def get_str(self):
#         str_ = "\n"
#         for column in self.rows:
#             for item in column:
#                 str_ += TextView.COLOR_CHAR[item]
#             str_ += "\n"
#         return str_


class Piece:
    L_SHAPE = {"tiles": ((0, 0), (0, 1), (0, 2), (1, 2)),
               "x_adj": 1,
               "y_adj": 2,
               "color": TetColor.YELLOW}
    R_SHAPE = {"tiles": ((0, 0), (1, 0), (0, 1), (0, 2)),
               "x_adj": 1,
               "y_adj": 2,
               "color": TetColor.ORANGE}
    # carré
    # O_SHAPE = {"tiles": ((0, 0), (0, 1), (1, 0), (1, 1)),
    O_SHAPE = {"tiles": ((0, 0), (1, 0), (2, 1), (1, 2), (0, 2)),
               "x_adj": 2,  # 1,
               "y_adj": 2,  # 1,
               "color": TetColor.CYAN}
    T_SHAPE = {"tiles": ((0, 0), (1, 0), (1, 1), (2, 0)),
               "x_adj": 2,
               "y_adj": 1,
               "color": TetColor.MAGENTA}
    S_SHAPE = {"tiles": ((0, 0), (0, 1), (1, 1), (1, 2)),
               "x_adj": 1,
               "y_adj": 2,
               "color": TetColor.BLUE}
    Z_SHAPE = {"tiles": ((0, 0), (1, 0), (1, 1), (2, 1)),
               "x_adj": 2,
               "y_adj": 1,
               "color": TetColor.GREEN}
    I_SHAPE = {"tiles": ((0, 0), (1, 0), (2, 0), (3, 0)),
               "x_adj": 3,
               "y_adj": 0,
               "color": TetColor.RED}
    SHAPES = (L_SHAPE, R_SHAPE, O_SHAPE, T_SHAPE, S_SHAPE, Z_SHAPE, I_SHAPE)

    def __init__(self, x, y, shape, color, rot=0):
        self.x = x
        self.y = y
        self.shape = shape
        self.color = color
        self.rotation = rot

    def move(self, x, y):
        self.x += x
        self.y += y

    def __iter__(self):
        for x_offset, y_offset in self.shape["tiles"]:
            if self.rotation == 0:
                yield (self.x + x_offset, self.y + y_offset)
            elif self.rotation == 1:
                yield (self.x - y_offset + self.shape["y_adj"],
                       self.y + x_offset)
            elif self.rotation == 2:
                yield (self.x - x_offset + self.shape["x_adj"],
                       self.y - y_offset + self.shape["y_adj"])
            elif self.rotation == 3:
                yield (self.x + y_offset,
                       self.y - x_offset + self.shape["x_adj"])

    def render(self, v):
        for x, y in self:
            v.render_tile(x, y, self.color)

    def rotate(self, clockwise=True):
        if clockwise:
            self.rotation = (self.rotation + 1) % 4
        else:
            self.rotation = (self.rotation - 1) % 4

    def rotated(self, clockwise=True):
        p = Piece(self.x, self.y, self.shape, self.color, self.rotation)
        p.rotate(clockwise)
        return p


class Board(pyv.Emitter):

    def __init__(self, n_columns, n_rows, autogen=True):
        super().__init__()

        self.height = n_rows
        self.width = n_columns
        self.columns = [self.height] * n_columns
        self.rand = random.Random()
        self.autogen = autogen

        self.level = self.piece = self.finalize_ready = None
        self.tiles = self.score = self.lines = self.game_over = None

        self.quake_effect = False
        self.reset()

    def reset(self):
        self.piece = None
        self.finalize_ready = False
        self.tiles = defaultdict(lambda: TetColor.CLEAR)
        self.score = 0
        self.level = 1
        self.lines = 0
        self.game_over = False

    def more_quake(self):
        tomba = False
        for y in range(self.height - 2, -1, -1):
            for x in range(0, self.width + 1):
                if not self.is_tile_empty(x, y):
                    c = self.tiles[(x, y)]
                    if self.is_tile_empty(x, y + 1):
                        self.set_tile_color(x, y, TetColor.CLEAR)
                        self.set_tile_color(x, y + 1, c)
                        tomba = True
            if tomba:
                self.pev(MyEvTypes.BlocksCrumble)
                return

        if not tomba:
            self.pev(MyEvTypes.FlatWorld)
            self.accu_score()

    def clear_tile(self, x, y):
        self.tiles[(x, y)] = TetColor.CLEAR

        # Move all the tiles above this row down one space
        for y_tile in range(y, self.columns[x] - 1, -1):
            self.tiles[(x, y_tile)] = self.tiles[(x, y_tile - 1)]

        # And reset the top of of the columns
        while (self.columns[x] < self.height and
               self.tiles[(x, self.columns[x])] == TetColor.CLEAR):
            self.columns[x] += 1

    def clear_row(self, row):
        for col in range(len(self.columns)):
            self.clear_tile(col, row)

    def row_full(self, row):
        for col in range(len(self.columns)):
            if self.tiles[(col, row)] == TetColor.CLEAR:
                return False
        return True

    def set_tile_color(self, x, y, color):
        # assert color != TetColor.CLEAR
        self.tiles[(x, y)] = color
        if color == TetColor.CLEAR:
            return
        if self.columns[x] > y:
            self.columns[x] = y

    def is_tile_empty(self, x, y):
        return self.tiles[(x, y)] == TetColor.CLEAR

    def piece_can_move(self, x_move, y_move):
        """Returns True if a piece can move, False otherwise."""
        assert self.piece is not None

        # for base_x, base_y in self.piece:
        #     x = x_move + base_x
        #     y = y_move + base_y
        #     if not 0 <= x < len(self.columns) or y >= self.columns[x]:
        #         return False

        for basex, basey in self.piece:
            x = basex + x_move
            y = basey + y_move
            if not (0 <= x < len(self.columns)):
                return False
            if y >= self.height:
                return False
            if not self.is_tile_empty(x, y):
                return False
        return True

    def drop_piece(self):
        """Either drops a piece down one level, or finalizes it and creates another piece."""
        if self.piece is not None:
            if self.piece_can_move(0, 1):
                self.piece.move(0, 1)
                self.finalize_ready = False
                return

            # piece cannot move down => hits the bottom...
            if not self.finalize_ready:  # this gives a short leeway for the player to move the piece, once it's hit bottom
                self.finalize_ready = True
            else:
                self.finalize_piece()
                self.generate_piece()

    def full_drop_piece(self):
        """Either drops a piece down one level, or finalizes it and creates another piece."""
        if self.piece is not None:
            while self.piece_can_move(0, 1):
                self.piece.move(0, 1)
            self.finalize_piece()
            self.generate_piece()

    def move_piece(self, x_move, y_move):
        """Move a piece some number of spaces in any direction"""
        if self.piece is not None:
            if self.piece_can_move(x_move, y_move):
                self.piece.move(x_move, y_move)

    def rotate_piece(self, clockwise=True):
        if self.piece is None:
            return
        if self.piece_can_rotate(clockwise):
            self.piece.rotate(clockwise)

    def piece_can_rotate(self, clockwise):
        """Returns True if a piece can drop, False otherwise."""
        p = self.piece.rotated(clockwise)
        for x, y in p:
            if not 0 <= x < len(self.columns) or y >= self.columns[x]:
                return False
        return True

    def generate_piece(self):
        """Creates a new piece at random and places it at the top of the board."""
        if self.game_over:
            return

        middle = len(self.columns) // 2
        shape = self.rand.choice(Piece.SHAPES)
        self.piece = Piece(middle - shape["x_adj"], 0, shape, shape["color"])

        if not self.piece_can_move(0, 0):
            # Show piece on the board
            self.finalize_piece()

            # And mark the game as over
            self.game_over = True
            self.piece = None

            self.pev(MyEvTypes.GameLost)

    def accu_score(self):
        old_level = self.level

        rows_cleared = 0
        for y in range(0, self.height + 1):
            if self.row_full(y):
                self.clear_row(y)
                rows_cleared += 1

        if rows_cleared:
            self.score += (rows_cleared * rows_cleared) * 10
            self.lines += rows_cleared
            self.level = 1 + (self.lines // 8)
            self.pev(MyEvTypes.LineDestroyed)

            if self.level != old_level:
                # pygame.event.post(pygame.event.Event(self.LEVELUP_EV_TYPE, level=self.level))
                self.pev(MyEvTypes.LevelUp, level=self.level)

    def finalize_piece(self):
        for x, y in self.piece:
            self.set_tile_color(x, y, self.piece.color)

        self.accu_score()

        self.piece = None

    def met_a_jour_vue(self, v):
        v.clear()
        v.set_size(len(self.columns), self.height)
        for (x, y), color in self.tiles.items():
            v.render_tile(x, y, color)
        if self.piece is not None:
            self.piece.render(v)
        v.set_score(self.score)
        v.set_level(self.level)

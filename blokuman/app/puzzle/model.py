from collections import defaultdict

from app.puzzle.TetColors import TetColors
from app.puzzle.TetPiece import TetPiece
from ev_types import MyEvTypes
import katagames_engine as kengi


CogObject = kengi.event.CogObj


class BagFulloPieces(CogObject):

    def __init__(self, ref_board):
        super().__init__()

        # bc we need to be able to check if the board is clumped
        self.ref_board = ref_board

        self._avail = list()
        self._refill_bag()

    def __iter__(self):
        return self._avail.__iter__()

    def _refill_bag(self):
        canput_is_proven = False

        for i in range(3):
            obj = TetPiece.gen_random()
            # if i == 0:
            #     obj.move(14, 2)
            # elif i == 1:
            #     obj.move(16, 5)
            # else:
            #     obj.move(18, 8)
            self._avail.append(obj)

            if (not canput_is_proven) and self.ref_board.can_put_anywhere(obj):
                canput_is_proven = True

        self.pev(MyEvTypes.NewPieces)
        if not canput_is_proven:
            self.ref_board.tag_deadend()

    @property
    def content(self):
        return self._avail

    def remove(self, ref_piece):
        self._avail.remove(ref_piece)

        if len(self._avail) > 0:
            for elt in self._avail:
                if self.ref_board.can_put_anywhere(elt):
                    return
            self.ref_board.tag_deadend()
        else:
            self._refill_bag()


class BoardModel(CogObject):

    SCORE_CAP = 10**6

    def __init__(self, n_columns, n_rows):
        super().__init__()

        self.height = n_rows
        self.width = n_columns
        self.columns = [self.height] * n_columns
        self.score = 0
        self.shadowpiece = None
        self.finalize_ready = False
        self.tiles = defaultdict(lambda: TetColors.Clear)
        self.score = 0
        self.lines = 0
        self.blocked_game = False

    def can_put_anywhere(self, ref_piece):
        for i in range(self.width):
            for j in range(self.height):
                if self.can_put(ref_piece, (i, j)):
                    return True
        return False

    def tag_deadend(self):
        self.blocked_game = True
        print('xxx BLOCKED GAME xxx')
        print('your score is {}'.format(self.score))
        self.pev(MyEvTypes.GameLost)

    def update(self):
        """
        after finalizing a piece (it has been put on the board)
        we NEED to check if there's a flush in
        any column or any line!
        """
        def col_full(col_index):
            for jj in range(self.height):
                if self.tiles[(col_index, jj)] == TetColors.Clear:
                    return False
            return True

        def row_full(row):
            for col in range(self.width):
                if self.tiles[(col, row)] == TetColors.Clear:
                    return False
            return True

        to_be_cleared = set()
        increm_score = 0

        for j in range(10):
            if row_full(j):
                # tag all cells in this row for deletion
                increm_score += 25
                for i in range(self.width):
                    to_be_cleared.add((i, j))

        for i in range(10):
            if col_full(i):
                increm_score += 25
                # tag all cells in this column for deletion
                for j in range(self.height):
                    to_be_cleared.add((i, j))

        if increm_score:
            self.pev(MyEvTypes.LineDestroyed)
            self.upgrade_score(increm_score)
            for zombiecell in to_be_cleared:
                self.tiles[zombiecell] = TetColors.Clear

    def upgrade_score(self, bonus):
        if self.score+bonus < self.SCORE_CAP:
            self.score += bonus
        else:
            self.score = self.SCORE_CAP-1
        self.pev(MyEvTypes.ScoreChanges, score=self.score)

    def set_tile_color(self, x, y, color):
        # assert color != TetColor.CLEAR
        self.tiles[(x, y)] = color
        if color == TetColors.Clear:
            return
        if self.columns[x] > y:
            self.columns[x] = y

    def is_tile_empty(self, x, y):
        return self.tiles[(x, y)] == TetColors.Clear

    def can_put(self, piece_obj, coords_ij):
        sh = piece_obj.shape

        temp = TetPiece(coords_ij[0], coords_ij[1], sh, sh["color"])
        for x, y in temp:
            if x >= self.width:
                return False
            if y >= self.height:
                return False
            if self.tiles[(x, y)] != TetColors.Clear:
                return False

        return True

    def put_piece(self, ref_p, coords_ij):
        shape = ref_p.shape
        self.shadowpiece = TetPiece(coords_ij[0], coords_ij[1], shape, shape["color"])
        self.finalize_piece()

    def finalize_piece(self):
        for x, y in self.shadowpiece:
            self.set_tile_color(x, y, self.shadowpiece.color)

        self.update()
        # self.accu_score()

        self.shadowpiece = None

    def met_a_jour_vue(self, v):
        v.clear()

        for (x, y), color in self.tiles.items():
            v.render_tile(x, y, color)

        if self.shadowpiece is not None:
            self.shadowpiece.savecolor_in_grid(v)

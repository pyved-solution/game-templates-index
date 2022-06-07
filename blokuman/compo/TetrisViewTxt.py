
class TextView(TetrisView):
    """Renders a board as text."""

    def __init__(self):
        super().__init__(None, None, None)

    COLOR_CHAR = {
        TetColor.CLEAR: '.',
        TetColor.RED: '*',
        TetColor.BLUE: '#',
        TetColor.GREEN: 'o',
        TetColor.YELLOW: 'O',
        TetColor.MAGENTA: '%',
        TetColor.CYAN: '&',
        TetColor.ORANGE: '$',
    }

    def show(self):
        str_ = self.get_str()
        print(str_)

    # alias
    def draw_content(self):
        return self.get_str()

    def get_str(self):
        str_ = "\n"
        for column in self.rows:
            for item in column:
                str_ += TextView.COLOR_CHAR[item]
            str_ += "\n"
        return str_

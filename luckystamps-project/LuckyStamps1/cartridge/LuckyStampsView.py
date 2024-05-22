from .shared import MyEvTypes, pimodules


pyv = pimodules.pyved_engine


class LuckyStampsView(pyv.EvListener):
    elt_type_to_imgname_mapping = {
        -1: 'lion',
        0: 'bonus-rolls',
        1: 'brightpink-prince',
        2: 'young-prince',
        3: 'rare-shilling',
        4: 'medaillon-queen',
        5: 'deepblue-queen',
        6: 'seven-pence',
        7: 'canada-orange',
    }

    # color_mapping = {
    #     1: THECOLORS['papayawhip'],
    #     2: THECOLORS['antiquewhite2'],
    #     3: THECOLORS['paleturquoise3'],
    #     4: THECOLORS['gray31'],
    #     5: THECOLORS['plum2'],
    #     6: THECOLORS['seagreen3'],
    #     7: THECOLORS['sienna1']
    # }

    # spr_sheet = pyv.gfx.JsonBasedSprSheet('cartes')
    def __init__(self, refmod):
        super().__init__()
        self.grid = [
            [None, None, None] for _ in range(5)
        ]
        self.line_idx_by_column = dict()
        for k in range(5):
            self.line_idx_by_column[k] = 2
        self.mod = refmod
        self.ft = pyv.pygame.font.Font(None, 22)

        self._label_rounds_cpt = None
        self.label_earnings = None
        self._refresh_cpt()
        self._refresh_earnings()

    def _refresh_cpt(self):
        self.label_rounds_cpt = self.ft.render(str(self.mod.get_rounds()), False, 'orange')

    def _refresh_earnings(self):
        self.label_earnings = self.ft.render('earings: {} credits'.format(self.mod.total_earnings), False, 'orange')

    def on_mousedown(self, ev):
        self.pev(MyEvTypes.GuiLaunchRound)

    def on_earnings_update(self, ev):
        print('call refresh earnings')
        self._refresh_earnings()

    def on_element_drop(self, ev):
        k = self.line_idx_by_column[ev.column]
        self.line_idx_by_column[ev.column] -= 1
        self.grid[ev.column][k] = ev.elt_type  # affectation

    def on_new_round(self, ev):
        # reset stack position
        for k in range(5):
            self.line_idx_by_column[k] = 2

    def on_force_update_rounds(self, ev):
        self._refresh_cpt()

    def on_paint(self, ev):
        ev.screen.fill(pyv.pal.japan['darkblue'])

        # -----------
        # paint grid
        # -----------
        binfx, binfy = 100, 88
        # for col_no in range(5):
        #     for row_no in range(3):
        #         a, b = col_no * 153 + binfx, row_no * 179 + binfy,
        #         r4infos = [a, b, STAMPW, STAMPH]
        #         cell_v = self.grid[col_no][row_no]
        #         if cell_v is None:
        #             pyv.draw_rect(ev.screen, pyv.pal.punk['darkblue'], r4infos, 1)
        #         elif 1 <= cell_v < 8:
        #             pyv.draw_rect(ev.screen, cls.color_mapping[cell_v], r4infos)
        #         elif cell_v == self.mod.BONUS_CODE:
        #             ev.screen.blit(pyv.vars.images['canada-orange'], r4infos[:2])

        # ------------
        # paint counter + earnings
        # ------------
        ev.screen.blit(self.label_rounds_cpt, (180, 64))
        ev.screen.blit(self.label_earnings, (400+180, 64))

        # ------------
        # paint falling blocks
        # ------------
        for k, blockinfos in self.mod.allboxes.items():
            elt_type = blockinfos[4]
            # if elt_type == self.mod.BOMB_CODE:
            #     pyv.draw_rect(ev.screen, 'red', blockinfos[:4])
            #
            # elif elt_type == self.mod.BONUS_CODE:
            #     pyv.draw_rect(ev.screen, 'black', blockinfos[:4])
            #
            # elif elt_type == 1:
            #     ev.screen.blit(
            #         pyv.vars.images['img/young-prince'],
            #         (blockinfos[0], blockinfos[1]))
            #
            # elif elt_type == 2:

            img = pyv.vars.images[self.__class__.elt_type_to_imgname_mapping[elt_type]]
            ev.screen.blit(img, (blockinfos[0], blockinfos[1]))

            # else:
            #     color = self.__class__.color_mapping[elt_type]
            #     pyv.draw_rect(ev.screen, color, blockinfos[:4])

from ... import pimodules

pyv = pimodules.pyved_engine
from ... import glvars
from ...ev_types import MyEvTypes
# from katagames_sdk.api import HttpServer
# from katagames_sdk.capsule.event import FIRST_CUSTO_TYPE  # TODO fix this dependancy! shouldnt be here


pygame = pyv.pygame
FIRST_CUSTO_TYPE = pyv.EngineEvTypes.size+1


class TetrisCtrl(pyv.EvListener):
    SHAKE_EV = FIRST_CUSTO_TYPE - 2
    DROP_EV = FIRST_CUSTO_TYPE - 1

    def __init__(self, ref_mod, ref_view):
        super().__init__()
        self.boardmodel = ref_mod
        self.boardmodel.generate_piece()
        self.view = ref_view
        self.game_over = False
        self.show_action = None
        self.max_fps = 50
        self.clock = pygame.time.Clock()
        self.__ready_to_exit = False

    @staticmethod
    def commit_score(valeur_score):
        if glvars.username is None:
            print('bonjour, peux pas veux commit score car no User Auth!')
        else:
            user = glvars.username
            print(f'bonjour je suis {user} et veux commit ce score-là:', valeur_score)
            pimodules.network.register_score(valeur_score, glvars.payment_token)
        return
        # TODO : need more fix?
        # envoyer info vers le SERVEUR
        serv = HttpServer.instance()
        url = serv.get_ludo_app_url() + 'tournois.php'
        params = {
            'fct': 'pushscore',
            'cid': str(glvars.num_challenge),
            'id_perso': str(glvars.id_perso),
            'name': str(glvars.nom_utilisateur),
            'score': str(valeur_score)
        }
        if glvars.DEV_MODE:
            print('URL= {}'.format(url))
            print('params below:')
            print(str(params))
        res = serv.proxied_get(url, params)
        if glvars.DEV_MODE:
            print('commit server done [xxxxxxxxxxxxxxxxxxxxxxx]  ')
            print(str(res))

    def flag_games_over(self):
        self.game_over = True
        self.__ready_to_exit = False

    # ---------------------------------------
    #  GESTION EV. COREMON ENG.
    # ---------------------------------------
    def on_update(self, ev):
        if self.game_over:
            if not self.__ready_to_exit:
                TetrisCtrl.commit_score(self.boardmodel.score)
                self.__ready_to_exit = True

    def on_keydown(self, ev):
        key = ev.key

        if key == pygame.K_ESCAPE:
            self.pev(pyv.EngineEvTypes.StatePop)
        elif key == pygame.K_RETURN and self.__ready_to_exit:
            self.pev(pyv.EngineEvTypes.StatePop)

        elif key == pygame.K_LEFT:
            self.boardmodel.move_piece(-1, 0)
        elif key == pygame.K_RIGHT:
            self.boardmodel.move_piece(1, 0)
        elif key == pygame.K_UP:
            self.boardmodel.rotate_piece()
        elif key == pygame.K_DOWN:
            self.boardmodel.move_piece(0, 1)

        elif key == pygame.K_a:
            self.boardmodel.rotate_piece(clockwise=False)
        elif key == pygame.K_s:
            self.boardmodel.rotate_piece()

        elif key == pygame.K_SPACE:
            self.boardmodel.full_drop_piece()

        # TODO fix the end game
        # elif key == pygame.K_RETURN:
        #     if self.__ready_to_exit:
        #         self.pev(pyv.EngineEvTypes.StatePop)
        #     elif glvars.DEV_MODE:  # activation manuelle possible en dev...
        #         pygame.time.set_timer(self.SHAKE_EV, 75)

    def on_paint(self, ev):
        self.render_frame(ev.screen)

    def on_drop(self, ev):
        self.boardmodel.drop_piece()

    def on_game_lost(self, ev):
        self.flag_games_over()
        glvars.ev_manager.set_interval(
            TetrisCtrl.get_level_speed(1),
            MyEvTypes.Drop  # self.DROP_EV,
        )
        # TODO fix
        # pygame.time.set_timer(self.SHAKE_EV, 0)

    def proc_event(self, ev, source):
        if ev.type == self.SHAKE_EV:
            self.boardmodel.more_quake()

        elif ev.type == MyEvTypes.FlatWorld:
            pygame.time.set_timer(self.SHAKE_EV, 0)

        elif ev.type == MyEvTypes.LevelUp:
            pygame.time.set_timer(self.DROP_EV, TetrisCtrl.get_level_speed(ev.level))
            pygame.time.set_timer(self.SHAKE_EV, 50)

    @staticmethod
    def get_level_speed(level):
        given_spd = {
            1: 1000,
            2: 750,
            3: 563,
            4: 422,
            5: 316,
            6: 237,
            7: 180,
            8: 170,
            9: 160
        }

        if level < 1:
            raise ValueError('level must be greater than 1')

        try:
            return given_spd[level]

        except KeyError:
            superlvl = level - 10
            delta = 50.0 / (1 + superlvl)
            return 100 + int(delta)

    def render_frame(self, ref_screen):
        self.boardmodel.met_a_jour_vue(self.view)  # TODO faire en sorte que vue tjr à jour
        # TODO faire en sorte que la vue se dessine tt seule (et pas quil faille que le ctrl lui dise quand le faire)

        if self.show_action is not None:
            self.show_action()
        self.view.draw_content(ref_screen)
        if self.game_over:
            self.view.show_game_over(ref_screen)

    def setup_ctrl(self):
        glvars.ev_manager.set_interval(
            TetrisCtrl.get_level_speed(1),
            MyEvTypes.Drop  # self.DROP_EV,
        )


import katagames_sdk as katasdk
katasdk.bootstrap(1)

# kataen = kengi = katasdk.import_kengi()
import katagames_engine as kengi
kengi.bootstrap_e()


import glvars
# from katagames_sdk.capsule.networking.httpserver import HttpServer
from defs import GameStates
import loctexts
from app.puzzle.state import PuzzleState
from app.title_screen.state import TitleScreenState

pygame = katasdk.import_pygame()

old_v_kengi = katasdk.import_kengi()
HttpServer = old_v_kengi.network.HttpServer  # katasdk.network.HttpServer in future versions


def run_game():
    kengi.init()
    glvars.init_fonts_n_colors()
    loctexts.init_repo(glvars.CHOSEN_LANG)

    kengi.declare_states(
        GameStates,
        {
            GameStates.TitleScreen: TitleScreenState,
            GameStates.Puzzle: PuzzleState
        },
        glvars
    )

    # - juste un test réseau, ce reset game ne sert a rien pour BLOKU-MAN,
    # il est utile pour mConquest...
    serv = HttpServer.instance()
    url = 'https://sc.gaudia-tech.com/tom/'
    params = {}
    full_script = url+'resetgame.php'
    print(full_script)
    res = serv.proxied_get(full_script, params)

    # - fin test réseau

    if not glvars.DEV_MODE:
        serv.set_debug_info(False)
    
    # cgm_engine.init(glvars.SCREEN_SIZE)
    # pygame.display.set_caption(tsl(Labels.WindowCaption))

    game_ctrl = kengi.get_game_ctrl()
    game_ctrl.turn_on()

    # launch the game, exit properly
    game_ctrl.loop()
    pygame.mixer.quit()

    if not kataen.runs_in_web():
        kataen.cleanup()


if __name__ == "__main__":
    run_game()

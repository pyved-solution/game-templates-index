import json

from . import glvars
from . import pimodules


pyv = pimodules.pyved_engine
pyv.bootstrap_e()
pyg = pyv.pygame
netw = pimodules.network  # important! used for get/post

screen = None
r4 = pyg.Rect(32, 32, 128, 128)
kpressed = set()
labels = [None, None]
ft = pyg.font.Font(None, 21)
gameserver_host = None

# TODO is there a way to enable pyved to provide metadata for the current game being executed??
SLUG_CART = 'SpinTheWheel'


def fetch_endpoint_gameserver() -> str:
    # read the content from remote file "servers.json", and provide the ad-hoc URL
    # the game host is provided by what can be read on "http://pyvm.kata.games/servers.json"

    tmp = netw.get(
        'http://pyvm.kata.games', '/servers.json'
    ).to_json()
    print(tmp)
    game_server_infos = tmp[SLUG_CART]
    target_game_host = game_server_infos['url']
    return target_game_host


def test_my_luck() -> tuple:
    """
    :return: a pair of integer values. The second one can be None
    """
    global gameserver_host
    print('call test my luck ------..........')
    # we have to use .text on the result bc we wish to pass a raw Serial to the model class
    netw_reply = netw.get('', gameserver_host, data={'jwt': glvars.stored_jwt})
    try:  # stop if error, stop right now as it will be easier to debug
        json_obj = json.loads(netw_reply.text)
        a, b = json_obj["serverNumber1"], json_obj["serverNumber2"]
        return a, b
    except json.JSONDecodeError:
        print(' --Warning-- : cant decode the JSON reply, after game server script has been called!')
        return None, None


@pyv.declare_begin
def init_game(vmst=None):
    global screen, gameserver_host

    pyv.init(wcaption='Untitled pyved-based Game')

    glvars.stored_jwt = netw.get_jwt()
    glvars.stored_username = netw.get_username()
    screen = pyv.get_surface()
    print("jwt:", glvars.stored_jwt)
    print("username:", netw.get_username())

    gameserver_host = fetch_endpoint_gameserver()


@pyv.declare_update
def upd(time_info=None):
    global labels

    for ev in pyg.event.get():
        if ev.type == pyg.QUIT:
            pyv.vars.gameover = True
        elif ev.type == pyg.KEYDOWN:
            if ev.key == pyg.K_SPACE:
                print('spinning!')
                spin_result = test_my_luck()
                print('rez:', spin_result)

    screen.fill('paleturquoise3')
    #if len(kpressed):
    #    pyv.draw_rect(screen, 'orange', r4)
    pyv.flip()


@pyv.declare_end
def done(vmst=None):
    pyv.close_game()
    print('gameover!')

"""
two states:
- menu (choose your side+connect to the server)
- default (ingame)
"""
import shared
from default import *
from menu import *
from shared import pyv, pygame, SCREEN_HEIGHT, SCREEN_WIDTH, GREEN


def game_init():
    pyv.init((SCREEN_WIDTH, SCREEN_HEIGHT), title="Breakout-Pong Crossover")

    # -----------------
    #  build the 'default' state
    # -----------------
    shared.bricks = new_bricks()
    shared.left_paddle = new_paddle('left')
    shared.right_paddle = new_paddle('right')
    new_ball()

    # -----------------
    #  build the 'menu' state
    # -----------------
    pyv.switch_world('menu')
    shared.ft = pygame.font.Font(None, 48)

    new_label('select your side:',  (30, 128), GREEN)
    shared.connecting_msg = new_label(
        'connecting...', (50, 200), GREEN
    )
    pyv.actor_state(shared.connecting_msg).visible = False

    def side_selection_left():
        print('client selects: left side')
        shared.connection_required = True
        shared.local_player = 'left'
        # remove buttons
        pyv.del_actor(shared.button_a, shared.button_b)

    def side_selection_right():
        print('client selects: right side')
        shared.connection_required = True
        shared.local_player = 'right'
        # remove buttons
        pyv.del_actor(shared.button_a, shared.button_b)

    shared.button_a = new_button(
        'left side', (30, 200), (150, 50), side_selection_left
    )
    shared.button_b = new_button(
        'right side', (465, 200), (150, 50), side_selection_right
    )

    # turn on the netw interface
    netw_layer = pyv.build_netw_layer('socket', 'client')
    # netw_layer = pyv.build_netw_layer('ws', 'client')

    pyv.init_network_layer(netw_layer)
    print('connecting to server (thru ws)...')

    netw_layer.start_comms(shared.HOST, shared.PORT)


def game_update(dt=None):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pyv.playing = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            pyv.post_ev('mouseclick', pos=pygame.mouse.get_pos())
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                pyv.post_ev("x_move_paddle", player=shared.local_player, dir="up")
            elif event.key == pygame.K_DOWN:
                pyv.post_ev("x_move_paddle", player=shared.local_player, dir="down")

    if pyv.get_curr_world() == 'menu':
        pyv.screen.fill('darkblue')  # draw bg for the menu

        if shared.connection_required and not shared.signal_sent:
            pyv.actor_state(shared.connecting_msg).visible = True
            # travail effectif sur la partie réseau
            pyv.post_ev('x_client_connects', player=shared.local_player)
            shared.signal_sent = True

            pyv.switch_world('default')
        return

    # - default
    # keys = pygame.key.get_pressed()
    # if keys[pygame.K_w]:
    #     pyv.ev_post("x_move_paddle", player=shared.local_player, dir="up")
    # if keys[pygame.K_s]:
    #     pyv.ev_post("x_move_paddle", "down")
    # if keys[pygame.K_UP]:
    #     pyv.ev_post("x_move_paddle", player=shared.local_player, dir="up")
    # if keys[pygame.K_DOWN]:
    #     pyv.ev_post("x_move_paddle", player=shared.local_player, dir="down")

    pyv.screen.fill((40, 40, 15))  # clear backgound with a dark yellow-ish color


def game_exit():
    print('bye!')


pyv.game_loop(locals())  # run the game

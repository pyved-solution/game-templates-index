"""
~ Server-side code ~

This needs to run concurrently to gamedef.py (the game client), so that clients can connect & sync
"""
import time

import glvars
import pyved as pyv
from model import new_paddle, new_ball, new_bricks


def new_gameserver():
    actor_type, data = 'gameserver', {
        "clients_connected": 0,
    }

    def on_x_client_connects(this, ev):
        this.clients_connected += 1
        if this.clients_connected == 2:
            pyv.post_ev('x_begin_match')
            glvars.match_started = True

    return pyv.new_actor(locals())


if __name__ == '__main__':
    # based on socket:
    netw_layer = pyv.build_netw_layer('socket', 'server')

    pyv.init_network_layer(netw_layer)
    netw_layer.start_comms(glvars.HOST, glvars.PORT)

    # init
    glvars.left_paddle = new_paddle('left')
    glvars.right_paddle = new_paddle('right')
    glvars.bricks = new_bricks()
    new_ball()
    new_gameserver()

    # server-side game loop
    cpt = 100
    ff = 1
    while True:
        pyv.post_ev('update', info_t=time.time())
        pyv.process_events()
        # glvars.mediator.update(True)  # True=saving cycles will send updates less frequently,
        # it can prevent sync errors on the socket interface, but creates a bit of lag
        cpt -= 1
        if cpt <= 0:
            ff = ff ^ 1  # flip bit
            print('  .tick. ' if ff else ' .tac. ')
            cpt = 100

        time.sleep(0.05)

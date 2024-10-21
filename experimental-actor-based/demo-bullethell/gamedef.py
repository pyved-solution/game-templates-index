import pygame
import pyved as pyv


SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
BLUE = (0, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)


def new_npc():
    actor_type, data = 'npc', {
        # demo of how components can be used (2/2)
        "x": -188+(SCREEN_WIDTH//2), "y": 55,
        "color": "pink",
        "mobile_size": 20
    }

    def on_draw(this, ev):
        pygame.draw.circle(pyv.screen, this.color, (this.x, this.y), this.mobile_size)
    return pyv.new_actor(locals())


def new_avatar(bx, by):
    # ---------------------------
    #  data
    # ---------------------------
    actor_type, data = 'avatar', {
        "x": bx, "y": by,
        "delta_px": 3,  # its like the avatar's speed
        "color": GREEN,
        "mobile_size": 13
    }

    # ---------------------------
    #  callable functions
    # ---------------------------
    def reset_pos(this):
        print('coucou je suis GREEN')

    # ---------------------------
    #  behavior
    # ---------------------------
    def on_move_avatar(this, ev):
        if ev.dir == "right":
            this.x += this.delta_px  # max(this.pos[1] - 5, 0)
        elif ev.dir == "left":
            this.x -= this.delta_px  # min(this.pos[1] + 5, SCREEN_HEIGHT - PADDLE_HEIGHT)
        elif ev.dir == "up":
            this.y -= this.delta_px
        elif ev.dir == "down":
            this.y += this.delta_px

    def on_update(this, ev):
        if pyv.get_curr_world() == 'default':
            if this.x > SCREEN_WIDTH-33:
                this.x = SCREEN_WIDTH-50
                pyv.switch_world('jungle')
        elif pyv.get_curr_world() == 'jungle':
            if this.x < 33:
                this.x = 50
                pyv.switch_world('default')

    def on_draw(this, ev):
        if pyv.get_curr_world() == 'default':
            pyv.screen.fill('darkred')
        else:
            pyv.screen.fill('gray6')
        pygame.draw.circle(pyv.screen, this.color, (this.x, this.y), this.mobile_size)

    return pyv.new_actor(locals())


# ----------------------------
# important declarations
# ----------------------------
def game_init():
    pyv.init((SCREEN_WIDTH, SCREEN_HEIGHT), title="Test with avatar and rooms")

    # prepare world #2
    pyv.switch_world('jungle')
    avatar_jungle = new_avatar(50, SCREEN_HEIGHT//2)
    pyv.actor_exec(avatar_jungle, 'reset_pos')  # move the avatar to a cool location
    print('a new av has been initiated (in jungle):', avatar_jungle)

    # go back to the default world
    pyv.switch_world('default')
    new_avatar(SCREEN_WIDTH//2, SCREEN_HEIGHT//2)
    new_npc()


def game_update(dt=None):  # will be called BEFORE event dispatching...
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pyv.playing = False
    # Keyboard input
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        pyv.post_ev("move_avatar", dir="left")
    if keys[pygame.K_RIGHT]:
        pyv.post_ev("move_avatar", dir="right")
    if keys[pygame.K_UP]:
        pyv.post_ev("move_avatar", dir="up")
    if keys[pygame.K_DOWN]:
        pyv.post_ev("move_avatar", dir="down")


def game_exit():
    print('bye!')


# launch the game
if __name__ == '__main__':
    pyv.game_loop(locals())

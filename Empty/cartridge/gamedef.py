from .glvars import pyv


# TODO cmt les sprites sont stackés? faut preciser dans la doc!

pyv.bootstrap_e()

r4 = pyv.new_rect_obj(128, 256, 200, 200)
kpressed = set()
text_surface = None
text_pos = (250, 168)
text_color = '#a1eeff' # 'black'


def init(vmst=None):
    global text_surface
    pyv.init(wcaption='Untitled, empty, and pyved-based demo')
    print('-'*32)
    print('press one or two key (any key) to see something cool')
    font_size = 48
    font_obj = pyv.new_font_obj(None, font_size)  # None -> the defaut font
    text_surface = font_obj.render('hello', False, text_color)


def update(time_info=None):
    for ev in pyv.evsys0.get():
        if ev.type == pyv.evsys0.QUIT:
            pyv.vars.gameover = True
        elif ev.type == pyv.evsys0.KEYDOWN:
            kpressed.add(ev.key)
        elif ev.type == pyv.evsys0.KEYUP:
            kpressed.remove(ev.key)

    # logic?
    pass
    
    # refresh screen
    screen_surface = pyv.get_surface()
    screen_surface.fill('paleturquoise3')

    # montre l'affichage du texte, a une position (x,y)
    screen_surface.blit(text_surface, text_pos)  # add some text
    if len(kpressed)==1:
        screen_surface.blit(
            pyv.vars.images['lion'], (r4[0]-100, r4[1]-200)
        )

    # TODO ca serait intéressant de mettre aussi l'affichage d'un sprite animé
    elif len(kpressed)==2:
        pyv.draw_rect(screen_surface, 'orange', r4)
    pyv.flip()


def close(vmst=None):
    pyv.close_game()
    print('gameover!')

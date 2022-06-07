import random

from gradients import ColorInterpolator
from engine_events import CogObject
from ev_types import MyEvTypes
import glvars


COLOR_PAL = (
    (255,255,192),  # jaune pale
    (255,64,0)  # orange vif
)
Rfunc = (lambda x: x)
Gfunc = (lambda x: x)
Bfunc = (lambda x: x)
Afunc = (lambda x: 1)
mode = 0
interpolator = ColorInterpolator(1.0, COLOR_PAL[0], COLOR_PAL[1], Rfunc, Gfunc, Bfunc, Afunc)

UTIL_MIN = 5
UTIL_MAX = 53

POIDS_MIN = 1.7
POIDS_MAX = 7.9

TAILLE_MIN = 8
TAILLE_MAX = 40


class ItemEmportable(CogObject):

    X_DECAL = 425  # quand cest pris ds le sac

    DECAL_X_HITBOX = 0
    DECAL_Y_HITBOX = -20

    OFFSET_X_HITBOX = 6
    OFFSET_Y_HITBOX = 24

    NB_IT_PAR_LIGNE = 7

    def __init__(self, rang):
        super().__init__()

        self.__w = round(random.uniform(POIDS_MIN, POIDS_MAX), 1)
        self.utilite = random.randint(UTIL_MIN, UTIL_MAX)

        self.choisi = False
        self.rang = rang

        self.basepos = ItemEmportable.calc_base_pos(rang)

        self.position = None
        self.__update_pos()

        ratio_util = (self.utilite - UTIL_MIN) / (UTIL_MAX - UTIL_MIN)
        self.couleur = tuple(interpolator.do_eval(ratio_util)[:3])

        ratio_poids = (self.__w - POIDS_MIN) / (POIDS_MAX - POIDS_MIN)
        delta = TAILLE_MAX - TAILLE_MIN
        compo = int(TAILLE_MIN + ratio_poids * delta)
        self.taille = (compo, compo)

        # a priori, attribue une lettre pour désigner l'item
        self.nom = ItemEmportable.det_nom(rang)

        # création de l'image pour la lettre
        ma_fonte = glvars.fonts['basic']
        self.bigfont = glvars.fonts['medium']
        self.img_lettre = ma_fonte.render(self.nom, True, glvars.colors['noir'])

        self.img_wg = ma_fonte.render('{}kg'.format(self.__w), False, glvars.colors['noir'], self.couleur)
        self.img_util = self.bigfont.render('u{}'.format(self.utilite), False, self.couleur)

        self.__hitbox_visible = False
        self.__hitbox_pos = [self.position[0] + self.DECAL_X_HITBOX, self.position[1] + self.DECAL_Y_HITBOX]
        self.__hitbox_size = (44, 78)  #self.taille[0] + self.OFFSET_X_HITBOX, self.taille[1] + self.OFFSET_Y_HITBOX )

    @staticmethod
    def calc_base_pos(rang_0_a_51):
        # en pixels...
        xoffset = 49
        yoffset = 64

        # base pos(scr coords)for item such as  i,j  = 0,0 in the grid
        res = [5, 75]

        # x soit la quantité d'items par ligne....
        x_quantity = ItemEmportable.NB_IT_PAR_LIGNE

        j = rang_0_a_51 // x_quantity
        res[1] += j * yoffset
        i = rang_0_a_51 % x_quantity
        res[0] += i * xoffset
        return res

    @staticmethod
    def det_nom(rang_0_a_51):
        pl_alphabet = rang_0_a_51 % 26
        lettre = chr(65 + pl_alphabet)  # on sait 65 est le code ascii de 'A'
        if rang_0_a_51 < 26:
            return '_{}_'.format(lettre)

        return '<{}>'.format(lettre)

    def get_weight(self):
        return self.__w

    def reset(self):
        self.choisi = False
        self.__update_pos()

    def __update_pos(self):
        xval = self.basepos[0] if (not self.choisi) else self.basepos[0] + self.X_DECAL

        self.position = (xval, self.basepos[1])
        self.__hitbox_pos = [
            self.position[0] + self.DECAL_X_HITBOX,
            self.position[1] + self.DECAL_Y_HITBOX
        ]

    def get_util(self):
        return self.utilite

    def is_taken(self):
        return self.choisi

    def collides(self, mpos):
        x, y = self.__hitbox_pos
        w, h = self.__hitbox_size
        if x < mpos[0] < x + w:
            if y < mpos[1] < y + h:
                return True
        return False

    def toggle_taken(self):
        if self.choisi:
            self.choisi = False
        else:
            self.choisi = True
        self.__update_pos()
        self.pev(MyEvTypes.ContentChanges)

    def dessin(self, screen):
        if self.__hitbox_visible:
            x, y = self.__hitbox_pos
            w, h = self.__hitbox_size
            rectinfo = (x, y, w, h)
            pygame_emu.draw.rect(screen, glvars.colors['superdark'], rectinfo, 2)

        x, y = self.position
        w, h = self.taille
        rectinfo = (x, y, w, h)
        pygame_emu.draw.rect(screen, self.couleur, rectinfo)

        # - dessin util
        tmp = list(self.position)
        tmp[1] -= 24
        screen.blit(self.img_util, tmp)

        # - dessin poids
        tmp = list(self.position)
        tmp[1] += 25
        screen.blit(self.img_wg, tmp)

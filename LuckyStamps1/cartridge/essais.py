import random
import json


dummy_tirage_result = """
[
  [
    [
      0,
      "c0",
      3,
      7,
      6
    ],
    [
      0,
      "c1",
      5,
      5,
      1
    ],
    [
      0,
      "c2",
      6,
      3,
      2
    ],
    [
      0,
      "c3",
      1,
      2,
      4
    ],
    [
      0,
      "c4",
      3,
      4,
      7
    ],
    [
      1,
      "c0",
      7,
      5,
      3
    ],
    [
      1,
      "c1",
      5,
      5,
      5
    ],
    [
      1,
      "c2",
      1,
      1,
      4
    ],
    [
      1,
      "c3",
      4,
      6,
      5
    ],
    [
      1,
      "c4",
      3,
      -1,
      6
    ],
    [
      1,
      "c4",
      2,
      5,
      1
    ],
    [
      2,
      "c0",
      7,
      4,
      7
    ],
    [
      2,
      "c1",
      7,
      5,
      4
    ],
    [
      2,
      "c2",
      5,
      4,
      3
    ],
    [
      2,
      "c3",
      4,
      3,
      6
    ],
    [
      2,
      "c4",
      6,
      6,
      0
    ],
    [
      3,
      "c0",
      5,
      7,
      6
    ],
    [
      3,
      "c1",
      6,
      1,
      6
    ],
    [
      3,
      "c2",
      3,
      3,
      5
    ],
    [
      3,
      "c3",
      3,
      6,
      3
    ],
    [
      3,
      "c4",
      1,
      5,
      1
    ],
    [
      4,
      "c0",
      5,
      7,
      5
    ],
    [
      4,
      "c1",
      4,
      6,
      7
    ],
    [
      4,
      "c2",
      2,
      3,
      4
    ],
    [
      4,
      "c3",
      1,
      2,
      6
    ],
    [
      4,
      "c4",
      5,
      2,
      4
    ]
  ],
  [
    0,
    0,
    0,
    0,
    0
  ]
]
"""


class ModelisationTirage:
    BOMB_CODE = -1
    RERUN_BONUS_CODE = 0

    def __init__(self):
        self.li_events = list()
        self.li_gains = list()

    @classmethod
    def pioche(cls):
        if random.random() < 0.015:
            return 0
        if random.random() < 0.05:
            return -1
        return random.choice(tuple(range(1, 8)))

    def generation(self):
        # première passe pour cet algorithme
        # ----------------------------------
        cpt_tirages = 3
        cls = self.__class__
        numero_tirage = -1
        self.li_events = list()
        while cpt_tirages > 0:
            numero_tirage += 1
            cpt_tirages -= 1
            a_lancer = [0, 1, 2, 3, 4]
            li_courante = list()
            while len(a_lancer) > 0:
                col_rank = a_lancer.pop(0)
                nouv_elt = [numero_tirage, 'c'+str(col_rank), cls.pioche(), cls.pioche(), cls.pioche()]
                li_courante.append(nouv_elt)
                for k, v in enumerate(nouv_elt):
                    if k == 0 or k == 1:
                        continue
                    if v == cls.BOMB_CODE:
                        a_lancer.append(col_rank)
                        break
            for col in li_courante:
                for k, v in enumerate(col):
                    if k == 0 or k == 1:
                        continue
                    if v == cls.RERUN_BONUS_CODE:
                        cpt_tirages += 2
                        break
            self.li_events.extend(li_courante)

        # todo: do it FOR REAL
        # la seconde passe,
        # qui a besoin de parser les colonnes tant qu'on a pas atteint le tirage T+1 et qui,
        # juste avant de passer au tirage T+1 va analyser le contenu de la grille (ens.
        self.li_gains = [0 for _ in range(numero_tirage+1)]

    def dump(self):
        t = json.dumps([self.li_events, self.li_gains])
        print(t)


# ----------------------------------
#  test génération
# ----------------------------------
# import sys
# tmp = ModelisationTirage()
# tmp.generation()
# tmp.dump()
# sys.exit(1)
# ----------------------------------

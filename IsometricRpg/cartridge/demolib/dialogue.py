import json

from . import rpgmenu
from ..custom_events import MyEvTypes
from ..glvars import pyv


# - aliases
frects = pyv.polarbear.frects
default_border = pyv.polarbear.default_border
draw_text = pyv.polarbear.draw_text
pygame = pyv.pygame
EngineEvTypes = pyv.EngineEvTypes
EventReceiver = pyv.EvListener


class Offer(object):
    # An Offer is a single line spoken by the NPC.
    # "effect" is a callable with no parameters.
    # "replies" is a list of replies.
    def __init__(self, msg, effect=None, replies=()):
        self.msg = msg
        self.effect = effect
        self.replies = list(replies)

    def __str__(self):
        return self.msg

    @classmethod
    def from_json(cls, jdict):
        # We spoke about not needing a json loader yet. But, in terms of hardcoding a conversation, it was just as
        # easy to write this as to hand-code a dialogue tree.
        msg = jdict.get("msg", "Hello there!")
        effect = None
        replies = list()
        for rdict in jdict.get("replies", ()):
            replies.append(Reply.from_json(rdict))
        return cls(msg, effect, replies)

    @classmethod
    def load_json(cls, filename):
        with open(filename) as f:
            jdict = json.load(f)
        return cls.from_json(jdict)


class Reply(object):
    # A Reply is a single line spoken by the PC, leading to a new offer
    def __init__(self, msg, destination=None):
        self.msg = msg
        self.destination = destination

    def __str__(self):
        return self.msg

    def apply_to_menu(self, mymenu):
        mymenu.add_item(self.msg, self.destination)

    @classmethod
    def from_json(cls, jdict):
        msg = jdict.get("msg", "And you too!")
        destination = jdict.get("destination")
        if destination:
            destination = Offer.from_json(destination)
        return cls(msg, destination)


class ConversationView(EventReceiver):
    # The visualizer is a class used by the conversation when conversing.
    # It has a "text" property and "render", "get_menu" methods.
    TEXT_AREA = frects.Frect(-75, -100, 300, 100)
    MENU_AREA = frects.Frect(-75, 30, 300, 80)
    PORTRAIT_AREA = frects.Frect(-240, -110, 150, 225)

    def __init__(self, root_offer, pre_render=None):
        super().__init__()
        self.text = ''
        self.root_offer = root_offer
        self.pre_render = pre_render
        self.font = pyv.vars.data['DejaVuSansCondensed-Bold']  # using pre-load via engine
        self.portrait = pyv.vars.images['mysterious_stranger']
        self.curr_offer = root_offer
        self.dialog_upto_date = False
        self.existing_menu = None
        self.screen = pyv.get_surface()

    def turn_off(self):  # because the conversation view can be closed from "outside" i.e. the main program
        if self.existing_menu:
            self.existing_menu.turn_off()
        super().turn_off()

    def on_event(self, ev):
        if ev.type == EngineEvTypes.Paint:
            self.render()

        elif ev.type == EngineEvTypes.Update:
            if self.curr_offer is not None:
                if self.dialog_upto_date:
                    return
                if self.existing_menu:
                    self.existing_menu.turn_off()

                self.dialog_upto_date = True
                self.text = self.curr_offer.msg

                # create a new Menu inst.
                mymenu = rpgmenu.Menu(
                    self.MENU_AREA.dx, self.MENU_AREA.dy, self.MENU_AREA.w, self.MENU_AREA.h,
                    border=None, predraw=self.render)
                mymenu.turn_on()

                self.existing_menu = mymenu
                for i in self.curr_offer.replies:
                    i.apply_to_menu(mymenu)
                if self.text and not mymenu.items:
                    mymenu.add_item("[Continue]", None)
                else:
                    mymenu.sort()
                nextfx = self.curr_offer.effect
                if nextfx:
                    nextfx()

            else:
                # auto-close everything
                self.turn_off()
                self.pev(MyEvTypes.ConvEnds)

        elif ev.type == MyEvTypes.ConvChoice:  # ~ iterate over the conversation...
            self.dialog_upto_date = False
            self.curr_offer = ev.value

    def render(self):
        if self.pre_render:
            self.pre_render()
        text_rect = self.TEXT_AREA.get_rect()
        default_border.render(text_rect)
        draw_text(self.font, self.text, text_rect)
        default_border.render(self.MENU_AREA.get_rect())
        self.screen.blit(self.portrait, self.PORTRAIT_AREA.get_rect())

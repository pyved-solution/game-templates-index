import sys
import glvars
from katagames_sdk.engine import EventReceiver, EngineEvTypes
import katagames_sdk.engine as kataen

pygame = kataen.import_pygame()
# sys.path.append('..')


def test_func():
    print( "Button clicked!")


class Button(EventReceiver):

    HIDEOUS_PURPLE = (255, 0, 255)

    def __init__(self, font, text, position_on_screen, callback=None, draw_background=True):
        super().__init__()
        padding_value = 20  # pixels

        if draw_background:
            self.bg_color = (100, 100, 100)
            self.fg_color = (255, 255, 255)
        else:
            self.bg_color = self.HIDEOUS_PURPLE
            self.fg_color = (0, 0, 0)

        # data
        self._callback = callback
        self._text = text
        self._hit = False
        
        # dawing
        self.font = font
        self.txt = text
        size = font.size(text)
        self.tmp_size = size
        self.position = position_on_screen
        self._col_rect = pygame.Rect(self.position, size).inflate(padding_value, padding_value)
        self._col_rect.topleft = self.position
        
        self.image = None
        self.refresh_img()

    def refresh_img(self):
        self.image = pygame.Surface(self._col_rect.size).convert()
        self.image.fill(self.bg_color)

        if self.bg_color != self.HIDEOUS_PURPLE:
            textimg = self.font.render(self.txt, True, self.fg_color, self.bg_color)
        else:
            textimg = self.font.render(self.txt, False, self.fg_color)
        xpos = (self._col_rect.width - self.tmp_size[0]) / 2
        ypos = (self._col_rect.height - self.tmp_size[1]) / 2
        self.image.blit(textimg, (xpos, ypos))

        if self.bg_color == self.HIDEOUS_PURPLE:
            self.image.set_colorkey((self.bg_color))
            box_color = (190,)*3
            full_rect = (0, 0, self.image.get_size()[0], self.image.get_size()[1])
            pygame.draw.rect(self.image, box_color, full_rect, 1)

    # pour des raisons pratiques (raccourci)
    def get_size(self):
        return self.image.get_size()

    def proc_event(self, ev, source):
        if ev.type == pygame.KEYDOWN:
            self.on_keydown(ev)
        elif ev.type == pygame.MOUSEMOTION:
            self.on_mousemotion(ev)
        elif ev.type == pygame.MOUSEBUTTONDOWN:
            self.on_mousedown(ev)
        elif ev.type == pygame.MOUSEBUTTONUP:
            self.on_mouseup(ev)

    def on_keydown(self, event):
        """
        Decides what do to with a keypress.
        special meanings have these keys: 
        enter, left, right, home, end, backspace, delete
        """
        if event.type != pygame.KEYDOWN:
            print( "textentry got wrong event: " + str(event))
        else:
            self.render()
### debug
            # if __name__=='__main__' and event.key == pygame.K_ESCAPE:
            #     events.RootEventSource.instance().stop()
        
    def on_mousedown(self, event):
        pos = event.pos
        if self._col_rect.collidepoint(pos):
            self._hit = True

    def on_mouseup(self, event):
##        print "mouse button up", event.pos
##        print self._up_col_rect
##        print self._down_col_rect
        pos = event.pos
        if self._hit and self._col_rect.collidepoint(pos):
            if self._callback:
                self._callback()
        self._hit = False
        
    def on_mousemotion(self, event):
        pass
        
    def set_callback(self, callback):
        self._callback = callback
        
    def render(self):
        """
        
        """
        pass
        
    def update(self):
        """
        Actually not needed. (only need if this module is run as a script)
        """
        # only need if this module is run as a script
        if __name__ == '__main__':
##            print "_min_w:", self._min_w, "len items:", len(self._items)
            screen = pygame.display.get_surface()
            screen.fill( (100, 0, 0))
            screen.blit(self.image, self.position)
##            pygame.draw.rect(screen, (255,255,0), self._text_col_rect, 1)
##            pygame.draw.rect(screen, (255,255,0), self._up_col_rect, 1)
##            pygame.draw.rect(screen, (255,255,0), self._down_col_rect, 1)
            pygame.display.flip()


# if __name__ == '__main__':
#     pygame.init()
#     pygame.key.set_repeat(500, 30)
#     pygame.display.set_mode((800,600))
#     t = Button(pygame.font.Font(None, 30), "cancel", (100,100), test_func)
#
# ##    tt = Spinner(pygame.font.Font(None, 30), (300,100))
# ##    tt.add(Item("Human", 1))
# ##    tt.add(Item("passive AI", 2))
# ##    tt.add(Item("dumb AI", 3))
# ##    tt.add(Item("better AI", 4))
# ##    tt.add(Item("None", 5))
#
#     events.RootEventSource.instance().add_listener(t)
#     print( t.parent)
#     events.RootEventSource.instance().set_blocking(True)
#     events.RootEventSource.instance().run(t.update)


class TextInput(EventReceiver):
    """
    Simple text entry component.
    """

    _caret_color = (90, 90, 90)
    _padding = 4  # en px

    def __init__(self, nickname, font, how_to_process_cb, pos, width=300):
        """
        nickname: nickname, all messages will be prefixed with the nickname
        font    : pygame.font.Font object
        width   : in pixel that this element can use (this restricts the number
                  of char you can enter

        events:
        in : pygame.KEYDOWN
        out: eventtypes.CHATMSG
        """
        super().__init__()

        self.position = pos
        # test que le 3e arg est callable...
        assert hasattr(how_to_process_cb, '__call__')
        self.on_enter_func = how_to_process_cb

        self.pwd_field = False

        # data
        self.__txt_content = ""
        self.caretpos = 0
        self.max = 255
        self.nickname = nickname

        # drawing
        self.dirty = True
        self.font = font
        height = self.font.get_ascent() - self.font.get_descent() + 1 + 4
        self.image = pygame.Surface((width, height)).convert()
        self.size = (width, height)

        self.text_color = (1, 1, 1)
        self.text_field_rect = pygame.Rect(0, 0, width - 1, height - 1)
        self.text_img = pygame.Surface((2, 2))
        self.pixel_width = width - 4

        self._focus = None
        self.fill_color = None
        self.no_focus()

    def get_disp_text(self):
        if self.pwd_field:
            return TextInput.hide_text(self.__txt_content)
        return self.__txt_content

    def focus(self):
        self._focus = True
        self.fill_color = (220, 220, 220)
        self.render_field()

    def no_focus(self):
        self._focus = False
        self.fill_color = (100, 100, 100)
        self.render_field()

    def contains(self, scr_pos):
        w, h = self.image.get_size()
        a, b = self.position[0], self.position[0] + w
        c, d = self.position[1], self.position[1] + h
        x, y = scr_pos
        if (a < x < b) and (c < y < d):
            return True
        return False

    @staticmethod
    def hide_text(txt_content):
        tmp = ['*' for i in range(len(txt_content))]
        return ''.join(tmp)

    def proc_event(self, event, source):
        if event.type != pygame.KEYDOWN:
            return

        # - traitement touche pressée
        if event.key == pygame.K_RETURN:
            # self.on_enter()
            self.on_enter_func(self.__txt_content)
            self.__txt_content = ''
            self.caretpos = 0

        elif event.key == pygame.K_RIGHT:
            self.move_caret(+1)

        elif event.key == pygame.K_LEFT:
            self.move_caret(-1)

        elif event.key == pygame.K_HOME:
            self.move_caret('home')

        elif event.key == pygame.K_END:
            self.move_caret('end')

        elif event.key == pygame.K_BACKSPACE:
            self.backspace_char()

        elif event.key == pygame.K_DELETE:
            self.delete_char()

        elif event.key == pygame.K_TAB:
            pass

        else:
            if event.unicode != '':
                if len(self.__txt_content) < self.max:
                    self.__txt_content = self.__txt_content[:self.caretpos] + event.unicode + self.__txt_content[
                                                                                              self.caretpos:]
                    self.caretpos += 1
        self.render_field()

    def move_caret(self, steps):
        """
        Moves the caret about steps. Positive numbers moves it right, negative
        numbers left.
        """
        if steps == 'home':
            self.caretpos = 0
        elif steps == 'end':
            self.caretpos = len(self.__txt_content)
        else:
            assert isinstance(steps, int)
            self.caretpos += steps

        if self.caretpos < 0:
            self.caretpos = 0
        if self.caretpos > len(self.__txt_content):
            self.caretpos = len(self.__txt_content)

    def backspace_char(self):
        """
        Deltes the char befor the caret position.
        """
        if self.caretpos > 0:
            self.__txt_content = self.__txt_content[:self.caretpos - 1] + self.__txt_content[self.caretpos:]
            self.caretpos -= 1

    def delete_char(self):
        """
        Deltes the char after the caret position.
        """
        self.__txt_content = self.__txt_content[:self.caretpos] + self.__txt_content[self.caretpos + 1:]

    def render_field(self):
        """
        Renders the string to self.image.
        """
        self.image.fill(self.fill_color)
        content = self.get_disp_text()

        if len(content):
            # while self.font.size(content)[0] > self.pixel_width:
            #    self.backspace_char()
            self.text_img = self.font.render(content, 1, self.text_color, self.fill_color)
            self.image.blit(self.text_img, (2, 2))

            # - draw caret
            xpos = self.font.size(content[:self.caretpos])[0] + 2
            pygame.draw.line(self.image, self._caret_color, (xpos, self._padding),
                             (xpos, self.image.get_height() - self._padding), 2)
        # else:
        #    pygame.draw.line(self.image, (255, 255, 255), (3, 2), (3, self.image.get_height() - 2), 1)

        pygame.draw.rect(self.image, (100, 100, 100), self.text_field_rect, 2)


# --- DÉMO. FONCTIONNEMENT
# if __name__ == '__main__':
#     coremon_main.init((800, 600))
#     pygame.key.set_repeat(500, 30)
#
#
#     def cb(texte):
#         print(texte)
#         print(TextInput.hide_text(texte))
#
#
#     txt_entry = TextInput("supernick:", glvars.fonts['courier_font'], cb, (100, 100))
#
#
#     class BasicView(EventReceiver):
#         def __init__(self, ref_te):
#             super().__init__()
#             self.te = ref_te
#
#         def proc_event(self, ev, source):
#             if ev.type == EngineEvTypes.PAINT:
#                 # print(te.text, len(te.text), te.caretpos)
#                 coremon_main.screen.fill((0, 0, 0))
#                 coremon_main.screen.blit(self.te.image, self.te.position)
#
#
#     bv = BasicView(txt_entry)
#     mger = EventManager.instance()
#     bv.turn_on()
#     txt_entry.turn_on()
#
#     ctrl = VanillaGameCtrl()
#     ctrl.turn_on()
#     ctrl.loop()
#     print('test terminé.')

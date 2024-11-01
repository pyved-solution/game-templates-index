from .glvars import pyv
from .constants import *
import random
from .sprites import Obstacle, BonusItem, Tower, Item, Explosion, Player, Mob, Runner


pg = pyv.pygame
tilemap = pyv.tmx.get_ztilemap_module()


class GameflowCtrl(pyv.EvListener):
    """
    utilitary class to react to events
    """
    def __init__(self, ref_world):
        super().__init__()
        self.world = ref_world

    def on_gameover(self, ev):
        print('set game over dans pyv')
        pyv.vars.gameover = True


class IngameText(pg.sprite.Sprite):
    def __init__(self, game, x, y, text, font_size=32):
        self._layer = EFFECTS_LAYER
        self.groups = game.all_sprites
        pg.sprite.Sprite.__init__(self, self.groups)
        self.game = game
        self.x = x
        self.y = y
        self.text = text
        font = pg.font.Font(self.game.title_font, font_size)  # font_name, size
        self.image = font.render(text, True, BLACK)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)


class GameWorld:
    # todo adapter architecture...
    #  soit vers MVC, soit vers actor-based

    def __init__(self):
        self.playing = True  # true when player selects 'new game' or 'continue'

        # attributs obligés
        self.screen = None  # init from outside
        self.camera = None
        self.all_sprites = None

        # a bit like constants / pre-init vars
        self.game_folder = 'assets'  # path.dirname(__file__)  # Where our game is running from
        # self.img_folder = path.join(self.game_folder, 'zassets')
        self.sound_folder = 'assets/'
        self.music_folder = 'assets/'

        self.map_folder = 'assets/maps'
        self.level_complete = False
        self.dt = 0  # mesure elapsed time between frames
        self.all_sounds = []
        self.soundfx_lvl = .6
        self.music_lvl = .8
        self.clock = pg.time.Clock()
        self.draw_debug = False  # afficher les collision rect ou non
        self.paused = False

        # fonts
        self.title_font = self.menu_font = self.hud_font = None
        # self.title_font = path.join(self.img_folder, 'DemonSker-zyzD.ttf')  # TTF = True Type Font
        # self.menu_font = path.join(self.img_folder, 'DemonSker-zyzD.ttf')  # TODO: Experiment
        # self.hud_font = path.join(self.img_folder, 'DemonSker-zyzD.ttf')

        # gfx
        self.fog = None
        self.wall_img = None
        self.mob_img = None
        self.runner_img = None
        self.gun_images = None
        self.light_mask = None
        self.light_rect = None
        self.dim_screen = None

        # sfx
        self.effects_sounds = None
        self.weapon_sounds = None
        self.player_hit_sounds = None
        self.zombie_death_sounds = None
        self.zombie_moan_sounds = None

        # for LOAD_DATA
        self.explosion_sheet = None
        self.explosion_frames = None
        self.bullet_images = dict()
        self.pistol_bullet_img = None
        self.shotgun_bullet_img = None
        self.uzi_bullet_img = None
        self.gun_flashes = []
        self.item_images = {}
        self.splat_images = {}

        # for LOAD_LEVEL
        self.current_music = None
        self.player = None
        self.walls = self.towers = self.mobs = None
        self.bullets = self.items = self.landmines = self.explosions = None
        self.current_lvl = None  # Grab our game layout file (map)
        self.player_img = None
        self.objective = None
        self.story = None
        self.map = None
        self.map_img = None
        self.map_rect = None
        self.texts = None
        self.comms_req = None

    def draw_text(self, text, font_name, size, color, x, y, align='nw'):
        font = pg.font.Font(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == 'nw':
            text_rect.topleft = (x, y)
        elif align == 'ne':
            text_rect.topright = (x, y)
        elif align == 'sw':
            text_rect.bottomleft = (x, y)
        elif align == 'se':
            text_rect.bottomright = (x, y)
        elif align == 'n':
            text_rect.midtop = (x, y)
        elif align == 'e':
            text_rect.midright = (x, y)
        elif align == 's':
            text_rect.midbottom = (x, y)
        elif align == 'w':
            text_rect.midleft = (x, y)
        elif align == 'center':
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    def load_data(self):
        # Setting up explosion animation
        self.explosion_sheet = cload_img('(zombies)explosion.png')
        self.explosion_frames = []
        expl_width = 130
        expl_height = 130
        x = 0
        y = -25
        # Creating and iterating through each "square" of the explosion spritesheet
        # TODO better use a sprsheet 'cause this does not work in web ctx
        for i in range(5):
            for j in range(5):
                img = pg.Surface((expl_width, expl_height))
                img.blit(self.explosion_sheet, (0, 0), (x, y, expl_width, expl_height))
                img.set_colorkey(BLACK)
                img = pg.transform.scale(img, (round(expl_width * 2.8), round(expl_height * 2.8)))
                self.explosion_frames.append(img)
                x += expl_width
            x = 0
            y += expl_height

        self.dim_screen = pg.Surface(self.screen.get_size()).convert_alpha()
        self.dim_screen.fill((0, 0, 0, 180))  # BLACK with 180 transparency
        self.wall_img = cload_img('(zombies)tile_179.png').convert_alpha()  # Surface

        # TODO scaling?
        # self.wall_img = pg.transform.scale(self.wall_img, (TILESIZE, TILESIZE))  # can scale image

        self.mob_img = cload_img('zombie1_hold.png').convert_alpha()  # Surface
        self.runner_img = cload_img(RUNNER_IMG).convert_alpha()
        # pg.draw.circle(surface, color, center, radius)  # Each image is a Surface
        self.gun_images = {}
        for gun in GUN_IMAGES:
            gun_img = cload_img(GUN_IMAGES[gun]).convert_alpha()
            gun_img = pg.transform.scale(gun_img, (32, 32))
            self.gun_images[gun] = gun_img

        self.bullet_images = {}
        self.pistol_bullet_img = pg.Surface((7, 7))
        self.bullet_images['pistol'] = self.pistol_bullet_img
        self.shotgun_bullet_img = pg.Surface((3, 3))
        self.bullet_images['shotgun'] = self.shotgun_bullet_img
        self.uzi_bullet_img = pg.Surface((4, 4))
        self.bullet_images['uzi'] = self.uzi_bullet_img
        self.gun_flashes = []

        # TODO adapt to web ctx
        for img in MUZZLE_FLASHES:
            self.gun_flashes.append(
                cload_img(img).convert_alpha()
            )

        self.item_images = {}
        for item in ITEM_IMAGES:
            self.item_images[item] = cload_img(ITEM_IMAGES[item]).convert_alpha()

        self.splat_images = []
        # TODO retablir giclées de sang, sprsheet si possible?
        # for img in SPLAT_IMAGES:
        #     i = pg.image.load(path.join(self.img_folder, img)).convert_alpha()
        #     i.set_colorkey(BLACK)
        #     i = pg.transform.scale(i, (64, 64))
        #     self.splat_images.append(i)

        # lighting effect
        self.fog = pg.Surface(pyv.get_surface().get_size())
        self.fog.fill(NIGHT_COLOR)

        self.light_mask = cload_img(LIGHT_MASK).convert_alpha()
        self.light_mask = pg.transform.scale(self.light_mask, LIGHT_RADIUS)
        self.light_rect = self.light_mask.get_rect()

        # PRE-load sounds
        if not NO_SOUND:
            pg.mixer.music.load(MENU_MUSIC)
            self.effects_sounds = {}
            for snd_type in EFFECTS_SOUNDS:
                snd = pg.mixer.Sound(EFFECTS_SOUNDS[snd_type])
                snd.set_volume(self.soundfx_lvl)
                self.effects_sounds[snd_type] = snd
                self.all_sounds.append(snd)

            self.weapon_sounds = {}
            for weapon in WEAPON_SOUNDS:
                self.weapon_sounds[weapon] = []
                for snd in WEAPON_SOUNDS[weapon]:
                    s = pg.mixer.Sound(snd)
                    s.set_volume(0.5)
                    self.weapon_sounds[weapon].append(s)
                    self.all_sounds.append(s)

            self.player_hit_sounds = []
            for snd in PLAYER_HIT_SOUNDS:
                s = pg.mixer.Sound(snd)
                self.player_hit_sounds.append(s)
                self.all_sounds.append(s)

            self.zombie_moan_sounds = []
            for snd in ZOMBIE_MOAN_SOUNDS:
                s = pg.mixer.Sound(snd)
                s.set_volume(0.1)
                self.zombie_moan_sounds.append(s)
                self.all_sounds.append(s)

            self.zombie_death_sounds = []
            for snd in ZOMBIE_DEATH_SOUNDS:
                s = pg.mixer.Sound(snd)
                self.zombie_death_sounds.append(s)
                self.all_sounds.append(s)

    # -------------------------------------------
    #  these two methods have been disabled
    # -------------------------------------------
    def show_story_screen(self, unknown_arg):
        pass

    def save_progress(self):
        pass

    def load_level(self, stats=None):
        # level_name = 'tutorial.tmx' <-- previously this was the default val.
        self.all_sprites = pg.sprite.LayeredUpdates()  # Group()
        self.walls = pg.sprite.Group()
        self.towers = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        self.bullets = pg.sprite.Group()
        self.items = pg.sprite.Group()
        self.landmines = pg.sprite.Group()
        self.explosions = pg.sprite.Group()
        # Grab our game layout file (map)
        # TODO support multi-level
        #  self.current_lvl = level_name
        self.current_lvl = 'level1.tmx'

        self.player_img = cload_img(
            LEVELS[self.current_lvl]['plyr']
        ).convert_alpha()  # Surface
        self.objective = LEVELS[self.current_lvl]['objective']
        self.story = LEVELS[self.current_lvl]['story']

        web = 0

        self.map = tilemap.CustomTiledMap('level1.tmj', 'cartridge/')  # TODO fix to use pyv.vars.data instead

        self.map_img = self.map.make_map()
        self.map_rect = self.map_img.get_rect()
        self.texts = pg.sprite.Group()  # Created sprite group of texts, and apply the camera on them
        # Amount of comms needed to beat level
        self.comms_req = 0

        # load everything on map
        for tile_object in self.map.objects:
            obj_center = pg.math.Vector2(tile_object.x + tile_object.width / 2, tile_object.y + tile_object.height / 2)
            if tile_object.name == 'player':
                if stats:
                    self.player = Player(self, obj_center.x, obj_center.y, stats)
                else:
                    self.player = Player(self, obj_center.x, obj_center.y)
            elif tile_object.name == 'wall':
                Obstacle(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            elif tile_object.name == 'zombie':
                Mob(self, obj_center.x, obj_center.y)  # pass
            elif tile_object.name == 'runner':
                Runner(self, obj_center.x, obj_center.y)
            elif tile_object.name == 'tower':
                Tower(self, tile_object.x, tile_object.y, tile_object.width, tile_object.height)
            elif tile_object.name in ITEM_IMAGES.keys():
                if tile_object.name == 'bonus':
                    ratio = (32, 32)
                    if tile_object.type == 'x':
                        BonusItem(self, obj_center, 'x', ratio)
                    else:
                        BonusItem(self, obj_center, 'y', ratio)
                    continue
                elif tile_object.name == 'health':
                    ratio = (32, 32)
                elif tile_object.name == 'comms':
                    ratio = (48, 48)
                    self.comms_req += 1
                elif tile_object.name in GUN_IMAGES:
                    ratio = (48, 48)
                elif tile_object.name == 'pistol_ammo' or tile_object.name == 'shotgun_ammo' \
                        or tile_object.name == 'uzi_ammo':
                    ratio = (32, 32)
                elif tile_object.name == 'landmine':
                    ratio = (32, 32)
                Item(self, obj_center, tile_object.name, ratio)
            elif tile_object.type == 'text':  # putting text in object name
                IngameText(self, tile_object.x, tile_object.y, tile_object.name)

        self.camera = tilemap.Camera(self.map.width, self.map.height)  # , WINDOW_WIDTH, WINDOW_HEIGHT)
        # self.draw_debug = False
        self.paused = False

        if not NO_SOUND:
            pg.mixer.music.stop()

        self.show_story_screen(LEVELS[self.current_lvl]['story'])

        if not NO_SOUND:
            # if self.current_lvl == 'tutorial.tmx':
            self.current_music = LEVELS[self.current_lvl]['music']
            self.effects_sounds['level_start'].play()
            #    self.current_music = BG_MUSIC
            # elif self.current_lvl == 'level1.tmx':
            #    self.current_music = LVL1_MUSIC
            pg.mixer.music.load(self.current_music)
            pg.mixer.music.play(loops=-1)

    def update(self):
        # update portion of the game loop
        self.all_sprites.update()
        self.camera.update(self.player)

        # Mobs hit player
        f_collide = tilemap.collide_hit_rect
        hits = pg.sprite.spritecollide(self.player, self.mobs, False, f_collide)
        if not self.player.is_damaged and hits:
            self.player.got_hit()
            self.player.pos += pg.math.Vector2(MOB_KNOCKBACK, 0).rotate(-hits[0].rot)
            for hit in hits:
                self.player.health -= MOB_DAMAGE
                if not NO_SOUND:
                    if random.random() <= 0.9:
                        random.choice(self.player_hit_sounds).play()
                hit.vel = pg.math.Vector2(0, 0)

        # Player touches explosion
        hits = pg.sprite.spritecollide(self.player, self.explosions, False, f_collide)
        if not self.player.is_damaged and hits:
            self.player.got_hit()
            self.player.pos -= pg.math.Vector2(LANDMINE_KNOCKBACK, 0).rotate(self.player.rot)
            for hit in hits:
                self.player.health -= LANDMINE_DAMAGE
                if not NO_SOUND:
                    if random.random() < 0.9:
                        random.choice(self.player_hit_sounds).play()

                hit.vel = pg.math.Vector2(0, 0)
        if self.player.health <= 0:
            self.save_progress()
            self.playing = False
            self.game_over = True

        # Bullets hit mobs
        hits = pg.sprite.groupcollide(self.mobs, self.bullets, False, True)
        for mob in hits:
            # Multiply dmg by amount of bullets that hit the mob using len(hits[hit]) keep in mind hits is a dict
            # hit.health -= WEAPONS[self.player.curr_weapon]['damage'] * len(hits[hit])  # TODO: ensure correctness
            # Purpose for doing it this way to ensure that the bullet damage doesn't depend on which gun the player is
            # holding
            for bullet in hits[mob]:
                mob.health -= bullet.damage
            mob.vel = pg.math.Vector2(0, 0)
        # Mobs touch mine
        hits = pg.sprite.groupcollide(self.mobs, self.landmines, False, True)
        if hits:
            if not NO_SOUND:
                self.effects_sounds['explosion'].play()

        for mob in hits:
            Explosion(self, mob.pos)
        # Mobs touch explosion
        hits = pg.sprite.groupcollide(self.mobs, self.explosions, False, False)
        for mob in hits:
            mob.health -= LANDMINE_DAMAGE + self.player.stats['dmg_bonus']
            mob.vel = pg.math.Vector2(0, 0)
        # Player touches item
        hits = pg.sprite.spritecollide(self.player, self.items, False)
        for hit in hits:  # TODO: Put sounds in an object instead of a dictionary
            if hit.type == 'health' and self.player.health < PLAYER_MAX_HEALTH:
                if not NO_SOUND:
                    self.effects_sounds['health_up'].play()  # TODO: Find different sound
                self.player.health = min(self.player.health + HEALTH_PICKUP_AMT, PLAYER_MAX_HEALTH)
                hit.kill()
            elif hit.type == 'shotgun':
                hit.kill()
                if not NO_SOUND:
                    self.effects_sounds['gun_pickup'].play()
                self.player.weapons.append('shotgun')
                self.player.weapon_selection += 1
                self.player.curr_weapon = 'shotgun'
                self.player.ammo['shotgun_ammo'] += SHOTGUN_AMMO_PICKUP_AMT + self.player.stats['ammo_bonus']
            elif hit.type == 'uzi':
                hit.kill()
                if not NO_SOUND:
                    self.effects_sounds['gun_pickup'].play()
                self.player.weapons.append('uzi')
                self.player.weapon_selection += 1
                self.player.curr_weapon = 'uzi'
                self.player.ammo['uzi_ammo'] += UZI_AMMO_PICKUP_AMT + self.player.stats['ammo_bonus']
            elif hit.type == 'pistol_ammo':
                if hit.visible:
                    hit.make_invisible()
                    self.player.ammo['pistol_ammo'] += PISTOL_AMMO_PICKUP_AMT + self.player.stats['ammo_bonus']
                    if not NO_SOUND:
                        self.effects_sounds['ammo_pickup'].play()
            elif hit.type == 'shotgun_ammo':
                hit.kill()
                self.player.ammo['shotgun_ammo'] += SHOTGUN_AMMO_PICKUP_AMT + self.player.stats['ammo_bonus']
                if not NO_SOUND:
                    self.effects_sounds['ammo_pickup'].play()
            elif hit.type == 'uzi_ammo':
                hit.kill()
                self.player.ammo['uzi_ammo'] += UZI_AMMO_PICKUP_AMT + self.player.stats['ammo_bonus']
                if not NO_SOUND:
                    self.effects_sounds['ammo_pickup'].play()
            elif hit.type == 'landmine':
                hit.kill()
                self.player.ammo['landmines'] += 1  # Not getting any bonus stats for mines ;)
                if not NO_SOUND:
                    self.effects_sounds['ammo_pickup'].play()
            elif hit.type == 'comms':
                hit.kill()
                self.player.comms += 1
                if not NO_SOUND:
                    self.effects_sounds['item_pickup'].play()
                if self.current_lvl == 'tutorial.tmx':
                    IngameText(self, 2000, 200, "Pistol ammo regenerates...")

        # Bullet touches BonusItem
        hits = pg.sprite.groupcollide(self.items, self.bullets, False, False)
        for hit in hits:
            if isinstance(hit, BonusItem):
                hit.kill()
                hit.activate(self.player)
                self.player.stats['bonuses'] += 1
        # Check if we beat brought comms to tower
        if self.objective == 'return_comms':
            hits = pg.sprite.spritecollide(self.player, self.towers, False, False)
            for hit in hits:
                if self.player.comms >= self.comms_req:
                    self.level_complete = True
        elif self.objective == 'kill_all_zombies':
            if len(self.mobs) <= 0:
                self.level_complete = True

        if self.level_complete:  # ------ GO TO NEXT LEVEL ------
            print('----------------------------')
            print('  LEVEL COMPLETED')
            print('----------------------------')

            # self.player.kill()
            if not NO_SOUND:
                pg.mixer.music.stop()

            # TODO multi-level support
            # self.level_complete = False
            # if self.current_lvl == 'tutorial.tmx':
            #     self.load_level('level1.tmx', self.player.stats)
            # elif self.current_lvl == 'level1.tmx':
            #     self.playing = False
            #     self.current_lvl = 'ending'

    def draw_grid(self):
        for x in range(0, WINDOW_WIDTH, TILESIZE):
            pg.draw.line(self.screen, WHITE, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, TILESIZE):
            pg.draw.line(self.screen, WHITE, (0, y), (WINDOW_WIDTH, y))

    def draw_health(self, x, y, health_pct):
        surface = self.screen
        if health_pct < 0:
            health_pct = 0
        fill = health_pct * PLAYER_HEALTH_BAR_WIDTH
        outline_rect = pg.Rect(x, y, PLAYER_HEALTH_BAR_WIDTH, PLAYER_HEALTH_BAR_HEIGHT)
        fill_rect = pg.Rect(x, y, fill, PLAYER_HEALTH_BAR_HEIGHT)
        if health_pct > 0.65:
            col = GREEN
        elif health_pct > 0.45:
            col = YELLOW
        else:
            col = RED
        pg.draw.rect(surface, col, fill_rect)
        pg.draw.rect(surface, WHITE, outline_rect, 2)

    def render_fog(self):
        # draw the light mask (gradient) onto the fog image
        self.fog.fill(NIGHT_COLOR)
        self.light_rect.center = self.camera.apply_sprite(self.player).center
        self.fog.blit(self.light_mask, self.light_rect)  # mask -> light_rect
        # BLEND_MULT blends somehow by multiplying adjacent pixels color's (int values)
        self.screen.blit(self.fog, (0, 0), special_flags=pg.BLEND_MULT)

    def draw_scene(self):
        # pg.display.set_caption("{:.2f}".format(self.clock.get_fps()))
        # self.screen.fill(BGCOLOR)
        self.screen.blit(self.map_img, self.camera.apply_rect(self.map_rect))

        # self.draw_grid()
        for sprite in self.all_sprites:
            # if isinstance(sprite, Mob):  # I put this in the Mob.update instead
            #    sprite.draw_health()
            self.screen.blit(sprite.image, self.camera.apply_sprite(sprite))
            if self.draw_debug:
                if hasattr(sprite, 'hit_rect'):
                    rect_drawn = self.camera.apply_rect(sprite.hit_rect)
                    adhoc_r = rect_drawn
                elif hasattr(sprite, 'pos'):
                    adhoc_r = (
                        self.camera.camera[0] + sprite.pos[0] - (sprite.rect[2] / 2),
                        self.camera.camera[1] + sprite.pos[1] - (sprite.rect[3] / 2),
                        sprite.rect[2],
                        sprite.rect[3]
                    )
                else:
                    adhoc_r = None
                if adhoc_r:
                    pg.draw.rect(self.screen, RED, adhoc_r, 1)

        if self.draw_debug:
            for wall in self.walls:
                pg.draw.rect(self.screen, GREEN, self.camera.apply_rect(wall.rect), 1)
        # for wall in self.walls:
        #    pg.draw.rect(self.screen, WHITE, wall.rect, 2)
        # Draw player's rect. Good for debugging.   Thickness of 2
        # pg.draw.rect(self.screen, WHITE, self.player.hit_rect, 2)

        if not NO_FOG:
            self.render_fog()
        # if self.is_night:
        #     self.render_fog()
        self.draw_health(5, 5, self.player.health / PLAYER_MAX_HEALTH)

        # Display current weapon
        self.screen.blit(self.gun_images[self.player.curr_weapon], (10, 25))
        # Display current ammo
        curr_weapon_ammo_amt = self.player.get_ammo(self.player.curr_weapon)
        self.draw_text(' - {}'.format(curr_weapon_ammo_amt), self.hud_font, 30, BLACK, 45, 30, align='nw')

        # display zombies left
        self.draw_text(
            'ZOMBIES - {}'.format(len(self.mobs)), self.hud_font, 30, WHITE, WINDOW_WIDTH - 10, 10, align='ne'
        )

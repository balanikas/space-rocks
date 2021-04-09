import pygame as pg


class Player(pg.sprite.Sprite):

    def __init__(self, pos):
        super(Player, self).__init__()
        self.image = pg.Surface((120, 120), pg.SRCALPHA)
        pg.draw.polygon(self.image, (0, 100, 240), [(60, 0), (120, 120), (0, 120)])
        self.rect = self.image.get_rect(center=pos)
        self.mask = pg.mask.from_surface(self.image)


class Enemy(pg.sprite.Sprite):

    def __init__(self, pos):
        super(Enemy, self).__init__()
        self.image = pg.Surface((120, 120), pg.SRCALPHA)
        pg.draw.circle(self.image, (240, 100, 0), (60, 60), 60)
        self.rect = self.image.get_rect(center=pos)
        self.mask = pg.mask.from_surface(self.image)


class Game:
    def __init__(self):
        self.screen = pg.display.set_mode((640, 480))
        self.player = Player((20, 20))
        self.enemies = pg.sprite.Group(Enemy((320, 240)))
        self.all_sprites = pg.sprite.Group(self.player, self.enemies)
        self.done = False
        self.clock = pg.time.Clock()

    def run(self):
        while not self.done:
            self.event_loop()
            self.update()
            self.draw()
            pg.display.flip()
            self.clock.tick(60)

    def event_loop(self):
        for event in pg.event.get():
            if event.type == pg.QUIT:
                self.done = True
            elif event.type == pg.MOUSEMOTION:
                self.player.rect.center = event.pos

    def update(self):
        # Check if the player collides with an enemy sprite. The
        # `pygame.sprite.collide_mask` callback uses the `mask`
        # attributes of the sprites for the collision detection.
        if pg.sprite.spritecollide(self.player, self.enemies, False, pg.sprite.collide_mask):
            pg.display.set_caption('collision')
        else:
            pg.display.set_caption('no collision')

    def draw(self):
        self.screen.fill((30, 30, 30))
        self.all_sprites.draw(self.screen)


#
# if __name__ == '__main__':
#     pg.init()
#     game = Game()
#     game.run()
#     pg.quit()


from game import SpaceRocks

if __name__ == "__main__":
    space_rocks = SpaceRocks()
    space_rocks.main_loop()

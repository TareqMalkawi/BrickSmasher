import math
import os
import random
import pygame

if not pygame.font:
    print("font not initialized")
if not pygame.mixer:
    print("audios not initialized")

# create platform independent file path.
main_dir = os.path.split(os.path.abspath(__file__))[0]
gamedata_dir = os.path.join(main_dir, "Game Data")

# used to help spawn the blocks by names
block_names = ["Crimson", "DarkBlue", "LightBlue", "LimeGreen", "Orange",
               "Pink", "Purple", "Turquoise", "Yellow"]


def load_sprite(name, color_key=None, scale=1.0):
    sprite_fullname = os.path.join(gamedata_dir, name)
    sprite = pygame.image.load(sprite_fullname)
    sprite = sprite.convert()

    sprite_size = sprite.get_size()
    sprite_size = (sprite_size[0] * scale, sprite_size[1] * scale)
    sprite = pygame.transform.scale(sprite, sprite_size)

    if color_key is not None:
        if color_key == -1:
            color_key = sprite.get_at((0, 0))
        sprite.set_colorkey(color_key, pygame.RLEACCEL)

    return sprite, sprite.get_rect()


def load_sound(name):
    class NoneSound:
        def play(self):
            pass

    if not pygame.mixer or not pygame.mixer.get_init():
        return NoneSound()

    audio_fullname = os.path.join(gamedata_dir, name)
    sound = pygame.mixer.Sound(audio_fullname)

    return sound


class BasePlatform(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_sprite("Sprites/Base.png", -1, 0.38)
        screen = pygame.display.get_surface()
        self.area = screen.get_rect()
        self.ball = Ball()

    def get_ball(self):
        return self.ball

    def remove_ball(self):
        self.ball.remove_ball()

    def move_base(self):
        mouse_pos = pygame.mouse.get_pos()
        self.rect.topleft = (mouse_pos[0], 640)
        if not self.area.contains(self.rect):
            if self.rect.right > self.area.right:
                self.rect.topleft = (910, 640)

        self.ball.setbaseblatform_rectpos(self.rect.topleft)

    def update(self):
        self.move_base()

    def check_collision(self, other):
        return self.rect.colliderect(other)


class Block(pygame.sprite.Sprite):
    def __init__(self, block_name):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_sprite("Sprites/"
                                            + block_name + ".png", -1, 0.425)

    def change_pos(self, x, y):
        self.rect.update(x, y, self.image.get_size()[0], self.image.get_size()[1])

    def remove_block(self):
        self.kill()

    def check_ballcollision(self, other):
        return self.rect.colliderect(other)


class Ball:
    def __init__(self):
        self.screen = pygame.display.get_surface()
        self.area = self.screen.get_rect()
        self.outside_area = False
        self.ball_rect = None
        self.initial_move = 4
        self.horizontal_move = 0
        self.vertical_move = -4
        self.collided_once = False
        self.collided = False
        self.get_rectpos = False
        self.x = 520
        self.y = 380
        self.dist = 0
        self.baseblatform_rectpos = (0, 0)
        self.balllangtituade_direction = ""

    def setbaseblatform_rectpos(self, baseblatform_rectpos):
        self.baseblatform_rectpos = baseblatform_rectpos

    def setball_movement(self, horizontal_move=0, vertical_move=-4):
        self.horizontal_move = horizontal_move
        self.vertical_move = vertical_move

    def setball_pos(self, x, y):
        self.x = x
        self.y = y

    def draw_ball(self):
        self.ball_rect = pygame.draw.circle(self.screen, (250, 250, 250), [self.x, self.y], 14, 0)
        if not self.get_rectpos:
            self.x = self.ball_rect.x
            self.y = self.ball_rect.y
            self.get_rectpos = True
            self.dist = 0
            self.balllangtituade_direction = "BOTTOM"

    def get_ballrect(self):
        return self.ball_rect

    def remove_ball(self):
        self.x = 0
        self.y = 0

    def update(self):
        if not self.collided_once:
            if not self.get_rectpos:
                pass

            self.y += self.initial_move
            self.ball_rect[1] = self.y
        self.dist = math.fabs(self.baseblatform_rectpos[0] - self.ball_rect.x)

        if not self.area.contains(self.ball_rect):
            if self.ball_rect.top > self.area.bottom:
                pygame.time.delay(500)
                self.x = 520
                self.y = 380
                self.initial_move = 3
                self.horizontal_move = 0
                self.vertical_move = 3

        if self.collided:
            if not self.area.contains(self.ball_rect):
                if self.ball_rect.right > self.area.right and self.balllangtituade_direction == "TOP":
                    self.balllangtituade_direction = "BOTTOM"
                    self.horizontal_move = -4
                    self.vertical_move = 4
                elif self.ball_rect.right > self.area.right and self.balllangtituade_direction == "BOTTOM":
                    self.horizontal_move = -4
                    self.vertical_move = -4
                elif self.ball_rect.left < self.area.left and self.balllangtituade_direction == "TOP":
                    self.balllangtituade_direction = "BOTTOM"
                    self.horizontal_move = 4
                    self.vertical_move = 4
                elif self.ball_rect.left < self.area.left and self.balllangtituade_direction == "BOTTOM":
                    self.horizontal_move = 4
                    self.vertical_move = -4
                elif self.ball_rect.top < self.area.top:
                    self.balllangtituade_direction = "TOP"
                    if self.dist < 25 or self.dist > 25:
                        if self.ball_rect.x < self.baseblatform_rectpos[0]:
                            self.horizontal_move = -3
                            self.vertical_move = 4
                        else:
                            self.horizontal_move = 2
                            self.vertical_move = 4

                elif self.ball_rect.top > self.area.top:
                    self.horizontal_move = -2
                    self.vertical_move = 4

            self.y += self.vertical_move
            self.x += self.horizontal_move

    def reflect_ball(self):
        self.collided = False
        if self.baseblatform_rectpos[0] > self.ball_rect.x and self.dist >= 25:
            self.horizontal_move = -3
            self.vertical_move = -4
        elif self.baseblatform_rectpos[0] < self.ball_rect.x and self.dist >= 25:
            self.horizontal_move = 3
            self.vertical_move = -4
        elif self.dist < 25:
            self.horizontal_move = 0
            self.vertical_move = -4

        self.balllangtituade_direction = "BOTTOM"

        if not self.collided:
            self.collided_once = True
            self.collided = True


def create_block(block_name, x, y):
    block = Block(block_name)
    block.change_pos(x, y)
    return block


def createallblocks():
    block = 0
    xpos = 0
    blocks = []
    blockssprites = 0
    for i in range(0, 61):
        r = random.randint(0, 8)
        if i < 15:
            if i == 0:
                xpos = 32
            else:
                xpos += 66
            block = create_block(block_names[r], xpos, 22)
        elif 15 <= i < 30:
            if i == 15:
                xpos = 32
            else:
                xpos += 66
            block = create_block(block_names[r], xpos, 92)
        elif 30 <= i < 45:
            if i == 30:
                xpos = 32
            else:
                xpos += 66
            block = create_block(block_names[r], xpos, 162)

        elif 45 <= i < 60:
            if i == 45:
                xpos = 32
            else:
                xpos += 66
            block = create_block(block_names[r], xpos, 232)

        blocks.append(block)

    if len(blocks) == 61:
        blockssprites = pygame.sprite.RenderPlain(blocks[0], blocks[1], blocks[2], blocks[3],
                                                  blocks[4], blocks[5], blocks[6], blocks[7],
                                                  blocks[8], blocks[9], blocks[10],
                                                  blocks[11], blocks[12], blocks[13], blocks[14],
                                                  blocks[15], blocks[16], blocks[17], blocks[18],
                                                  blocks[19], blocks[20], blocks[21], blocks[22],
                                                  blocks[23], blocks[24], blocks[25], blocks[26],
                                                  blocks[27], blocks[28], blocks[29], blocks[30],
                                                  blocks[31], blocks[32],
                                                  blocks[33], blocks[34], blocks[35], blocks[36],
                                                  blocks[37], blocks[38], blocks[39], blocks[40],
                                                  blocks[41], blocks[42], blocks[43], blocks[44],
                                                  blocks[45], blocks[46], blocks[47], blocks[48],
                                                  blocks[49], blocks[50], blocks[51], blocks[52],
                                                  blocks[53], blocks[54], blocks[55], blocks[56],
                                                  blocks[57], blocks[58], blocks[59])
    return blocks, blockssprites


def main():
    pygame.init()

    screen = pygame.display.set_mode((1040, 700), pygame.SCALED)
    pygame.display.set_caption("Brick Smasher")  # Smash Some Bricks
    pygame.mouse.set_visible(False)

    main_background = pygame.Surface(screen.get_size()).convert()
    main_background.fill((110, 110, 110))

    screen.blit(main_background, (0, 0))
    pygame.display.flip()

    # game sprites
    base_platform = BasePlatform()
    ball = base_platform.get_ball()

    # game sounds
    hit_sound = load_sound("Sounds/hit.wav")
    ambient_sound = load_sound("Sounds/ambient.wav")
    impact_sound = load_sound("Sounds/impact.wav")
    ambient_sound.play(-1)
    hit_sound.set_volume(0.9)
    impact_sound.set_volume(0.7)
    ambient_sound.set_volume(0.1)

    all_blocks, sprites = createallblocks()
    base_platformsprite = pygame.sprite.RenderPlain(base_platform)

    clock = pygame.time.Clock()
    main_loop = True
    hit_block = 0

    while main_loop:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                main_loop = False

            elif event.type == pygame.KEYDOWN:
                if event.type == pygame.K_ESCAPE:
                    main_loop = False
                elif event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    hit_block = 0
                    base_platform.remove_ball()

                    textcover = pygame.Surface((1040, 300)).convert()
                    textcover.fill((110, 110, 110))
                    main_background.blit(textcover, (0, 200))
                    pygame.display.flip()

                    pygame.time.delay(1000)
                    all_blocks, sprites = createallblocks()
                    ball.setball_pos(520, 380)
                    ball.setball_movement(0, 4)

        base_platformsprite.update()
        sprites.update()
        screen.blit(main_background, (0, 0))
        base_platformsprite.draw(screen)
        sprites.draw(screen)
        ball.draw_ball()

        if base_platform.check_collision(ball.get_ballrect()):
            ball.reflect_ball()
            hit_sound.play()
        ball.update()

        for block in range(0, len(all_blocks)):
            if all_blocks[block].alive() and all_blocks[block].check_ballcollision(ball.ball_rect):
                impact_sound.play()
                all_blocks[block].remove_block()
                hit_block += 1

        if hit_block == (len(all_blocks) - 1):
            hit_block = 0
            ball.setball_movement(0, 0)

            winfont = pygame.font.Font(None, 64)
            wintext = winfont.render("You Win !", True, (250, 0, 0))
            wintextpos = wintext.get_rect(centerx=main_background.get_width() / 2, y=250)

            restartfont = pygame.font.Font(None, 32)
            restarttext = restartfont.render("Press (Space) to restart the game", True, (0, 250, 0))
            restarttextpos = restarttext.get_rect(centerx=main_background.get_width() / 2, y=300)

            main_background.blit(wintext, wintextpos)
            main_background.blit(restarttext, restarttextpos)

        pygame.display.flip()
        pygame.display.update()

    pygame.quit()


if __name__ == "__main__":
    main()

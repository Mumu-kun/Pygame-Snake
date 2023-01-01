import pygame
from random import randint
from sys import exit as sys_exit

pygame.init()
main_clock = pygame.time.Clock()
display_screen = pygame.display.set_mode()
grid_size = 15
display_height = display_screen.get_height() // grid_size
display_width = display_screen.get_width() // grid_size

text_font = pygame.font.Font("freesansbold.ttf", 20)

## Global Variables
score = 0
game_speed = 10

## Events
INIT_GAME_EVENT = pygame.USEREVENT + 1

game_tick_event = pygame.event.Event(pygame.USEREVENT + 2)
pygame.time.set_timer(game_tick_event, 1000 // game_speed)


point_anim_event = pygame.event.Event(pygame.USEREVENT + 3)
pygame.time.set_timer(point_anim_event, 200)

## Classes
class SnakeSegment(pygame.sprite.Sprite):
    def __init__(
        self, order: int, pos: tuple = (display_width // 2, display_height // 2)
    ):
        super().__init__()
        self.order = order
        self.pos = pos

        self.image = pygame.surface.Surface((grid_size, grid_size))
        self.image.fill("White")
        self.rect = self.image.get_rect(
            topleft=(pos[0] * grid_size, pos[1] * grid_size)
        )


class Snake(pygame.sprite.Group):
    def __init__(self, *sprites) -> None:
        super().__init__(*sprites)
        self.direction = (1, 0)
        self.size = 1
        self.head = sprites[0]
        self.tail = sprites[0]

    def addHead(self, segment):
        self.head = segment
        self.add(self.head)
        self.size += 1

    def addTail(self):
        temp_tail = SnakeSegment(self.size, self.tail.rect.topleft)
        self.tail = temp_tail
        self.add(self.tail)
        self.size += 1

    def destroyTail(self):
        self.tail.kill()
        # self.tail = None
        self.size -= 1

    def keyInput(self, key):
        if key == pygame.K_UP and self.direction != (0, 1):
            self.direction = (0, -1)
        if key == pygame.K_DOWN and self.direction != (0, -1):
            self.direction = (0, 1)
        if key == pygame.K_LEFT and self.direction != (1, 0):
            self.direction = (-1, 0)
        if key == pygame.K_RIGHT and self.direction != (-1, 0):
            self.direction = (1, 0)

    def moveSnake(self):
        for segment in self.sprites():
            if segment.order >= (self.size - 1):
                self.tail = segment
            segment.order += 1

        head_new_position = (
            self.head.pos[0] + self.direction[0],
            self.head.pos[1] + self.direction[1],
        )
        self.addHead(SnakeSegment(0, head_new_position))
        self.destroyTail()

    def selfCollideCheck(self):
        body_list = [body_segment.rect for body_segment in self.sprites()]
        body_list.remove(self.head.rect)
        if self.head.rect.collidelistall(body_list):
            pygame.event.post(pygame.event.Event(INIT_GAME_EVENT))

    def outOfScreenCheck(self):
        if (
            self.head.pos[0] < 0
            or self.head.pos[0] > display_width - 1
            or self.head.pos[1] < 0
            or self.head.pos[1] > display_height - 1
        ):
            pygame.event.post(pygame.event.Event(INIT_GAME_EVENT))

    def update(self):

        self.moveSnake()
        self.outOfScreenCheck()
        self.selfCollideCheck()
        # print([segment.order for segment in self.sprites()])
        # self.tail.image.fill((randint(0, 255), randint(0, 255), randint(0, 255)))
        # display_screen.blit(self.tail.image, self.tail.rect)


class Point(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        self.x = randint(0, display_width - 1)
        self.y = randint(0, display_height - 1)
        self.size = grid_size * 0.6
        self.image = pygame.surface.Surface((self.size, self.size))
        self.image.fill("White")

        self.rect = pygame.rect.Rect(
            self.x * grid_size, self.y * grid_size, grid_size, grid_size
        )

    def drawPoint(self, screen: pygame.surface.Surface):
        screen.blit(
            self.image,
            (self.rect.centerx - self.size / 2, self.rect.centery - self.size / 2),
        )

    def animation(self):
        self.size = grid_size * 0.8 if self.size == grid_size * 0.6 else grid_size * 0.6
        self.image = pygame.surface.Surface((self.size, self.size))
        self.image.fill("White")

    def update(self):
        self.animation()


## Helper Functions
def init_game():
    global snake, point, score, game_speed
    score = 0
    game_speed = 5
    snake = Snake(SnakeSegment(0))
    point = pygame.sprite.GroupSingle(Point())
    if_point_grabbed()


def render_fps():
    fps_surface = text_font.render(f"{main_clock.get_fps()}", False, "White")
    display_screen.blit(fps_surface, (5, 5))


def render_score(score: int):
    score_surface = text_font.render(f"Score : {score}", False, "White")
    score_rect = score_surface.get_rect(topright=(display_screen.get_width() - 5, 5))
    display_screen.blit(score_surface, score_rect)


def if_point_grabbed():
    if pygame.sprite.groupcollide(snake, point, False, True):
        point.add(Point())
        return True
    return False


snake = Snake(SnakeSegment(0))
point = pygame.sprite.GroupSingle(Point())
if_point_grabbed()

while True:
    for event in pygame.event.get():
        if event.type == INIT_GAME_EVENT:
            init_game()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys_exit()
        if event == point_anim_event:
            point.update()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                pygame.time.set_timer(game_tick_event, 1000 // (game_speed * 5))
            if event.key == pygame.K_RETURN:
                pygame.event.post(pygame.event.Event(INIT_GAME_EVENT))
            if event.key == pygame.K_ESCAPE:
                pygame.event.post(pygame.event.Event(pygame.QUIT))
            else:
                snake.keyInput(event.key)
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_SPACE:
                pygame.time.set_timer(game_tick_event, 1000 // game_speed)
        if event == game_tick_event:
            snake.update()

    display_screen.fill("Black")

    snake.draw(display_screen)
    # snake.update()

    point.sprite.drawPoint(display_screen)
    # point.update()

    if if_point_grabbed():
        snake.addTail()
        score += 1
        game_speed += 2

    render_score(score)
    # render_fps()

    pygame.display.update()
    main_clock.tick(60)

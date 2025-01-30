import pygame
import random
import copy
import sqlite3

conn = sqlite3.connect('tetris.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY,
    best_score INTEGER,
    total_money INTEGER
)
''')
cursor.execute('''
INSERT INTO records (best_score, total_money) VALUES (0, 0)
ON CONFLICT(id) DO NOTHING
''')
conn.commit()


def update_record(score, money):
    cursor.execute('SELECT best_score, total_money FROM records WHERE id=1')
    best_score, total_money = cursor.fetchone()
    if score > best_score:
        cursor.execute('UPDATE records SET best_score = ? WHERE id=1', (score,))
    cursor.execute('UPDATE records SET total_money = total_money + ? WHERE id=1', (money,))
    conn.commit()


def get_record():
    cursor.execute('SELECT best_score, total_money FROM records WHERE id=1')
    return cursor.fetchone()


pygame.init()
columns = 11
strings = 21
screen_x = 250
screen_y = 500
COLORS = [
    (255, 99, 71),  # Tomato
    (255, 140, 0),  # Dark Orange
    (255, 215, 0),  # Gold
    (34, 139, 34),  # Forest Green
    (30, 144, 255),  # Dodger Blue
    (75, 0, 130),  # Indigo
    (238, 130, 238),  # Violet
    (255, 20, 147),  # Deep Pink
    (255, 182, 193),  # Light Pink
    (173, 216, 230),  # Light Blue
    (144, 238, 144),  # Light Green
    (255, 105, 180),  # Hot Pink
    (135, 206, 250),  # Light Sky Blue
    (255, 160, 122),  # Light Salmon
    (240, 128, 128),  # Light Coral
]
screen = pygame.display.set_mode((screen_x, screen_y))
pygame.display.set_caption("Tetris CODE")
clock = pygame.time.Clock()
cell_x = screen_x / (columns - 1)
cell_y = screen_y / (strings - 1)
fps = 60
grid = []
score = 0
font = pygame.font.Font(None, 36)
COLOR = random.choice(COLORS)
LEVEL = 1
for i in range(columns):
    grid.append([])
    for j in range(strings):
        grid[i].append([1, pygame.Rect(i * cell_x, j * cell_y, cell_x, cell_y), pygame.Color("Gray")])
details = [
    [[-2, 0], [-1, 0], [0, 0], [1, 0]],
    [[-1, 1], [-1, 0], [0, 0], [1, 0]],
    [[1, 1], [-1, 0], [0, 0], [1, 0]],
    [[-1, 1], [0, 1], [0, 0], [-1, 0]],
    [[1, 0], [1, 1], [0, 0], [-1, 0]],
    [[0, 1], [-1, 0], [0, 0], [1, 0]],
    [[-1, 1], [0, 1], [0, 0], [1, 0]],
]
det = [[] for _ in range(len(details))]
for i in range(len(details)):
    for j in range(4):
        det[i].append(
            pygame.Rect(details[i][j][0] * cell_x + cell_x * (columns // 2), details[i][j][1] * cell_y, cell_x, cell_y))
det_choice = copy.deepcopy(random.choice(det))
count = 0
game = True
rotate = False


def game_over():
    play_soundtrack("game-over.mp3")
    money_earned = score // 200 * 10
    update_record(score, money_earned)
    screen.fill(pygame.Color(222, 248, 116))
    game_over_text = font.render("Game Over", True, (255, 0, 0))
    score_text = font.render(f"Final Score: {score}", True, (255, 255, 255))
    money = font.render(f"Get money +{money_earned}", True, (255, 255, 255))
    best_score, total_money = get_record()
    All_money = font.render(f"ALL money: {total_money + money_earned}", True, (255, 255, 255))
    screen.blit(game_over_text, (screen_x // 2 - game_over_text.get_width() // 2,
                                 screen_y // 2 - game_over_text.get_height()))
    screen.blit(score_text, (screen_x // 2 - score_text.get_width() // 2,
                             screen_y // 2 + game_over_text.get_height()))
    screen.blit(best_score_text, (screen_x // 2 - best_score_text.get_width() // 2,
                                  screen_y // 2 + game_over_text.get_height() + 20))
    screen.blit(All_money, (screen_x // 2 - All_money.get_width() // 2,
                            screen_y // 2 + game_over_text.get_height() + 40))
    screen.blit(money, (screen_x // 2 - money.get_width() // 2,
                        screen_y // 2 + game_over_text.get_height() + 60))
    pygame.display.flip()
    pygame.time.wait(3000)
    pygame.quit()
    exit()


def play_soundtrack(sound_file):
    pygame.mixer.music.load(sound_file)
    pygame.mixer.music.play(-1)


play_soundtrack("sound_track.mp3")
while game:
    delta_x = 0
    delta_y = 1
    screen.fill(pygame.Color(222, 248, 116))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                delta_x = -1
            elif event.key == pygame.K_RIGHT:
                delta_x = 1
            elif event.key == pygame.K_UP:
                rotate = True

    key = pygame.key.get_pressed()
    if key[pygame.K_DOWN]:
        count = 31 * fps
    for i in range(columns):
        for j in range(strings):
            pygame.draw.rect(screen, grid[i][j][2], grid[i][j][1])
    for i in range(4):
        if (det_choice[i].x + delta_x * cell_x < 0) or (det_choice[i].x + delta_x * cell_x >= screen_x):
            delta_x = 0
        if ((det_choice[i].y + cell_y >= screen_y) or (
                grid[int(det_choice[i].x // cell_x)][int(det_choice[i].y // cell_y) + 1][0] == 0)):
            delta_y = 0
            for i in range(4):
                x = int(det_choice[i].x // cell_x)
                y = int(det_choice[i].y // cell_y)
                grid[x][y][0] = 0
                grid[x][y][2] = pygame.Color(45, 109, 234)
                COLOR = random.choice(COLORS)
            if any(grid[i][0][0] == 0 for i in range(columns)):
                game_over()
            det_choice = copy.deepcopy(random.choice(det))
    for i in range(4):
        det_choice[i].x += delta_x * cell_x
    count += fps
    if count > 30 * fps:
        for i in range(4):
            det_choice[i].y += delta_y * cell_y
        count = 0
    C = det_choice[2]
    if rotate:
        for i in range(4):
            x = det_choice[i].y - C.y
            y = det_choice[i].x - C.x
            det_choice[i].x = C.x - x
            det_choice[i].y = C.y + y
        rotate = False
    for j in range(strings - 1, -1, -1):
        count_cells = sum(1 for i in range(columns) if grid[i][j][0] == 0)
        if count_cells == (columns - 1):
            play_soundtrack("clear.mp3")
            pygame.time.wait(1000)
            play_soundtrack("sound_track.mp3")
            score += 100
            if score % 200 == 0:
                LEVEL += 1
                fps += 10
            for l in range(columns):
                grid[l][j][0] = 1
            for k in range(j, -1, -1):
                for l in range(columns):
                    grid[l][k][0] = grid[l][k - 1][0]
                    grid[l][k][2] = grid[l][k - 1][2]
    score_text = font.render(f"Score: {score}", True, (255, 255, 255))
    screen.blit(score_text, (10, 10))
    score_text2 = font.render(f"LEVEL: {LEVEL}", True, (255, 255, 255))
    screen.blit(score_text2, (10, 30))
    best_score, total_money = get_record()
    best_score_text = font.render(f"Best Score: {best_score}", True, (255, 255, 255))
    screen.blit(best_score_text, (10, 50))
    for i in range(4):
        pygame.draw.rect(screen, pygame.Color(COLOR), det_choice[i])
    pygame.display.flip()
    clock.tick(fps)
conn.close()

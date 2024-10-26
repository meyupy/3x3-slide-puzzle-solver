import pygame
import os
import shutil
from PIL import Image
from itertools import product
import random

pygame.init()

S_WIDTH, S_HEIGHT = 960, 720   # it has to be 4:3
BG_COLOR, BOARD_COLOR = (63, 63, 63), (0, 0, 0)
TEXT_COLOR = (159, 159, 159)
BUTTON_COLOR_1, BUTTON_COLOR_2 = (79, 79, 79), (71, 71, 71)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
font_medium = pygame.font.Font(f"{SCRIPT_DIR}/assets/fonts/MontserratMedium-nRxlJ.ttf", size=S_HEIGHT//18)
font_small = pygame.font.Font(f"{SCRIPT_DIR}/assets/fonts/MontserratMedium-nRxlJ.ttf", size=S_HEIGHT//36)

screen = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
pygame.display.set_caption("3x3 Slide Puzzle Solver")

clock = pygame.time.Clock()

INPUT_DIR = os.path.join(SCRIPT_DIR, "inputs")
OUTPUT_DIR = os.path.join(SCRIPT_DIR, "sliced_images")
input_file_names = next(os.walk(INPUT_DIR), (None, None, []))[2]
sliced_image_names = []
sliced_images = []


def tile(the_file_name, img, dir_out, div_size):

    name, ext = os.path.splitext(the_file_name)
    w, h = img.size

    grid = product(range(0, h - h % div_size, div_size), range(0, w - w % div_size, div_size))
    for i, j in grid:
        box = (j, i, j + div_size, i + div_size)
        out = os.path.join(dir_out, f'{name}_{i//div_size+1}_{j//div_size+1}{ext}')
        img.crop(box).save(out)


def resize_image(img, length):
    if img.size[0] < img.size[1]:

        resized_image = img.resize((length, int(img.size[1] * (length / img.size[0]))))
        required_loss = (resized_image.size[1] - length)
        resized_image = resized_image.crop(
            box=(0, required_loss / 2, length, resized_image.size[1] - required_loss / 2))

        return resized_image

    else:

        resized_image = img.resize((int(img.size[0] * (length / img.size[1])), length))
        required_loss = resized_image.size[0] - length
        resized_image = resized_image.crop(
            box=(required_loss / 2, 0, resized_image.size[0] - required_loss / 2, length))

        return resized_image


if len(input_file_names) == 0:

    raise Exception(f"There is no file in {INPUT_DIR}")


else:

    file_name = random.choice(input_file_names)
    image = Image.open(f"{INPUT_DIR}/{file_name}")

    if image.width != image.height:
        if image.width > image.height:
            image = resize_image(image, image.height)
        elif image.height > image.width:
            image = resize_image(image, image.width)

    image = image.resize((3 * S_WIDTH // 8, 3 * S_WIDTH // 8), Image.LANCZOS)
    shutil.rmtree(OUTPUT_DIR)
    os.mkdir(OUTPUT_DIR)
    tile(file_name, image, OUTPUT_DIR, S_WIDTH // 8)
    sliced_image_names = sorted(next(os.walk(OUTPUT_DIR), (None, None, []))[2])

for image_name in sliced_image_names:
    new_img = pygame.image.load(f"{OUTPUT_DIR}/{image_name}").convert_alpha()
    sliced_images.append(new_img)


def produce_item_coordinates(s_w, s_h):
    return {"board": (s_w//8, s_h//4),
            "display": (s_w//16, s_h//12),
            "button_1": (3 * s_w // 4, 5 * s_h // 12),
            "button_2": (3 * s_w // 4, 2 * s_h // 3)}


def produce_square_coordinates(s_w, m_x, m_y):
    gap = s_w / 16
    return [(m_x+gap, m_y+gap), (m_x+3*gap, m_y+gap), (m_x+5*gap, m_y+gap),
            (m_x+gap, m_y+3*gap), (m_x+3*gap, m_y+3*gap), (m_x+5*gap, m_y+3*gap),
            (m_x+gap, m_y+5*gap), (m_x+3*gap, m_y+5*gap), (m_x+5*gap, m_y+5*gap)]


item_coordinates = produce_item_coordinates(S_WIDTH, S_HEIGHT)
square_coordinates = produce_square_coordinates(S_WIDTH, item_coordinates["board"][0], item_coordinates["board"][1])

board_rect = pygame.Rect(item_coordinates["board"], (S_WIDTH // 2, S_WIDTH // 2))


class Square:

    def __init__(self, number, index, weight, x_pos, y_pos):
        self.weight = weight
        self.number = number
        self.index = index
        self.body_rect = pygame.Rect((x_pos, y_pos), (self.weight, self.weight))
        self.image = sliced_images[self.number - 1]

    def check_if_moves(self, the_neighbour_indexes):
        if self.index in the_neighbour_indexes:
            if pygame.mouse.get_pressed()[0] and self.body_rect.collidepoint(pygame.mouse.get_pos()):
                return True

    def draw(self):
        current_pos = square_coordinates[self.index - 1]
        self.body_rect.topleft = current_pos
        pygame.draw.rect(surface=screen, color=(0, 0, 0), rect=self.body_rect)
        screen.blit(self.image, current_pos)


squares = []
index_square_dict = {}   # index: number (index starts from 1)

for n in range(8):
    new_pos = square_coordinates[n]
    new_square = Square(number=n + 1, index=n + 1, weight=S_WIDTH // 8, x_pos=new_pos[0], y_pos=new_pos[1])
    squares.append(new_square)
    index_square_dict[n + 1] = n + 1

index_square_dict[9] = None


class Button:

    def __init__(self, surface, text, font, x, y, width, height,
                 button_color_1, button_color_2, text_color, border_radius):
        self.surface = surface
        self.button_color_1 = button_color_1
        self.button_color_2 = button_color_2
        self.color = button_color_1
        self.border_radius = border_radius
        self.body_rect = pygame.rect.Rect(x, y, width, height)
        self.text_surf = font.render(text, True, text_color)
        self.text_rect = self.text_surf.get_rect(center=self.body_rect.center)
        self.press_allowed = True
        self.pressed = False

    def is_clicked(self):
        mouse_pressed = pygame.mouse.get_pressed()[0]
        if self.body_rect.collidepoint(pygame.mouse.get_pos()):
            if mouse_pressed:
                self.pressed = True
            elif self.pressed and self.press_allowed:
                self.pressed = False
                return True
        else:
            self.pressed = False
            if mouse_pressed:
                self.press_allowed = False
            else:
                self.press_allowed = True
        return False

    def draw(self):
        if self.body_rect.collidepoint(pygame.mouse.get_pos()):
            self.color = self.button_color_2
        else:
            self.color = self.button_color_1
        pygame.draw.rect(self.surface, self.color, self.body_rect, border_radius=self.border_radius)
        self.surface.blit(self.text_surf, self.text_rect)


button_solve = Button(screen, "Solve", font_small,
                      item_coordinates["button_1"][0], item_coordinates["button_1"][1], S_WIDTH // 8, S_WIDTH // 16,
                      BUTTON_COLOR_1, BUTTON_COLOR_2, TEXT_COLOR, S_WIDTH // 96)
button_reset = Button(screen, "Reset", font_small,
                      item_coordinates["button_2"][0], item_coordinates["button_2"][1], S_WIDTH // 8, S_WIDTH // 16,
                      BUTTON_COLOR_1, BUTTON_COLOR_2, TEXT_COLOR, S_WIDTH // 96)


class Display:

    def __init__(self, height, y_pos):
        self.height = height
        self.body_rect = pygame.rect.Rect((0, y_pos), (S_WIDTH, self.height))
        self.text_surf = None
        self.text_rect = None

    def draw(self, text):
        self.text_surf = font_medium.render(text, True, TEXT_COLOR)
        self.text_rect = self.text_surf.get_rect(center=self.body_rect.center)
        screen.blit(self.text_surf, self.text_rect)


display = Display(S_HEIGHT // 18, 7 * S_HEIGHT // 72)
solution = None

NOTATIONS = ["R", "L", "U", "D"]
OPPOSITE_NOTATIONS = {"R": "L", "L": "R", "U": "D", "D": "U"}


def find_empty_sq_and_neighbor_indexes(perm):

    empty_sq_index = [perm.index(number) + 1 for number in perm if number is None][0]
    neighbor_indexes = []
    amounts = []

    if empty_sq_index in [2, 5, 8]:
        amounts = [-1, 1, -3, 3]
    elif empty_sq_index in [1, 4, 7]:
        amounts = [1, -3, 3]
    elif empty_sq_index in [3, 6, 9]:
        amounts = [-1, -3, 3]

    for amount in amounts:
        neighbor_index = empty_sq_index + amount
        if 1 <= neighbor_index <= 9:
            neighbor_indexes.append(neighbor_index)

    return empty_sq_index, neighbor_indexes


def check_if_solved(perm):
    for i in range(8):
        if perm[i] != i + 1:
            return False
    return True


def produce_perm(empty_sq_index, neighbor_indexes, perm, the_notation):

    the_possible_notations = []

    for neighbor_index in neighbor_indexes:

        if neighbor_index == empty_sq_index - 1:
            the_possible_notations.append("R")
        elif neighbor_index == empty_sq_index + 1:
            the_possible_notations.append("L")
        elif neighbor_index == empty_sq_index + 3:
            the_possible_notations.append("U")
        elif neighbor_index == empty_sq_index - 3:
            the_possible_notations.append("D")

    if the_notation not in the_possible_notations:
        return None

    new_perm = [number for number in perm]
    index_num_to_move = 0

    if the_notation == "R":
        index_num_to_move = empty_sq_index - 1
    elif the_notation == "L":
        index_num_to_move = empty_sq_index + 1
    elif the_notation == "U":
        index_num_to_move = empty_sq_index + 3
    elif the_notation == "D":
        index_num_to_move = empty_sq_index - 3

    num_to_move = perm[index_num_to_move-1]
    new_perm[index_num_to_move - 1] = None
    new_perm[empty_sq_index - 1] = num_to_move

    return new_perm


def steps(paths_and_perms):

    new_paths_and_perms = []

    for path, perm in paths_and_perms:
        checking_notations = [notation for notation in NOTATIONS if OPPOSITE_NOTATIONS[path[-1]] != notation]
        for notation in checking_notations:
            empty_sq_index, neighbor_indexes = find_empty_sq_and_neighbor_indexes(perm)
            new_perm = produce_perm(empty_sq_index, neighbor_indexes, perm, notation)
            if new_perm is not None:
                new_path = [_ for _ in path]
                new_path.append(notation)
                new_path_and_perm = (new_path, new_perm)
                new_paths_and_perms.append(new_path_and_perm)

    for path, perm in new_paths_and_perms:
        if check_if_solved(perm):
            the_solution = path
            return the_solution, new_paths_and_perms

    return None, new_paths_and_perms


def solve_the_board(main_perm):

    if check_if_solved(main_perm):
        return None

    paths_and_perms = []
    empty_sq_index, neighbor_indexes = find_empty_sq_and_neighbor_indexes(main_perm)

    for notation in NOTATIONS:
        checking_perm = produce_perm(empty_sq_index, neighbor_indexes, main_perm, notation)
        if checking_perm is not None:
            new_path_and_perm = ([notation], checking_perm)
            paths_and_perms.append(new_path_and_perm)

    for path, perm in paths_and_perms:
        if check_if_solved(perm):
            return notations_to_arrows(path)

    while True:
        # print(len(paths_and_perms))
        the_solution, paths_and_perms = steps(paths_and_perms)
        if the_solution is not None:
            return notations_to_arrows(the_solution)


def notations_to_arrows(path):
    arrows_path = []
    notation_to_arrow_dict = {"R": "→", "L": "←", "U": "↑", "D": "↓"}
    # notation_to_arrow_dict = {"R": ">", "L": "<", "U": "^", "D": "v"}
    for notation in path:
        arrows_path.append(notation_to_arrow_dict[notation])
    return arrows_path


while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.fill(BG_COLOR)

    pygame.draw.rect(surface=screen, color=BOARD_COLOR, rect=board_rect, border_radius=S_WIDTH // 16)

    current_perm = list(index_square_dict.values())
    empty_square_index, neighbour_indexes = find_empty_sq_and_neighbor_indexes(current_perm)

    for square in squares:

        if square.check_if_moves(neighbour_indexes):
            old_index = square.index
            square.index = empty_square_index
            index_square_dict[old_index] = None
            index_square_dict[empty_square_index] = square.number

        square.draw()

    if button_solve.is_clicked():
        solution = solve_the_board(current_perm)
        if solution is None:
            solution = "Board is already solved."
        else:
            solution = ' '.join([str(n) for n in solution])
    button_solve.draw()

    if button_reset.is_clicked():
        solution = None
        for square in squares:
            index_square_dict[square.number] = square.number
            square.index = square.number
        index_square_dict[9] = None
    button_reset.draw()

    if check_if_solved(current_perm):
        screen.blit(sliced_images[8], square_coordinates[8])

    display.draw(solution)

    clock.tick(60)
    pygame.display.update()

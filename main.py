import os
import pygame

pygame.init()

S_WIDTH, S_HEIGHT = 960, 720   # it has to be 4:3
BG_COLOR, BOARD_COLOR = (191, 191, 191), (127, 127, 127)
SQ_COLOR_1, SQ_COLOR_2 = (159, 159, 159), (151, 151, 151)
TEXT_COLOR_1, TEXT_COLOR_2 = (223, 223, 223), (79, 79, 79)
BUTTON_COLOR_1, BUTTON_COLOR_2 = (159, 159, 159), (143, 143, 143)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
pixel_font_large = pygame.font.Font(f"{SCRIPT_DIR}/assets/fonts/VT323-Regular.ttf", size=S_HEIGHT//12)
pixel_font_medium = pygame.font.Font(f"{SCRIPT_DIR}/assets/fonts/VT323-Regular.ttf", size=S_HEIGHT // 18)
pixel_font_small = pygame.font.Font(f"{SCRIPT_DIR}/assets/fonts/VT323-Regular.ttf", size=S_HEIGHT // 24)

screen = pygame.display.set_mode((S_WIDTH, S_HEIGHT))
clock = pygame.time.Clock()
pygame.display.set_caption("3x3 Slide Puzzle Solver")

def produce_square_coordinates(s_w, m_x, m_y):
    gap = s_w / 48
    return [(m_x+2*gap, m_y+2*gap), (m_x+9*gap, m_y+2*gap), (m_x+16*gap, m_y+2*gap),
            (m_x+2*gap, m_y+9*gap), (m_x+9*gap, m_y+9*gap), (m_x+16*gap, m_y+9*gap),
            (m_x+2*gap, m_y+16*gap), (m_x+9*gap, m_y+16*gap), (m_x+16*gap, m_y+16*gap)]


item_coordinates = {"board": (S_WIDTH // 8, S_HEIGHT // 4),
                    "display": (S_WIDTH // 16, S_HEIGHT // 12),
                    "button_1": (3 * S_WIDTH // 4, 5 * S_HEIGHT // 12),
                    "button_2": (3 * S_WIDTH // 4, 2 * S_HEIGHT // 3)}
square_coordinates = produce_square_coordinates(S_WIDTH, item_coordinates["board"][0], item_coordinates["board"][1])

board_rect = pygame.Rect(item_coordinates["board"], (S_WIDTH // 2, S_WIDTH // 2))


class Square:

    def __init__(self, number, index, weight, x_pos, y_pos):
        self.weight = weight
        self.number = number
        self.index = index
        self.color = SQ_COLOR_1
        self.body_rect = pygame.Rect((x_pos, y_pos), (self.weight, self.weight))
        self.text = pixel_font_large.render(str(self.number), True, TEXT_COLOR_1)
        self.text_rect = self.text.get_rect(center=self.body_rect.center)

    def check_if_moves(self, the_neighbour_indexes):
        if self.index in the_neighbour_indexes:
            if pygame.mouse.get_pressed()[0] and self.body_rect.collidepoint(pygame.mouse.get_pos()):
                return True

    def draw(self):
        self.body_rect.topleft = square_coordinates[self.index - 1]
        if self.body_rect.collidepoint(pygame.mouse.get_pos()):
            self.color = SQ_COLOR_2
        else:
            self.color = SQ_COLOR_1
        pygame.draw.rect(surface=screen, color=self.color, rect=self.body_rect, border_radius=self.weight // 6)
        self.text_rect.center = self.body_rect.center
        screen.blit(self.text, self.text_rect)


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


button_solve = Button(screen, "Solve", pixel_font_small,
                      item_coordinates["button_1"][0], item_coordinates["button_1"][1], S_WIDTH // 8, S_WIDTH // 16,
                      BUTTON_COLOR_1, BUTTON_COLOR_2, TEXT_COLOR_2, S_WIDTH // 96)
button_reset = Button(screen, "Reset", pixel_font_small,
                      item_coordinates["button_2"][0], item_coordinates["button_2"][1], S_WIDTH // 8, S_WIDTH // 16,
                      BUTTON_COLOR_1, BUTTON_COLOR_2, TEXT_COLOR_2, S_WIDTH // 96)


class Display:

    def __init__(self, height, y_pos):
        self.height = height
        self.body_rect = pygame.rect.Rect((0, y_pos), (S_WIDTH, self.height))
        self.text_surf = None
        self.text_rect = None

    def draw(self, text):
        self.text_surf = pixel_font_medium.render(text, True, TEXT_COLOR_2)
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
            return notations_to_numbers(main_perm, path)

    while True:
        # print(len(paths_and_perms))
        the_solution, paths_and_perms = steps(paths_and_perms)
        if the_solution is not None:
            return notations_to_numbers(main_perm, the_solution)


def notations_to_numbers(perm, path):
    numbers_path = []
    new_perm = perm

    for notation in path:

        new_empty_sq_index, new_neighbor_indexes = find_empty_sq_and_neighbor_indexes(new_perm)
        new_number = None

        if notation == "R":
            new_number = new_perm[new_empty_sq_index - 2]
        elif notation == "L":
            new_number = new_perm[new_empty_sq_index]
        elif notation == "U":
            new_number = new_perm[new_empty_sq_index + 2]
        elif notation == "D":
            new_number = new_perm[new_empty_sq_index - 4]

        numbers_path.append(new_number)
        new_perm = produce_perm(new_empty_sq_index, new_neighbor_indexes, new_perm, notation)

    return numbers_path


while True:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    screen.fill(BG_COLOR)

    pygame.draw.rect(surface=screen, color=BOARD_COLOR, rect=board_rect, border_radius=S_WIDTH // 24)

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

    display.draw(solution)

    clock.tick(60)
    pygame.display.update()

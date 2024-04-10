import pygame
from sys import exit

pygame.init()

S_WEIGHT, S_HEIGHT = 960, 720   # it has to be 4:3
BG_COLOR, BOARD_COLOR = (191, 191, 191), (127, 127, 127)
SQ_COLOR_1, SQ_COLOR_2 = (159, 159, 159), (151, 151, 151)
TEXT_COLOR_1, TEXT_COLOR_2 = (223, 223, 223), (79, 79, 79)
BUTTON_COLOR_1, BUTTON_COLOR_2 = (159, 159, 159), (143, 143, 143)

pixel_font_large = pygame.font.Font("assets/fonts/VT323-Regular.ttf", size=S_HEIGHT//12)
pixel_font_medium = pygame.font.Font("assets/fonts/VT323-Regular.ttf", size=S_HEIGHT // 18)
pixel_font_small = pygame.font.Font("assets/fonts/VT323-Regular.ttf", size=S_HEIGHT // 24)

screen = pygame.display.set_mode((S_WEIGHT, S_HEIGHT))
pygame.display.set_caption("3x3 Slide Puzzle Solver")

clock = pygame.time.Clock()


def produce_item_coordinates(s_w, s_h):
    return {"board": (s_w//8, s_h//4),
            "display": (s_w//16, s_h//12),
            "button_1": (3 * s_w // 4, 5 * s_h // 12),
            "button_2": (3 * s_w // 4, 2 * s_h // 3)}


def produce_square_coordinates(s_w, m_x, m_y):
    gap = s_w / 48
    return [(m_x+2*gap, m_y+2*gap), (m_x+9*gap, m_y+2*gap), (m_x+16*gap, m_y+2*gap),
            (m_x+2*gap, m_y+9*gap), (m_x+9*gap, m_y+9*gap), (m_x+16*gap, m_y+9*gap),
            (m_x+2*gap, m_y+16*gap), (m_x+9*gap, m_y+16*gap), (m_x+16*gap, m_y+16*gap)]


item_coordinates = produce_item_coordinates(S_WEIGHT, S_HEIGHT)
square_coordinates = produce_square_coordinates(S_WEIGHT, item_coordinates["board"][0], item_coordinates["board"][1])

board_rect = pygame.Rect(item_coordinates["board"], (S_WEIGHT//2, S_WEIGHT//2))


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
    new_square = Square(number=n + 1, index=n + 1, weight=S_WEIGHT // 8, x_pos=new_pos[0], y_pos=new_pos[1])
    squares.append(new_square)
    index_square_dict[n + 1] = n + 1

index_square_dict[9] = None


class Button:

    def __init__(self, text, width, pos):
        self.width = width
        self.height = width // 2
        self.pressed = False
        self.body_rect = pygame.Rect(pos, (self.width, self.height))
        self.body_color = BUTTON_COLOR_1
        self.text_surf = pixel_font_small.render(text, True, TEXT_COLOR_2)
        self.text_rect = self.text_surf.get_rect(center=self.body_rect.center)

    def draw(self):
        pygame.draw.rect(screen, self.body_color, self.body_rect, border_radius=self.width // 12)
        screen.blit(self.text_surf, self.text_rect)

    def check_button_clicked(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.body_rect.collidepoint(mouse_pos):
            self.body_color = BUTTON_COLOR_2
            if pygame.mouse.get_pressed()[0]:
                self.pressed = True
            else:
                if self.pressed:
                    self.pressed = False
                    return True
        else:
            self.body_color = BUTTON_COLOR_1
            self.pressed = False
        return False


button_solve = Button("Solve", S_WEIGHT // 8, item_coordinates["button_1"])
button_reset = Button("Reset", S_WEIGHT // 8, item_coordinates["button_2"])


class Display:

    def __init__(self, height, y_pos):
        self.height = height
        self.body_rect = pygame.rect.Rect((0, y_pos), (S_WEIGHT, self.height))
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

    pygame.draw.rect(surface=screen, color=BOARD_COLOR, rect=board_rect, border_radius=S_WEIGHT//24)

    current_perm = list(index_square_dict.values())
    empty_square_index, neighbour_indexes = find_empty_sq_and_neighbor_indexes(current_perm)

    for square in squares:

        if square.check_if_moves(neighbour_indexes):
            old_index = square.index
            square.index = empty_square_index
            index_square_dict[old_index] = None
            index_square_dict[empty_square_index] = square.number

        square.draw()

    if button_solve.check_button_clicked():
        solution = solve_the_board(current_perm)
        if solution is None:
            solution = "Board is already solved."
        else:
            solution = ' '.join([str(n) for n in solution])
    button_solve.draw()

    if button_reset.check_button_clicked():
        solution = None
        for square in squares:
            index_square_dict[square.number] = square.number
            square.index = square.number
        index_square_dict[9] = None
    button_reset.draw()

    display.draw(solution)

    clock.tick(60)
    pygame.display.update()

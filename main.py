import re
import sys
import os
import pygame
from utils import scale_image
from car import Car
from game_info import GameInfo
import neat
from neat import visualize
import pickle
import exceptions
import matplotlib.pyplot as plt
import tempfile

pygame.font.init()

TRACK = scale_image(pygame.image.load("imgs/track.png"), 0.9)
GRASS = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)
WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Autonomous car")
MAIN_FONT = pygame.font.SysFont("comicsans", 44)
SECONDARY_FONT = pygame.font.SysFont("comicsans", 24)
RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.55)

PATH_POINTS = []

LEVELS = [
    {
        "track_img": "imgs/circuito_1.png",
        "border_img": "imgs/circuito_1_bordo.png",
        "finish_img": "imgs/finish_line_1.png",
        "finish_position": (50, 400),
        "start_position": (100, 370),
        "path_points": [(83, 383), (116, 314), (167, 240), (225, 177), (299, 131), (395, 107), (503, 110), (601, 167),
                        (678, 242), (713, 320), (726, 407), (737, 482), (729, 565), (697, 639), (618, 716), (507, 756),
                        (387, 775), (246, 722), (165, 636), (101, 567), (86, 510), (76, 446)]
    },
    {
        "track_img": "imgs/circuito_2.png",
        "border_img": "imgs/circuito_2_bordo.png",
        "finish_img": "imgs/finish_line_2.png",
        "finish_position": (20, 400),
        "start_position": (80, 370),
        "path_points": [(63, 367), (69, 337), (84, 305), (107, 281), (137, 262), (179, 245), (218, 243), (256, 247),
                        (289, 262), (317, 284), (341, 296), (369, 305), (411, 315), (445, 313), (485, 305), (514, 291),
                        (540, 270), (540, 270), (563, 248), (592, 229), (630, 222), (671, 238), (696, 261), (717, 285),
                        (730, 325), (735, 360), (736, 395), (728, 426), (718, 456), (706, 477), (689, 503), (674, 527),
                        (653, 553), (624, 567), (587, 579), (547, 577), (519, 552), (495, 523), (461, 501), (461, 501),
                        (421, 479), (383, 471), (337, 474), (286, 483), (249, 501), (228, 518), (198, 536), (151, 557),
                        (112, 553), (88, 534), (71, 504), (61, 470), (59, 438)]
    },
    {
        "track_img": "imgs/circuito_3.png",
        "border_img": "imgs/circuito_3_bordo.png",
        "finish_img": "imgs/finish_line_2.png",
        "finish_position": (30, 420),
        "start_position": (110, 380),
        "path_points": [(99, 399), (123, 362), (141, 337), (142, 297), (130, 269), (114, 248), (100, 225), (89, 202),
                        (85, 173), (85, 149), (94, 119), (120, 107), (152, 99), (188, 94), (236, 89), (258, 85),
                        (280, 82), (324, 77), (359, 75), (397, 75), (425, 77), (461, 77), (498, 77), (531, 79),
                        (556, 83), (572, 94), (593, 112), (612, 130), (631, 147), (669, 149), (703, 150), (726, 150),
                        (750, 158), (761, 186), (761, 217), (753, 238), (716, 260), (678, 278), (654, 286), (627, 301),
                        (618, 328), (618, 346), (636, 368), (648, 383), (658, 399), (676, 418), (692, 434), (713, 449),
                        (732, 462), (747, 489), (753, 515), (756, 544), (757, 568), (752, 591), (739, 627), (718, 632),
                        (698, 625), (681, 617), (643, 605), (624, 602), (597, 606), (573, 620), (558, 633), (540, 647),
                        (522, 650), (492, 648), (476, 646), (439, 645), (404, 644), (394, 643), (357, 638), (325, 636),
                        (305, 642), (285, 654), (257, 668), (245, 671), (196, 671), (173, 665), (167, 653), (154, 630),
                        (150, 620), (139, 598), (127, 578), (121, 559), (108, 525), (103, 510), (100, 478), (97, 466)]
    },
    {
        "track_img": "imgs/circuito_4.png",
        "border_img": "imgs/circuito_4_bordo.png",
        "finish_img": "imgs/finish_line_2.png",
        "finish_position": (20, 420),
        "start_position": (50, 380),
        "path_points": [(53, 393), (55, 356), (59, 323), (58, 287), (55, 257), (54, 221), (53, 194), (52, 155),
                        (54, 126), (57, 97), (77, 82), (102, 76), (129, 76), (159, 87), (163, 107), (163, 141),
                        (162, 175), (159, 202), (155, 233), (155, 264), (161, 286), (165, 309), (171, 325), (181, 341),
                        (205, 342), (230, 333), (246, 321), (252, 291), (252, 291), (249, 262), (248, 245), (248, 216),
                        (251, 181), (256, 141), (254, 97), (258, 78), (273, 68), (293, 71), (311, 68), (347, 61),
                        (385, 63), (433, 62), (506, 60), (574, 60), (630, 60), (677, 65), (705, 70), (714, 72),
                        (724, 78), (739, 90), (743, 99), (750, 118), (750, 133), (746, 153), (746, 177), (745, 198),
                        (744, 221), (732, 230), (702, 235), (685, 235), (647, 237), (647, 237), (601, 239), (565, 237),
                        (513, 237), (472, 237), (445, 238), (427, 244), (423, 253), (419, 266), (417, 274), (412, 282),
                        (410, 296), (418, 310), (426, 316), (450, 324), (460, 326), (502, 324), (557, 318), (600, 318),
                        (652, 322), (706, 323), (746, 328), (756, 378), (756, 403), (761, 457), (753, 485), (753, 519),
                        (759, 566), (757, 586), (756, 629), (753, 658), (753, 677), (740, 693), (728, 701), (709, 712),
                        (700, 716), (676, 723), (671, 725), (644, 725), (632, 725), (617, 723), (601, 718), (578, 707),
                        (561, 694), (550, 679), (548, 652), (551, 609), (552, 560), (558, 516), (552, 479), (540, 448),
                        (522, 431), (505, 424), (475, 409), (442, 399), (416, 395), (391, 393), (371, 395), (353, 399),
                        (336, 409), (312, 414), (305, 419), (286, 433), (286, 433), (266, 447), (262, 470), (266, 505),
                        (260, 550), (256, 584), (264, 630), (257, 665), (254, 688), (249, 702), (227, 720), (212, 720),
                        (183, 711), (171, 703), (152, 680), (135, 656), (115, 627), (92, 589), (74, 551), (65, 513),
                        (64, 465), (63, 442)]
    },
    {
        "track_img": "imgs/circuito_5.png",
        "border_img": "imgs/circuito_5_bordo.png",
        "finish_img": "imgs/finish_line_2.png",
        "finish_position": (20, 420),
        "start_position": (50, 380),
        "path_points": [(53, 393), (55, 356), (59, 323), (58, 287), (55, 257), (54, 221), (53, 194), (52, 155),
                        (54, 126), (57, 97), (77, 82), (102, 76), (129, 76), (159, 87), (163, 107), (163, 141),
                        (162, 175), (159, 202), (155, 233), (155, 264), (161, 286), (165, 309), (171, 325), (181, 341),
                        (205, 342), (230, 333), (246, 321), (252, 291), (252, 291), (249, 262), (248, 245), (248, 216),
                        (251, 181), (256, 141), (254, 97), (258, 78), (273, 68), (293, 71), (311, 68), (347, 61),
                        (385, 63), (433, 62), (506, 60), (574, 60), (630, 60), (677, 65), (705, 70), (714, 72),
                        (724, 78), (739, 90), (743, 99), (750, 118), (750, 133), (746, 153), (746, 177), (745, 198),
                        (744, 221), (732, 230), (702, 235), (685, 235), (647, 237), (647, 237), (601, 239), (565, 237),
                        (513, 237), (472, 237), (445, 238), (427, 244), (423, 253), (419, 266), (417, 274), (412, 282),
                        (410, 296), (418, 310), (426, 316), (450, 324), (460, 326), (502, 324), (557, 318), (600, 318),
                        (652, 322), (706, 323), (746, 328), (756, 378), (756, 403), (761, 457), (753, 485), (753, 519),
                        (759, 566), (757, 586), (756, 629), (753, 658), (753, 677), (740, 693), (728, 701), (709, 712),
                        (700, 716), (676, 723), (671, 725), (644, 725), (632, 725), (617, 723), (601, 718), (578, 707),
                        (561, 694), (550, 679), (548, 652), (551, 609), (552, 560), (558, 516), (552, 479), (540, 448),
                        (522, 431), (505, 424), (475, 409), (442, 399), (416, 395), (391, 393), (371, 395), (353, 399),
                        (336, 409), (312, 414), (305, 419), (286, 433), (286, 433), (266, 447), (262, 470), (266, 505),
                        (260, 550), (256, 584), (264, 630), (257, 665), (254, 688), (249, 702), (227, 720), (212, 720),
                        (183, 711), (171, 703), (152, 680), (135, 656), (115, 627), (92, 589), (74, 551), (65, 513),
                        (64, 465), (63, 442)]
    },
    {
        "track_img": "imgs/track.png",
        "border_img": "imgs/track-border.png",
        "finish_img": "imgs/finish.png",
        "finish_position": (120, 270),
        "start_position": (180, 220),
        "path_points": [(175, 249), (176, 222), (175, 194), (176, 166), (175, 135), (171, 109), (156, 89), (124, 78),
                        (92, 85), (73, 103), (64, 125), (60, 153), (58, 180), (60, 255), (59, 338), (57, 410),
                        (67, 480), (124, 553), (193, 618), (261, 689), (305, 730), (328, 737), (349, 737), (372, 730),
                        (386, 723), (395, 705), (402, 682), (403, 656), (403, 613), (406, 574), (406, 574), (407, 549),
                        (415, 529), (424, 512), (436, 503), (457, 492), (471, 488), (493, 484), (505, 484), (518, 487),
                        (533, 492), (555, 499), (565, 507), (574, 521), (582, 528), (590, 545), (589, 564), (591, 593),
                        (593, 622), (591, 649), (602, 681), (607, 701), (613, 714), (627, 722), (643, 730), (656, 730),
                        (680, 735), (696, 730), (710, 727), (724, 718), (734, 702), (738, 686), (738, 645), (737, 583),
                        (732, 521), (733, 460), (730, 407), (723, 387), (709, 381), (687, 376), (667, 372), (643, 372),
                        (619, 369), (574, 363), (542, 366), (496, 363), (457, 357), (415, 347), (402, 331), (393, 316),
                        (393, 300), (396, 285), (404, 276), (416, 269), (429, 266), (444, 266), (461, 267), (484, 267),
                        (515, 267), (562, 267), (596, 266), (642, 263), (689, 257), (722, 251), (734, 240), (736, 230),
                        (736, 217), (738, 198), (735, 182), (735, 167), (734, 152), (734, 134), (733, 112), (726, 102),
                        (711, 92), (692, 89), (674, 85), (654, 82), (623, 82), (582, 81), (524, 79), (487, 82),
                        (433, 76), (396, 78), (361, 83), (334, 83), (322, 83), (309, 87), (294, 92), (290, 101),
                        (287, 114), (287, 126), (287, 139), (286, 151), (284, 160), (286, 179), (283, 206), (286, 234),
                        (292, 255), (288, 276), (288, 305), (289, 333), (287, 354), (278, 376), (265, 392), (257, 397),
                        (247, 404), (236, 407), (224, 407), (212, 404), (191, 401), (181, 392), (177, 379), (174, 358),
                        (174, 338), (173, 308), (170, 295)]
    },
]

loaded_tracks = []

FPS = 60

validation_car = None
trained_net = None
trained_net = None
num_generations = 15
current_generation = 0

game_info = GameInfo(WIN, WIDTH, HEIGHT)

stop_neat = False;


def load_trained_car(filename="trained_car.pkl"):
    with open(filename, 'rb') as file:
        return pickle.load(file)


def draw(win, cars, background_surface, stats=None):
    global game_info

    win.blit(background_surface, (0, 0))
    for car in cars:
        car.draw(win, True)
    if validation_car is not None:
        validation_car.draw(win, True)

    if stats:
        game_info.draw_statistics(stats)

    pygame.display.update()


def remove(index):
    cars.pop(index)
    ge.pop(index)
    nets.pop(index)


def next_level():
    global game_info, current_generation, num_generations, stop_neat

    game_info.current_level += 1
    if game_info.mode == "TRAINING":
        if game_info.current_level >= game_info.n_training:
            print("WIN! Nuova generazione nello stesso livellO")
            # stop_neat = game_info.victory_menu(current_generation >= num_generations - 1)
        else:
            load_level()
    elif game_info.mode == "VALIDATION":
        if game_info.current_level >= (game_info.n_training + game_info.n_validation):
            game_info.victory_menu(current_generation >= num_generations - 1)
        else:
            load_level()
    elif game_info.mode == "SIMULATION":
        if game_info.current_level >= (game_info.n_training + game_info.n_validation):
            print("WIN! Nuova generazione nello stesso livellO")
        else:
            load_level()


background_surface = pygame.Surface((WIDTH, HEIGHT))
loaded = False


def load_level():
    global RED_CAR, loaded, WIN, WIDTH, HEIGHT, TRACK, TRACK_BORDER, TRACK_BORDER_MASK, FINISH, FINISH_MASK, FINISH_POSITION, START_POSITION, PATH_POINTS, game_info, background_surface

    if game_info.mode == "TRAINING" and game_info.n_training == 0:
        return
    elif game_info.mode == "VALIDATION" and game_info.n_validation == 0:
        return

    # Carica le immagini per il livello corrente
    level_info = game_info.selected_levels[game_info.current_level]
    TRACK = scale_image(pygame.image.load(level_info["track_img"]), 0.7)
    TRACK_BORDER = scale_image(pygame.image.load(level_info["border_img"]), 0.7)
    FINISH = scale_image(pygame.image.load(level_info["finish_img"]), 0.7)
    FINISH_POSITION = level_info["finish_position"]
    START_POSITION = level_info["start_position"]
    PATH_POINTS = level_info["path_points"]

    if level_info["track_img"] == "imgs/circuito_5.png":
        TRACK = scale_image(pygame.image.load(level_info["track_img"]), 0.57)
        TRACK_BORDER = scale_image(pygame.image.load(level_info["border_img"]), 0.57)
        FINISH = scale_image(pygame.image.load(level_info["finish_img"]), 0.57)
        if not loaded:
            WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
            WIN = pygame.display.set_mode((WIDTH, HEIGHT))
            background_surface = pygame.Surface((WIDTH, HEIGHT))
            RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.4)
            loaded = True
    else:
        if level_info["track_img"] == "imgs/track.png":
            TRACK = scale_image(pygame.image.load(level_info["track_img"]), 0.9)
            TRACK_BORDER = scale_image(pygame.image.load(level_info["border_img"]), 0.9)
            FINISH = scale_image(pygame.image.load(level_info["finish_img"]), 1)
        if level_info["track_img"] == "imgs/circuito_3.png":
            FINISH = scale_image(pygame.image.load(level_info["finish_img"]), 0.8)
        if level_info["track_img"] == "imgs/circuito_4.png":
            TRACK = scale_image(pygame.image.load(level_info["track_img"]), 0.67)
            TRACK_BORDER = scale_image(pygame.image.load(level_info["border_img"]), 0.67)
            FINISH = scale_image(pygame.image.load(level_info["finish_img"]), 0.57)
        if loaded:
            WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
            WIN = pygame.display.set_mode((WIDTH, HEIGHT))
            background_surface = pygame.Surface((WIDTH, HEIGHT))
            RED_CAR = scale_image(pygame.image.load("imgs/red-car.png"), 0.53)
            loaded = False

    # Aggiorna le maschere
    TRACK_BORDER_MASK = pygame.mask.from_surface(TRACK_BORDER)
    FINISH_MASK = pygame.mask.from_surface(FINISH)

    imgs = [
        (GRASS, (0, 0)),
        (TRACK, (0, 0)),
        (FINISH, FINISH_POSITION),
        (TRACK_BORDER, (0, 0))
    ]
    for img, pos in imgs:
        background_surface.blit(img, pos)


clock = pygame.time.Clock()


def eval_genomes(genomes, config):
    global cars, ge, nets, validation_car, pop, game_info, \
        current_generation, num_generations, stop_neat, current_mutation_rate, \
        current_num_cars, current_simulation_num

    if game_info.mode == "TRAINING" or game_info.mode == "SIMULATION":
        cars = []
        ge = []
        nets = []

        stats = {
            "generation": pop.generation,
            "best_fitness": 0,
            "num_species": len(pop.species.species),
            "num_alive": 0
        }

        if game_info.mode == "SIMULATION":
            stats["mutation_rate"] = current_mutation_rate
            stats["num_cars"] = current_num_cars
            stats["simulation_index"] = current_simulation_num

        current_generation = pop.generation

        if game_info.current_level == 0:
            load_level()

        for genome_id, genome in genomes:
            cars.append(Car(4, 7, START_POSITION, PATH_POINTS, RED_CAR))
            ge.append(genome)
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            nets.append(net)
            genome.fitness = 0

        max_fitness = 0

        run = True
        while run:
            clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            stats['num_alive'] = len(cars)

            draw(WIN, cars, background_surface, stats)

            if len(cars) == 0:
                break

            winner_found = False
            for i, car in enumerate(cars):
                alive_score = 1
                distance_reached_score = int(car.nearest_point_reached)
                safe_driving_score = car.average_distance_from_edges()
                win_score = 500

                ge[i].fitness += alive_score + (distance_reached_score / 50) + (safe_driving_score / 10)

                # Aggiornamento delle statistiche
                if ge[i].fitness > max_fitness:
                    max_fitness = ge[i].fitness

                if car.winner:
                    ge[i].fitness += win_score * (game_info.current_level + 1)
                    winner_found = True
                    game_info.winner_genome = ge[i]
                    next_level()
                    if game_info.mode == "SIMULATION":
                        car.winner = False
                    break

                if car.damaged:
                    remove(i)

            stats['best_fitness'] = max_fitness
            stats['num_alive'] = len(cars)
            draw(WIN, cars, background_surface, stats)

            if winner_found:
                if stop_neat:
                    raise exceptions.EarlyStoppingException("NEAT Stopping condition reached")
                break

            for i, car in enumerate(cars):
                output = nets[i].activate(car.data())
                if output[0] > 0.7:
                    car.controls.right = True
                    car.controls.left = False
                if output[1] > 0.7:
                    car.controls.left = True
                    car.controls.right = False
                if output[0] <= 0.7 and output[1] <= 0.7:
                    car.controls.right = False
                    car.controls.left = False

            for car in cars:
                car.update(WIN, MAIN_FONT, TRACK_BORDER_MASK, FINISH_MASK, FINISH_POSITION)

        # Aggiornamento delle statistiche alla fine di una generazione
        stats["generation"] = pop.generation
        stats["num_species"] = len(pop.species.species)

    elif game_info.mode == "VALIDATION":
        while game_info.current_level < len(LEVELS):

            if game_info.current_level == game_info.n_training:
                load_level()

            validation_car = Car(4, 4, START_POSITION, PATH_POINTS, RED_CAR)

            run = True
            while run:
                clock.tick(FPS)
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                        sys.exit()

                draw(WIN, [validation_car], background_surface)

                if validation_car.winner:
                    next_level()
                    break

                if validation_car.damaged:
                    game_info.game_over_menu()
                    break

                output = trained_net.activate(validation_car.data())
                if output[0] > 0.7:
                    validation_car.controls.right = True
                    validation_car.controls.left = False
                if output[1] > 0.7:
                    validation_car.controls.left = True
                    validation_car.controls.right = False
                if output[0] <= 0.7 and output[1] <= 0.7:
                    validation_car.controls.right = False
                    validation_car.controls.left = False

                validation_car.update(WIN, MAIN_FONT, TRACK_BORDER_MASK, FINISH_MASK, FINISH_POSITION)


def draw_point(win, position):
    pygame.draw.circle(win, (255, 0, 0), position, 5)


def capture_points():
    pygame.init()
    global WIN, background_surface
    load_level()

    points = []

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Salva le coordinate del click e disegna un punto rosso
                pos = pygame.mouse.get_pos()
                points.append(pos)
                draw_point(WIN, pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    # Rimuovi l'ultimo punto se Ctrl+Z è premuto
                    if points:
                        points.pop()

        WIN.blit(background_surface, (0, 0))
        for point in points:
            draw_point(WIN, point)

        pygame.display.update()

    # Stampa l'array delle coordinate quando il programma viene chiuso
    print(points)
    pygame.quit()


def load_saved_levels():
    global game_info

    try:
        with open('saved_levels.pkl', 'rb') as f:
            saved_config = pickle.load(f)
            print(saved_config)

            game_info.selected_tracks = saved_config["selected_tracks"] if "selected_tracks" in saved_config else [0, 1,
                                                                                                                   2]
            game_info.n_training = saved_config["n_training"] if "n_training" in saved_config else 3
            game_info.n_validation = saved_config["n_validation"] if "n_validation" in saved_config else 0
    except FileNotFoundError:
        game_info.selected_tracks = [0, 1, 2]
        game_info.n_training = 3
        game_info.n_validation = 0

    game_info.selected_levels.clear()
    for level_idx in game_info.selected_tracks:
        game_info.selected_levels.append(LEVELS[level_idx])
    print(game_info.selected_levels)


def show_popup_message(message, duration=3):
    start_time = pygame.time.get_ticks()
    font = pygame.font.SysFont("comicsans", 30)
    text_surf = font.render(message, True, (255, 0, 0))
    text_rect = text_surf.get_rect(center=(WIDTH // 2, 50))

    while (pygame.time.get_ticks() - start_time) < (duration * 1000):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        WIN.blit(text_surf, text_rect)
        pygame.display.update()


def main_menu():
    global LEVELS, loaded_tracks, game_info
    menu_options = [
        "Allenamento",
        "Validazione",
        "Simulazione",
        "Modifica percorsi",
        "Cattura punti",
        # "Modifica macchina"
    ]

    title = "AI Car Simulation"

    load_saved_levels()

    loaded_tracks.clear()
    for level in LEVELS:
        img = pygame.image.load(level["track_img"])
        img = pygame.transform.scale(img, (100, 100))
        loaded_tracks.append(img)

    running = True
    while running:

        if game_info.track_config_changed:
            load_saved_levels()
            game_info.track_config_changed = False
            print("percorsi caricati")

        game_info.draw_menu(menu_options, title)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if 200 <= y <= 240:
                    if game_info.n_training <= 0:
                        show_popup_message("Selezionare almeno un percorso di training", 2)
                    else:
                        game_info.mode = "TRAINING"
                        running = False
                elif 260 <= y <= 300:
                    if game_info.n_validation <= 0:
                        show_popup_message("Selezionare almeno un percorso di validazione", 2)
                    else:
                        game_info.mode = "VALIDATION"
                        running = False
                elif 320 <= y <= 360:
                    game_info.mode = "SIMULATION"
                    running = False
                elif 380 <= y <= 420:
                    game_info.track_selection_menu(LEVELS, loaded_tracks)
                elif 440 <= y <= 480:
                    game_info.mode = "CAPTURE_POINTS"
                    game_info.current_level = 3
                    running = False

        if game_info.mode == "TRAINING":
            game_info.current_level = 0
        elif game_info.mode == "VALIDATION":
            game_info.current_level = game_info.n_training


def run(config_path):
    global pop, trained_net, num_generations

    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    if game_info.mode == "TRAINING":
        pop = neat.Population(config)
        pop.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        pop.add_reporter(stats)

        winner = pop.run(eval_genomes, num_generations)

        # Display the winning genome.
        print("\nDrawing best genome\n")

        print('\nBest genome:\n{!s}'.format(winner))

        node_names = {-1: 'Sensore1', -2: 'Sensore2', -3: 'Sensore3',
                      -4: 'Sensore4', -5: 'Sensore5', -6: 'Sensore6',
                      0: 'Sinistra', 1: 'Destra'}

        print("\nDrawing nets\n")

        neat.nn.FeedForwardNetwork.create(winner, config)

        visualize.draw_net(config, winner, True, node_names=node_names)

        print("\nDrawing plots\n")

        visualize.plot_stats(stats, ylog=False, view=True)
        visualize.plot_species(stats, view=True)

        plot_single_fitness(stats.get_fitness_mean(), "Andamento Fitness Media", "fitness_media")
        plot_single_fitness(stats.get_fitness_stat(max), "Andamento Fitness Migliore", "fitness_best")

    elif game_info.mode == "VALIDATION":
        trained_net = neat.nn.FeedForwardNetwork.create(game_info.winner_genome, config)
        eval_genomes([], config)


def run_simulation(mutation_rate, num_pop, max_generations, simulation_idx):
    global pop

    temp_config_path = create_config(mutation_rate, num_pop, simulation_idx)
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         temp_config_path)
    pop = neat.Population(config)
    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    pop.run(eval_genomes, max_generations)

    mean_fitness_data = stats.get_fitness_mean()
    best_fitness_data = stats.get_fitness_stat(max)

    os.remove(temp_config_path)
    return mean_fitness_data, best_fitness_data

current_mutation_rate = 0.0
current_num_cars = 0
current_simulation_num = 0
def create_config(mutation_rate, num_cars, simulation_idx, base_config_path='config.txt'):
    global current_mutation_rate, current_num_cars, current_simulation_num

    # Legge il contenuto del file di configurazione base
    with open(base_config_path, 'r') as file:
        config_content = file.read();

    # Modificare il contenuto della configurazione con i parametri della simulazione
    config_content = re.sub(r'pop_size\s*=\s*\d+', f'pop_size = {num_cars}', config_content)
    config_content = re.sub(r'weight_mutate_rate\s*=\s*[\d.]+', f'weight_mutate_rate = {mutation_rate}', config_content)

    current_mutation_rate = mutation_rate
    current_num_cars = num_cars
    current_simulation_num = simulation_idx

    print(config_content)

    # Crea un file di configurazione temporaneo
    temp_config_path = tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt')
    temp_config_path.write(config_content)
    temp_config_path.close()

    return temp_config_path.name

def plot_single_fitness(data, title, plot_name):
    plt.plot(data)

    plt.xlabel('Generazioni')
    plt.ylabel('Fitness')
    plt.title(title)

    if not os.path.exists('plots'):
        os.makedirs('plots')

    plt.savefig(f'plots/{plot_name}.png')
    plt.close()

def plot_fitness_over_generations(data, title, plot_name):
    for variation, fitness_data in data.items():
        plt.plot(fitness_data, label=variation)

    plt.xlabel('Generazioni')
    plt.ylabel('Fitness')
    plt.title(title)
    plt.legend()

    if not os.path.exists('plots'):
        os.makedirs('plots')

    plt.savefig(f'plots/{plot_name}.png')
    plt.close()


if __name__ == '__main__':
    pygame.init()
    WIN = pygame.display.set_mode((WIDTH, HEIGHT))

    main_menu()

    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    if game_info.mode == "SIMULATION":
        mutation_rates = [0.1, 0.3, 0.5, 0.7, 0.9]
        pop_density = [10, 20, 30, 50, 100]
        base_rate = 0.8
        base_density = 30
        num_simulations = 3
        max_generations = 10

        def calcola_media(liste_di_fitness):
            # Calcola la media delle fitness per ogni generazione
            media_fitness = [sum(valori) / len(valori) for valori in zip(*liste_di_fitness)]
            return media_fitness

        def reset_simulation():
            game_info.current_level = 0
            load_level()

        # Eseguo la simulazione variando il tasso di mutazione
        plt.figure()
        fitness_data_mutation_mean = {}
        fitness_data_mutation_best = {}
        for rate in mutation_rates:
            all_data_mean = []
            all_data_best = []
            for i in range(num_simulations):
                reset_simulation()
                mean_fitness, best_fitness = run_simulation(rate, base_density, max_generations, i)
                all_data_mean.append(mean_fitness)
                all_data_best.append(best_fitness)
            fitness_data_mutation_mean[f"Mutation rate {rate}"] = calcola_media(all_data_mean)
            fitness_data_mutation_best[f"Mutation rate {rate}"] = calcola_media(all_data_best)

        plot_fitness_over_generations(fitness_data_mutation_mean, "Andamento Fitness Media per Tasso di Mutazione", "fitness_media_tasso_mutazione")
        plot_fitness_over_generations(fitness_data_mutation_best, "Andamento Best Fitness per Tasso di Mutazione", "best_fitness_tasso_mutazione")

        # Eseguo la simulazione variando il numero di macchine
        fitness_data_density_mean = {}
        fitness_data_density_best = {}
        for density in pop_density:
            all_data_mean = []
            all_data_best = []
            for i in range(num_simulations):
                reset_simulation()
                mean_fitness, best_fitness = run_simulation(base_rate, density, max_generations, i)
                all_data_mean.append(mean_fitness)
                all_data_best.append(best_fitness)
            fitness_data_density_mean[f"Pop Density {density}"] = calcola_media(all_data_mean)
            fitness_data_density_best[f"Pop Density {density}"] = calcola_media(all_data_best)

        plot_fitness_over_generations(fitness_data_density_mean, "Andamento Fitness Media per Numero di Macchine", "fitness_media_numero_macchine")
        plot_fitness_over_generations(fitness_data_density_best, "Andamento Best Fitness per Numero di Macchine", "best_fitness_numero_macchine")
    elif game_info.mode == "TRAINING":
        run(config_path)
    elif game_info.mode == "VALIDATION":
        game_info.winner_genome = load_trained_car()
        run(config_path)
    elif game_info.mode == "CAPTURE_POINTS":
        capture_points()

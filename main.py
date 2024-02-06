

# ------------------------------------------------------ IMPORT ------------------------------------------------------


import re
import sys
import os
import pygame
from utils import scale_image
from car import Car
from game_info import GameInfo
import neat
import pickle
import matplotlib.pyplot as plt
import tempfile
from levels_data import LEVELS


# ------------------------------------------------- GLOBAL VARIABLES -------------------------------------------------


# GAME VARIABLES
FPS = 60
CLOCK = pygame.time.Clock()
WINDOW = None
WINDOW_TITLE = "Autonomous car"

# SIMULATION VARIABLES
LEVEL_LOADED = False
FINISH_POSITION = (0, 0)
START_POSITION = (0, 0)
PATH_POINTS = []
LOADED_TRACKS = []
RED_CAR_IMG = scale_image(pygame.image.load("imgs/red-car.png"), 0.55)
TRACK_IMG = scale_image(pygame.image.load("imgs/track.png"), 0.9)
GRASS_IMG = scale_image(pygame.image.load("imgs/grass.jpg"), 2.5)
WIDTH, HEIGHT = TRACK_IMG.get_width(), TRACK_IMG.get_height()
GAME_INFO = None
MAIN_FONT = None
BACKGROUND_SURFACE = pygame.Surface((WIDTH, HEIGHT))
TRACK_BORDER_MASK = None
FINISH_LINE_MASK = None

# NEAT VARIABLES
NUM_GENERATIONS = 1000
CURRENT_GENERATION = 0
WINNER_GENOME = None
TRAINED_NET = None
VALIDATION_CAR = None
CARS = None
GE = None
NETS = None
POP = None
CURRENT_MUTATION_RATE = 0.0
CURRENT_NUM_CARS = 0
CURRENT_SIMULATION_NUM = 0


# ---------------------------------------------------- FUNCTIONS ------------------------------------------------------


'''
Neat fitness function. 
'''
def eval_genomes(genomes, config):
    global CARS, GE, NETS, VALIDATION_CAR, CURRENT_GENERATION, WINNER_GENOME

    # TRAINING/SIMULATION MODE
    if GAME_INFO.mode == "TRAINING" or GAME_INFO.mode == "SIMULATION":
        # Init population arrays
        CARS = []
        GE = []
        NETS = []

        # Init stats
        stats = {
            "generation": POP.generation,
            "best_fitness": 0,
            "num_species": len(POP.species.species),
            "num_alive": 0
        }
        if GAME_INFO.mode == "SIMULATION":
            stats["mutation_rate"] = CURRENT_MUTATION_RATE
            stats["num_cars"] = CURRENT_NUM_CARS
            stats["simulation_index"] = CURRENT_SIMULATION_NUM

        # Level loading
        CURRENT_GENERATION = POP.generation
        if GAME_INFO.current_level == 0:
            load_level()

        # Create population
        for genome_id, genome in genomes:
            CARS.append(Car(4, 7, START_POSITION, PATH_POINTS, RED_CAR_IMG))
            GE.append(genome)
            net = neat.nn.FeedForwardNetwork.create(genome, config)
            NETS.append(net)
            genome.fitness = 0

        max_fitness = 0

        # Generation loop
        running = True
        while running:
            CLOCK.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

            # Update stats
            stats['num_alive'] = len(CARS)
            draw(WINDOW, CARS, BACKGROUND_SURFACE, stats)

            # If there's no more car, new generation
            if len(CARS) == 0:
                break

            # Update fitness for each car
            winner_found = False
            for j, car in enumerate(CARS):
                alive_score = 1
                distance_reached_score = int(car.nearest_point_reached)
                safe_driving_score = car.average_distance_from_edges()
                win_score = 500

                # fitness score
                GE[j].fitness += alive_score + (distance_reached_score / 50) + (safe_driving_score / 10)

                # Update stats
                if GE[j].fitness > max_fitness:
                    max_fitness = GE[j].fitness

                # Save winner and go to next level
                if car.winner:
                    GE[j].fitness += win_score * (GAME_INFO.current_level + 1)
                    winner_found = True
                    WINNER_GENOME = GE[j]
                    save_trained_car(WINNER_GENOME)
                    next_level()
                    if GAME_INFO.mode == "SIMULATION":
                        car.winner = False
                    break

                if car.damaged:
                    remove(j)

            # Update stats
            stats['best_fitness'] = max_fitness
            stats['num_alive'] = len(CARS)
            draw(WINDOW, CARS, BACKGROUND_SURFACE, stats)

            # Start new generation
            if winner_found:
                break

            # Update car controls
            for j, car in enumerate(CARS):
                output = NETS[j].activate(car.data())
                if output[0] > 0.7:
                    car.controls.right = True
                    car.controls.left = False
                if output[1] > 0.7:
                    car.controls.left = True
                    car.controls.right = False
                if output[0] <= 0.7 and output[1] <= 0.7:
                    car.controls.right = False
                    car.controls.left = False
            for car in CARS:
                car.update(WINDOW, MAIN_FONT, TRACK_BORDER_MASK, FINISH_LINE_MASK, FINISH_POSITION)

        # Update stats end generation
        stats["generation"] = POP.generation
        stats["num_species"] = len(POP.species.species)


def validate_car():
    while GAME_INFO.current_level < len(LEVELS):

        # init level and car
        if GAME_INFO.current_level == GAME_INFO.n_training:
            load_level()
        VALIDATION_CAR = Car(4, 4, START_POSITION, PATH_POINTS, RED_CAR_IMG)

        # Inference loop
        running = True
        while running:
            CLOCK.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            draw(WINDOW, [VALIDATION_CAR], BACKGROUND_SURFACE)
            if VALIDATION_CAR.winner:
                next_level()
                break
            if VALIDATION_CAR.damaged:
                GAME_INFO.game_over_menu()
                break

            # update car controls using trained net
            output = TRAINED_NET.activate(VALIDATION_CAR.data())
            if output[0] > 0.7:
                VALIDATION_CAR.controls.right = True
                VALIDATION_CAR.controls.left = False
            if output[1] > 0.7:
                VALIDATION_CAR.controls.left = True
                VALIDATION_CAR.controls.right = False
            if output[0] <= 0.7 and output[1] <= 0.7:
                VALIDATION_CAR.controls.right = False
                VALIDATION_CAR.controls.left = False
            VALIDATION_CAR.update(WINDOW, MAIN_FONT, TRACK_BORDER_MASK, FINISH_LINE_MASK, FINISH_POSITION)


def remove(index):
    CARS.pop(index)
    GE.pop(index)
    NETS.pop(index)


def draw(win, car_list, surface, stats=None):
    win.blit(surface, (0, 0))
    for car in car_list:
        car.draw(win, True)
    if VALIDATION_CAR is not None:
        VALIDATION_CAR.draw(win, True)
    if stats:
        GAME_INFO.draw_statistics(stats)
    pygame.display.update()


def save_trained_car(genome, filename="trained_car.pkl"):
    with open(filename, 'wb') as file:
        pickle.dump(genome, file)


def load_trained_car(filename="trained_car.pkl"):
    with open(filename, 'rb') as file:
        return pickle.load(file)


def next_level():
    GAME_INFO.current_level += 1
    if GAME_INFO.mode == "TRAINING":
        if GAME_INFO.current_level < GAME_INFO.n_training:
            load_level()
    elif GAME_INFO.mode == "VALIDATION":
        if GAME_INFO.current_level >= (GAME_INFO.n_training + GAME_INFO.n_validation):
            GAME_INFO.victory_menu(CURRENT_GENERATION >= NUM_GENERATIONS - 1)
        else:
            load_level()
    elif GAME_INFO.mode == "SIMULATION":
        if GAME_INFO.current_level < (GAME_INFO.n_training + GAME_INFO.n_validation):
            load_level()


def load_level():
    global RED_CAR_IMG, LEVEL_LOADED, WINDOW, TRACK_BORDER_MASK, FINISH_LINE_MASK, FINISH_POSITION, START_POSITION, \
        PATH_POINTS, BACKGROUND_SURFACE

    if GAME_INFO.mode == "TRAINING" and GAME_INFO.n_training == 0:
        return
    if GAME_INFO.mode == "VALIDATION" and GAME_INFO.n_validation == 0:
        return

    # Carica le immagini per il livello corrente
    level_info = GAME_INFO.selected_levels[GAME_INFO.current_level]
    track = scale_image(pygame.image.load(level_info["track_img"]), 0.7)
    track_border = scale_image(pygame.image.load(level_info["border_img"]), 0.7)
    finish = scale_image(pygame.image.load(level_info["finish_img"]), 0.7)
    FINISH_POSITION = level_info["finish_position"]
    START_POSITION = level_info["start_position"]
    PATH_POINTS = level_info["path_points"]

    if level_info["track_img"] == "imgs/circuito_5.png":
        track = scale_image(pygame.image.load(level_info["track_img"]), 0.57)
        track_border = scale_image(pygame.image.load(level_info["border_img"]), 0.57)
        finish = scale_image(pygame.image.load(level_info["finish_img"]), 0.47)
        if not LEVEL_LOADED:
            width, height = track.get_width(), track.get_height()
            WINDOW = pygame.display.set_mode((width, height))
            BACKGROUND_SURFACE = pygame.Surface((width, height))
            RED_CAR_IMG = scale_image(pygame.image.load("imgs/red-car.png"), 0.4)
            LEVEL_LOADED = True
    else:
        if level_info["track_img"] == "imgs/track.png":
            track = scale_image(pygame.image.load(level_info["track_img"]), 0.9)
            track_border = scale_image(pygame.image.load(level_info["border_img"]), 0.9)
            finish = scale_image(pygame.image.load(level_info["finish_img"]), 1)
        if level_info["track_img"] == "imgs/circuito_3.png":
            finish = scale_image(pygame.image.load(level_info["finish_img"]), 0.8)
        if level_info["track_img"] == "imgs/circuito_4.png":
            track = scale_image(pygame.image.load(level_info["track_img"]), 0.67)
            track_border = scale_image(pygame.image.load(level_info["border_img"]), 0.67)
            finish = scale_image(pygame.image.load(level_info["finish_img"]), 0.57)
        if LEVEL_LOADED:
            width, height = track.get_width(), track.get_height()
            WINDOW = pygame.display.set_mode((width, height))
            BACKGROUND_SURFACE = pygame.Surface((width, height))
            RED_CAR_IMG = scale_image(pygame.image.load("imgs/red-car.png"), 0.53)
            LEVEL_LOADED = False

    # Aggiorna le maschere
    TRACK_BORDER_MASK = pygame.mask.from_surface(track_border)
    FINISH_LINE_MASK = pygame.mask.from_surface(finish)

    imgs = [
        (GRASS_IMG, (0, 0)),
        (track, (0, 0)),
        (finish, FINISH_POSITION),
        (track_border, (0, 0))
    ]
    for img, pos in imgs:
        BACKGROUND_SURFACE.blit(img, pos)


def capture_points():
    GAME_INFO.current_level = 0
    load_level()
    points = []

    # Capture loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Save click coordinates and draw a red dot
                pos = pygame.mouse.get_pos()
                points.append(pos)
                pygame.draw.circle(WINDOW, (255, 0, 0), pos, 5)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z and (pygame.key.get_mods() & pygame.KMOD_CTRL):
                    # Remove point when Ctrl+Z is pressed
                    if points:
                        points.pop()
        WINDOW.blit(BACKGROUND_SURFACE, (0, 0))
        for point in points:
            pygame.draw.circle(WINDOW, (255, 0, 0), point, 5)
        pygame.display.update()

    # Print coordinate array
    print("")
    print(points)
    print("")
    pygame.quit()


def load_saved_levels():
    try:
        with open('saved_levels.pkl', 'rb') as f:
            saved_config = pickle.load(f)
            GAME_INFO.selected_tracks = saved_config["selected_tracks"] if "selected_tracks" in saved_config else [0, 1,
                                                                                                                   2]
            GAME_INFO.n_training = saved_config["n_training"] if "n_training" in saved_config else 3
            GAME_INFO.n_validation = saved_config["n_validation"] if "n_validation" in saved_config else 0
    except FileNotFoundError:
        GAME_INFO.selected_tracks = [0, 1, 2]
        GAME_INFO.n_training = 3
        GAME_INFO.n_validation = 0

    GAME_INFO.selected_levels.clear()
    for level_idx in GAME_INFO.selected_tracks:
        GAME_INFO.selected_levels.append(LEVELS[level_idx])


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
        WINDOW.blit(text_surf, text_rect)
        pygame.display.update()


def run(config):
    global POP, TRAINED_NET

    # Load NEAT configs
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config
    )

    if GAME_INFO.mode == "TRAINING":
        POP = neat.Population(config)
        POP.add_reporter(neat.StdOutReporter(True))
        stats = neat.StatisticsReporter()
        POP.add_reporter(stats)

        winner = POP.run(eval_genomes, NUM_GENERATIONS)

        print('\nDrawing Best genome:\n{!s}'.format(winner))

        print("\nDrawing plots\n")
        plot_single_fitness(stats.get_fitness_mean(), "Andamento Fitness Media", "fitness_media")
        plot_single_fitness(stats.get_fitness_stat(max), "Andamento Fitness Migliore", "fitness_best")

    elif GAME_INFO.mode == "VALIDATION":
        TRAINED_NET = neat.nn.FeedForwardNetwork.create(WINNER_GENOME, config)
        validate_car()


def run_simulation(mutation_rate, num_pop, max_generations, simulation_idx):
    global POP

    # Dinamic setting of config.txt
    temp_config_path = create_simulation_config(mutation_rate, num_pop, simulation_idx)

    # NEAT config
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         temp_config_path)
    POP = neat.Population(config)
    POP.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    POP.add_reporter(stats)

    POP.run(eval_genomes, max_generations)

    # Plot data
    mean_fitness_data = stats.get_fitness_mean()
    best_fitness_data = stats.get_fitness_stat(max)

    os.remove(temp_config_path)
    return mean_fitness_data, best_fitness_data


def create_simulation_config(mutation_rate, num_cars, simulation_idx, base_config_path='config.txt'):
    global CURRENT_MUTATION_RATE, CURRENT_NUM_CARS, CURRENT_SIMULATION_NUM

    # read default config.txt
    with open(base_config_path, 'r') as file:
        config_content = file.read()

    # update config with simulation parameters
    config_content = re.sub(r'pop_size\s*=\s*\d+', f'pop_size = {num_cars}', config_content)
    config_content = re.sub(r'weight_mutate_rate\s*=\s*[\d.]+', f'weight_mutate_rate = {mutation_rate}', config_content)

    # Update global variables
    CURRENT_MUTATION_RATE = mutation_rate
    CURRENT_NUM_CARS = num_cars
    CURRENT_SIMULATION_NUM = simulation_idx

    # create tmp config file
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


def init_window(width, height):
    global MAIN_FONT, GAME_INFO, WINDOW
    pygame.display.set_caption(WINDOW_TITLE)
    MAIN_FONT = pygame.font.SysFont("comicsans", 44)
    WINDOW = pygame.display.set_mode((width, height))
    GAME_INFO = GameInfo(WINDOW, width, height)


# ------------------------------------------------------ MAIN --------------------------------------------------------


def main_menu():
    menu_options = [
        "Allenamento",
        "Validazione",
        "Simulazione",
        "Modifica percorsi",
        "Cattura punti"
    ]

    title = "AI Car Simulation"

    # Load levels
    load_saved_levels()
    LOADED_TRACKS.clear()
    for level in LEVELS:
        img = pygame.image.load(level["track_img"])
        img = pygame.transform.scale(img, (100, 100))
        LOADED_TRACKS.append(img)

    # Main menu loop
    running = True
    while running:
        if GAME_INFO.track_config_changed:
            load_saved_levels()
            GAME_INFO.track_config_changed = False

        GAME_INFO.draw_menu(menu_options, title)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = pygame.mouse.get_pos()
                if 200 <= y <= 240:
                    if GAME_INFO.n_training <= 0:
                        show_popup_message("Select at least one training track", 2)
                    else:
                        GAME_INFO.mode = "TRAINING"
                        running = False
                elif 260 <= y <= 300:
                    if GAME_INFO.n_validation <= 0:
                        show_popup_message("Select at least one validation track", 2)
                    else:
                        GAME_INFO.mode = "VALIDATION"
                        running = False
                elif 320 <= y <= 360:
                    GAME_INFO.mode = "SIMULATION"
                    running = False
                elif 380 <= y <= 420:
                    GAME_INFO.track_selection_menu(LEVELS, LOADED_TRACKS)
                elif 440 <= y <= 480:
                    GAME_INFO.mode = "CAPTURE_POINTS"
                    GAME_INFO.current_level = 3
                    running = False

        if GAME_INFO.mode == "TRAINING":
            GAME_INFO.current_level = 0
        elif GAME_INFO.mode == "VALIDATION":
            GAME_INFO.current_level = GAME_INFO.n_training


if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    init_window(WIDTH, HEIGHT)
    main_menu()
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')

    if GAME_INFO.mode == "SIMULATION":
        mutation_rates = [0.1, 0.3, 0.5, 0.7, 0.9]
        pop_density = [10, 20, 30, 50, 100]
        base_rate = 0.8
        base_density = 30
        num_simulations = 3
        generations = 10

        def average(fitness_lists):
            # Calculate average fitness for each generation
            media_fitness = [sum(valori) / len(valori) for valori in zip(*fitness_lists)]
            return media_fitness

        def reset_simulation():
            GAME_INFO.current_level = 0
            load_level()

        # Run simulation with different values of weight_mutate_rate
        plt.figure()
        fitness_data_mutation_mean = {}
        fitness_data_mutation_best = {}
        for rate in mutation_rates:
            all_data_mean = []
            all_data_best = []
            for i in range(num_simulations):
                reset_simulation()
                mean_fitness, best_fitness = run_simulation(rate, base_density, generations, i)
                all_data_mean.append(mean_fitness)
                all_data_best.append(best_fitness)
            fitness_data_mutation_mean[f"Mutation rate {rate}"] = average(all_data_mean)
            fitness_data_mutation_best[f"Mutation rate {rate}"] = average(all_data_best)

        plot_fitness_over_generations(fitness_data_mutation_mean, "Andamento Fitness Media per Tasso di Mutazione",
                                      "fitness_media_tasso_mutazione")
        plot_fitness_over_generations(fitness_data_mutation_best, "Andamento Best Fitness per Tasso di Mutazione",
                                      "best_fitness_tasso_mutazione")

        # Run simulation with different values of pop_size
        fitness_data_density_mean = {}
        fitness_data_density_best = {}
        for density in pop_density:
            all_data_mean = []
            all_data_best = []
            for i in range(num_simulations):
                reset_simulation()
                mean_fitness, best_fitness = run_simulation(base_rate, density, generations, i)
                all_data_mean.append(mean_fitness)
                all_data_best.append(best_fitness)
            fitness_data_density_mean[f"Pop Density {density}"] = average(all_data_mean)
            fitness_data_density_best[f"Pop Density {density}"] = average(all_data_best)

        plot_fitness_over_generations(fitness_data_density_mean, "Andamento Fitness Media per Numero di Macchine",
                                      "fitness_media_numero_macchine")
        plot_fitness_over_generations(fitness_data_density_best, "Andamento Best Fitness per Numero di Macchine",
                                      "best_fitness_numero_macchine")
    elif GAME_INFO.mode == "TRAINING":
        run(config_path)
    elif GAME_INFO.mode == "VALIDATION":
        WINNER_GENOME = load_trained_car()
        run(config_path)
    elif GAME_INFO.mode == "CAPTURE_POINTS":
        capture_points()

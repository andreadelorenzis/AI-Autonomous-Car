import pygame
import sys
import pickle

class GameInfo:

    def __init__(self, win, screen_width, screen_height):
        self.win = win
        self.current_level = 0
        self.mode = "TRAINING"
        self.winner_genome = None
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.n_training = 3
        self.n_validation = 0
        self.track_config_changed = False
        self.selected_tracks = []
        self.selected_levels = []
        self.selected_square = 0


    def draw_statistics(self, stats):
        font = pygame.font.SysFont("comicsans", 20)
        x, y = 10, 10  # Imposta le coordinate in alto a sinistra

        info_texts = [
            f"Generations: {stats['generation']}",
            f"Best fitness: {stats['best_fitness']:.2f}",
            f"Species: {stats['num_species']}",
            f"Alive: {stats['num_alive']}"
        ]

        for text in info_texts:
            render = font.render(text, True, (255, 255, 255))
            self.win.blit(render, (x, y))
            y += 25

        pygame.display.update()

    def victory_menu(self):
        running = True
        while running:
            buttons = self.draw_victory_menu(self.win)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    # Accedi al rettangolo del pulsante dalla tupla
                    if "save" in buttons and buttons["save"][1].collidepoint((mouse_x, mouse_y)) and self.mode == "TRAINING":
                        self.save_trained_car(self.winner_genome)
                        print("Macchina salvata")
                        running = False
        pygame.quit()
        sys.exit()

    def draw_victory_menu(self, win):
        win.fill((0, 0, 0))  # Sfondo nero
        font = pygame.font.SysFont("comicsans", 60)
        button_font = pygame.font.SysFont("comicsans", 40)

        victory_text = font.render("VITTORIA!", True, (255, 255, 255))
        win.blit(victory_text, (self.screen_width // 2 - victory_text.get_width() // 2, 100))

        buttons = {}
        if self.mode == "TRAINING":
            buttons["save"] = ("Salva macchina", pygame.Rect(self.screen_width // 2 - 150, 300, 300, 50))

        mouse_x, mouse_y = pygame.mouse.get_pos()

        for key, (text, rect) in buttons.items():
            text_color = (255, 255, 0) if rect.collidepoint((mouse_x, mouse_y)) else (255, 255, 255)
            text_surf = button_font.render(text, True, text_color)
            win.blit(text_surf, (rect.x + (rect.width - text_surf.get_width()) // 2, rect.y + (rect.height - text_surf.get_height()) // 2))
            pygame.draw.line(win, text_color, (rect.left, rect.bottom + 3), (rect.right, rect.bottom + 3), 2)

        pygame.display.update()
        return buttons

    def save_trained_car(self, genome, filename="trained_car.pkl"):
        with open(filename, 'wb') as file:
            pickle.dump(genome, file)

    def draw_menu(self, menu_options, title):
        self.win.fill((0, 0, 0))  # Sfondo nero
        title_font = pygame.font.SysFont("comicsans", 60)
        option_font = pygame.font.SysFont("comicsans", 40)

        mouse_x, mouse_y = pygame.mouse.get_pos()

        # Disegna il titolo
        title_surf = title_font.render(title, True, (255, 255, 255))
        title_rect = title_surf.get_rect(center=(self.screen_width // 2, 100))
        self.win.blit(title_surf, title_rect)

        # Disegna le opzioni del menu
        for i, option in enumerate(menu_options):
            text_surf = option_font.render(option, True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=(self.screen_width // 2, 200 + i * 60))

            # Cambia il colore del testo se il mouse è sopra l'opzione
            if text_rect.collidepoint((mouse_x, mouse_y)):
                text_surf = option_font.render(option, True, (255, 255, 0))  # Cambia il colore in giallo

            self.win.blit(text_surf, text_rect)

            # Disegna la linea di sottolineatura
            pygame.draw.line(self.win, (255, 255, 255), (text_rect.left, text_rect.bottom + 3), (text_rect.right, text_rect.bottom + 3), 2)

        pygame.display.update()


    def game_over_menu(self):
        self.draw_game_over_menu()
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    running = False
        pygame.quit()
        sys.exit()

    def draw_game_over_menu(self):
        self.win.fill((0, 0, 0))  # Sfondo nero
        font = pygame.font.SysFont("comicsans", 60)

        game_over_text = font.render("GAME OVER", True, (255, 0, 0))
        self.win.blit(game_over_text, (self.screen_width // 2 - game_over_text.get_width() // 2, self.screen_height // 2 - game_over_text.get_height() // 2))

        pygame.display.update()

    def track_selection_menu(self, levels, loaded_tracks):
        square_size = 100
        square_y = 150
        track_y = 300
        square_gap = 10
        total_squares = self.n_training + self.n_validation
        square_size = 100
        total_width = total_squares * square_size + (total_squares - 1) * 10
        window_width = self.win.get_width()
        start_x = (window_width - total_width) // 2

        control_center_x = window_width // 2
        control_y = 50

        minus_training = None
        plus_training = None
        minus_validation = None
        plus_validation = None
        save_button_rect = None
        back_button_rect = None

        running = True
        while running:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = event.pos

                    # Gestione click sui quadrati colorati
                    for i in range(self.n_training + self.n_validation):
                        square_x = start_x + i * (square_size + square_gap)
                        if square_x <= mouse_x <= square_x + square_size and square_y <= mouse_y <= square_y + square_size:
                            self.selected_square = i
                            if i < len(self.selected_tracks) and self.selected_tracks[i] is not None:
                                self.selected_tracks.pop(i)
                                break

                    # Gestione click sulle immagini dei percorsi
                    for i in range(len(levels)):
                        track_x = start_x + i * (square_size + square_gap)
                        if track_x <= mouse_x <= track_x + square_size and track_y <= mouse_y <= track_y + square_size:
                            if i not in self.selected_tracks:
                                self.selected_tracks.append(i)
                                break

                    # Gestione click pulsanti n_training
                    if minus_training.collidepoint((mouse_x, mouse_y)):
                        if self.n_training + self.n_validation > 0:
                            self.decrease_training()
                    if plus_training.collidepoint((mouse_x, mouse_y)):
                        if self.n_training + self.n_validation < 6:
                            self.increase_training()

                    # Gestione click su pulsanti n_validation
                    if minus_validation.collidepoint((mouse_x, mouse_y)):
                        if self.n_training + self.n_validation > 0:
                            self.decrease_validation()
                    if plus_validation.collidepoint((mouse_x, mouse_y)):
                        if self.n_training + self.n_validation < 6:
                            self.increase_validation()

                    # Gestione click pulsanti save e back
                    if save_button_rect and save_button_rect.collidepoint(mouse_x, mouse_y):
                        self.save_levels()
                        self.track_config_changed = True
                        print("Configuration Saved")
                        running = False
                    if back_button_rect and back_button_rect.collidepoint(mouse_x, mouse_y):
                        running = False

            self.draw_track_selection_menu(self.win, loaded_tracks)

            minus_training, plus_training = self.draw_buttons(self.win, control_center_x - 150, control_y, f"Training: {self.n_training}")
            minus_validation, plus_validation = self.draw_buttons(self.win, control_center_x + 50, control_y, f"Validation: {self.n_validation}")

            # Calcola la posizione dei pulsanti
            button_width = 100
            save_button_x = self.win.get_width() // 2 - button_width
            back_button_x = self.win.get_width() // 2 + 20

            # Disegna i pulsanti
            save_button_rect = self.draw_button(self.win, save_button_x, self.win.get_height() - 40, "Save", (0, 255, 0))
            back_button_rect = self.draw_button(self.win, back_button_x, self.win.get_height() - 40, "Back to Menu", (255, 0, 0))
            pygame.display.update()

    def decrease_training(self):
        if self.n_training > 0:
            self.n_training -= 1

    def increase_training(self):
        self.n_training += 1

    def decrease_validation(self):
        if self.n_validation > 0:
            self.n_validation -= 1

    def increase_validation(self):
        self.n_validation += 1

    def save_levels(self):
        config_to_save = {
            "selected_tracks": self.selected_tracks,
            "n_training": self.n_training,
            "n_validation": self.n_validation
        }
        print(config_to_save)
        with open('saved_levels.pkl', 'wb') as f:
            pickle.dump(config_to_save, f)

    def draw_button(self, win, x, y, text, background_color, text_color=(255, 255, 255)):
        font = pygame.font.SysFont(None, 30)
        button_text = font.render(text, True, text_color)
        text_rect = button_text.get_rect(center=(x, y))
        background_rect = pygame.Rect(text_rect.left - 10, text_rect.top - 10,
                                      text_rect.width + 20, text_rect.height + 20)
        pygame.draw.rect(win, background_color, background_rect)
        win.blit(button_text, text_rect)

        return background_rect

    def draw_buttons(self, win, x, y, text):
        font = pygame.font.SysFont(None, 30)
        text_surf = font.render(text, True, (255, 255, 255))
        win.blit(text_surf, (x, y))

        minus_button = pygame.Rect(x - 30, y, 20, 20)
        plus_button = pygame.Rect(x + text_surf.get_width() + 10, y, 20, 20)
        pygame.draw.rect(win, (100, 100, 100), minus_button)
        pygame.draw.rect(win, (100, 100, 100), plus_button)

        minus_text = font.render("-", True, (255, 255, 255))
        plus_text = font.render("+", True, (255, 255, 255))
        win.blit(minus_text, (minus_button.x + 5, minus_button.y))
        win.blit(plus_text, (plus_button.x + 5, plus_button.y))

        return minus_button, plus_button

    def draw_track_selection_menu(self, win, loaded_tracks):
        win.fill((0, 0, 0))
        window_width = win.get_width()
        total_squares = self.n_training + self.n_validation
        square_size = 100
        total_width = total_squares * square_size + (total_squares - 1) * 10
        start_x = 50
        square_y = 150
        track_y = 300

        # Disegna i quadrati colorati
        for i in range(total_squares):
            color = (255, 0, 0) if i < self.n_training else (0, 255, 0)
            rect = pygame.Rect(start_x + i * (square_size + 10), square_y, square_size, square_size)
            pygame.draw.rect(win, color, rect)

            # Se un percorso è selezionato per questo quadrato, disegnalo
            if i < len(self.selected_tracks):
                img_rect = loaded_tracks[self.selected_tracks[i]].get_rect(center=rect.center)
                win.blit(loaded_tracks[self.selected_tracks[i]], img_rect)

        # Disegna le immagini dei percorsi in orizzontale con sfondo bianco
        for i, track_image in enumerate(loaded_tracks):
            x = start_x + i * (square_size + 10)
            rect = pygame.Rect(x, track_y, square_size, square_size)
            pygame.draw.rect(win, (255, 255, 255), rect)
            img_rect = track_image.get_rect(center=rect.center)
            win.blit(track_image, img_rect)

            # Se il percorso è già selezionato, rendilo opaco
            if i in self.selected_tracks:
                s = pygame.Surface((square_size, square_size))
                s.set_alpha(128)
                s.fill((255, 255, 255))
                win.blit(s, (x, track_y))

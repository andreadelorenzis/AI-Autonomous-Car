import math
import pygame
from utils import lerp

class Sensor:
    def __init__(self, car):
        self.car = car
        self.ray_count = 6
        self.ray_length = 200
        self.ray_spread = 2.79
        self.rays = []
        self.readings = []
        self.last_car_angle = None
        self.last_car_pos = None

    def update(self, pos, mask):
        # Calcola i raggi solo se l'auto si è mossa o ruotata
        if self.last_car_pos != pos or self.last_car_angle != self.car.angle:
            self.cast_rays(pos)
            self.last_car_pos = pos
            self.last_car_angle = self.car.angle

        self.readings = []
        for ray in self.rays:
            result = self.get_reading(ray, mask)
            if result is not None:
                reading, distance = result
                self.readings.append((reading, distance))
            else:
                self.readings.append(None)

    def cast_rays(self, pos):
        self.rays = []
        for i in range(self.ray_count):
            # Calcolo l'angolo del raggio
            ray_angle = lerp(
                self.ray_spread/2,
                -self.ray_spread/2,
                0.5 if self.ray_count == 1 else i / (self.ray_count-1)
            ) + math.radians(self.car.angle)
            start = (pos[0], pos[1])
            end = (pos[0] - math.sin(ray_angle) * self.ray_length,
                   pos[1] - math.cos(ray_angle) * self.ray_length)
            self.rays.append([start, end])

    def get_reading(self, ray, mask):
        start, end = ray
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        distance = math.hypot(dx, dy)
        steps = int(distance)
        dx /= steps
        dy /= steps

        mask_width, mask_height = mask.get_size()

        for i in range(steps):
            x = int(start[0] + dx * i)
            y = int(start[1] + dy * i)

            # Verifica che (x, y) sia all'interno dei limiti della maschera
            if 0 <= x < mask_width and 0 <= y < mask_height:
                if mask.get_at((x, y)):
                    return (x, y), i  # Punto di intersezione e distanza
            else:
                break

        return None  # Nessuna intersezione trovata

    def draw(self, win):
        for i, ray in enumerate(self.rays):
            start = ray[0]
            end = ray[1]
            if self.readings[i] is not None:
                end = self.readings[i][0]
                pygame.draw.circle(win, (255, 0, 0), end, 5)
            pygame.draw.line(win, (169, 10, 255), start, end)

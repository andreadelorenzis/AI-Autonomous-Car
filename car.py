import numpy as np
from utils import *
from sensor import Sensor
from controls import Controls

class Car(pygame.sprite.Sprite):

    def __init__(self, max_vel, rotation_vel, start_pos, path_points, img):
        super().__init__()
        self.image = img
        self.rect = self.image.get_rect(center=start_pos)
        self.velocity = pygame.math.Vector2(0, max_vel)
        self.direction = pygame.math.Vector2(0, 1)
        self.img = img
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.friction = 0.05
        self.x, self.y = start_pos
        self.width, self.height = img.get_width(), img.get_height()
        self.acceleration = 0.1
        self.sensor = Sensor(self)
        self.controls = Controls()
        self.sensor_x, self.sensor_y = self.x + self.width / 2, self.y
        self.prediction_interval = 1000
        self.last_prediction_time = pygame.time.get_ticks()
        self.damaged = False
        self.nearest_point_reached = 0
        self.car_mask = pygame.mask.from_surface(img)
        self.controls.forward = True
        self.winner = False
        self.start_pos = start_pos
        self.path_points = path_points

    def update(self, win, font, border_mask, finish_mask, finish_position):
        self.sensor.readings.clear()
        self.move()
        self.damaged = self.handle_collision(win, font, border_mask,
                                             finish_mask, finish_position)
        self.update_nearest_point_reached(self.path_points)

        # update sensors
        car_center = self.rect.center
        muso_rel_pos = (0, -self.height / 2)
        muso_abs_pos = rotate_around_point(car_center, muso_rel_pos, -self.angle)

        self.sensor.update(muso_abs_pos, border_mask)

    def draw(self, win, draw_sensor=False):
        if self.damaged:
            self.image = apply_gray_filter(self.image)
        win.blit(self.image, self.rect)

        # draw sensors
        if self.sensor is not None and draw_sensor and not self.damaged:
            self.sensor.draw(win)

    def move(self):
        if self.controls.forward:
            self.vel = min(self.vel + self.acceleration, self.max_vel)
        if self.controls.backward:
            self.vel = max(self.vel - self.acceleration, -self.max_vel / 2)

        if self.vel > 0:
            self.vel -= self.friction
        if self.vel < 0:
            self.vel += self.friction
        if abs(self.vel) < self.friction:
            self.vel = 0

        if self.controls.left:
            self.angle += self.rotation_vel
        if self.controls.right:
            self.angle -= self.rotation_vel

        self.image = pygame.transform.rotate(self.img, self.angle)
        self.rect = self.image.get_rect(center=self.rect.center)

        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.rect.y -= vertical
        self.rect.x -= horizontal

    def calculate_collision(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.image)
        offset = (int(self.rect.x - x), int(self.rect.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def handle_collision(self, win, font, border_mask, finish_mask, finish_position):
        if self.calculate_collision(border_mask) != None:
            return True

        finish_poi_collide = self.calculate_collision(finish_mask, *finish_position)
        if finish_poi_collide != None:
            if finish_poi_collide[1] == 0:
                return True
            else:
                self.winner = True

        return False

    def update_nearest_point_reached(self, path_points):
        current_pos = (self.rect.x, self.rect.y)
        distances = [math.sqrt((p[0] - current_pos[0])**2 + (p[1] - current_pos[1])**2) for p in path_points]
        nearest_point_index = np.argmin(distances)
        if nearest_point_index > self.nearest_point_reached:
            self.nearest_point_reached = nearest_point_index

    def average_distance_from_edges(self):
        if self.sensor.readings:
            readings = self.sensor.readings
            default_distance = self.sensor.ray_length
            readings = [default_distance if reading is None else reading[1] for reading in readings]
            average_distance = sum(readings) / len(readings)
            normalized_distance_score = average_distance / default_distance
            return normalized_distance_score
        else:
            return 0

    def data(self):
        readings = [0, 0, 0, 0, 0, 0]
        if self.sensor.readings:
            readings = self.sensor.readings
            default_distance = self.sensor.ray_length
            readings = [default_distance if reading is None else reading[1] for reading in readings]
        return readings

    def reset(self):
        self.rect.x, self.rect.y = self.start_pos
        self.angle = 0
        self.vel = 0
        self.damaged = False

import math

import pygame


def scale_image(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)


def blit_rotate_center(win, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(
        center=image.get_rect(topleft=top_left).center)
    win.blit(rotated_image, new_rect.topleft)


def get_rotated_image(image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=top_left).center)
    return rotated_image, new_rect


def blit_text_center(win, font, text):
    render = font.render(text, 1, (200, 200, 200))
    win.blit(render, (win.get_width()/2 - render.get_width() /
                      2, win.get_height()/2 - render.get_height()/2))


'''
Linear interpolation: calculates an intermediate value between two numbers A and B based on a 
parameter t, which determines the position of the interpolated value between A and B. For example:
    t=0 -> A
    t=1 -> B
    A=10, B=20, t=0.5 -> 15
'''
def lerp(A, B, t):
    return A + (B - A) * t


def rotate_around_point(center, relative_point, angle):
    angle_rad = math.radians(angle)

    cos_theta = math.cos(angle_rad)
    sin_theta = math.sin(angle_rad)

    # Rotate relative point
    rotated_x = relative_point[0] * cos_theta - relative_point[1] * sin_theta
    rotated_y = relative_point[0] * sin_theta + relative_point[1] * cos_theta

    # Translate into absolute position
    final_x = rotated_x + center[0]
    final_y = rotated_y + center[1]

    return final_x, final_y


def apply_gray_filter(image):
    # Create image with gray filter
    grayscale_img = pygame.Surface(image.get_size())
    grayscale_img.fill((128, 128, 128))  # Riempimento con grigio
    grayscale_img.blit(image, (0, 0), special_flags=pygame.BLEND_RGB_MULT)
    return grayscale_img


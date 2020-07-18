# coding=utf-8

import pygame


class MyChar(pygame.sprite.Sprite):
    def __init__(self, targetscreen, width, height, color=(255, 0, 0)):
        super(MyChar, self).__init__()
        self.rect = pygame.Rect(0, 0, width, height)
        self.target = targetscreen
        self.color = color

    def moveto(self, x, y):
        self.rect.left = x
        self.rect.top = y

    def move(self, x, y):
        self.rect.left += x
        self.rect.top += y

    def update(self, *args, **kwargs):
        pygame.draw.rect(self.target, self.color, self.rect)

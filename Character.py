# coding=utf-8

import pygame
import Configuration


class MyChar(pygame.sprite.Sprite):
    def __init__(self, targetscreen, width, height, color=(255, 0, 0)):
        super(MyChar, self).__init__()
        self.rect = pygame.Rect(0, 0, width, height)
        self.target = targetscreen
        self.color = color
        self.font = pygame.font.Font(Configuration.Font, 15)

    def moveto(self, x, y):
        self.rect.left = x
        self.rect.top = y

    def move(self, x, y):
        self.rect.left += x
        self.rect.top += y

    def update(self, *args, **kwargs):
        pygame.draw.rect(self.target, self.color, self.rect)
        if 'text' in kwargs.keys():
            self.target.blit(self.font.render(kwargs['text'], True, (255, 255, 255)), self.rect.topleft)

# coding=utf-8
import math

import pygame
from random import randint
from Character import MyChar
import time


class Enemy(MyChar):
    def __init__(self, targetscreen, width, height, color=(0, 0, 255), moveper=20, movespeed=10, distanse=50):
        super().__init__(targetscreen, width, height, color)
        if randint(0, 1):  # 随机从左上角或右上角出现
            self.rect.right = targetscreen.get_rect()[2]
        self.targetx = self.rect.left
        self.targety = self.rect.top
        self.moving = False
        self.moveper = moveper
        self.movespeed = movespeed  # 移动速度越小越快
        self.distanse = distanse  # 随机移动到玩家的最大距离（越大玩家越安全）
        self.movetimes = 0
        self.endmoveper = 40
        self.sleeptime = 0.5
        self.lastsleeptime = time.time()
        self.lives = 5  # 生命数

    def checkskilled(self):
        player = self.groups()[0].player
        sx, sy = player.skillingposition
        srange = player.skillrange
        x, y = self.rect.midbottom[0], self.rect.midleft[1]
        square_sum = (sx - x) ** 2 + (sy - y) ** 2
        if square_sum < srange ** 2:  # 在技能范围内
            effect = player.skilleffect
            distance = math.sqrt(square_sum)
            cos = distance / ((x - sx) or 0.001)
            sin = distance / ((y - sy) or 0.001)
            self.targetx, self.targety = (effect * cos + x, effect * sin + y)
            self.moving = True

    def summonpoint(self):
        # 玩家的坐标
        x = self.groups()[0].player.rect.x
        y = self.groups()[0].player.rect.y
        self.targetx = randint(-self.distanse, self.distanse) + x
        self.targety = randint(-self.distanse, self.distanse) + y
        self.moving = True
        self.movetimes += 1

    def move(self, x, y):
        super(Enemy, self).move(x, y)
        a, b, sw, sh = self.target.get_rect()
        # 防止超出边缘
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, sw)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, sh)

    def moveto(self, x, y):
        self.moving = True
        self.targetx, self.targety = x, y

    def update(self, *args, **kwargs):
        super(Enemy, self).update()
        self.moveper = self.groups()[0].moveper  # 根据Controller.py改变移动概率
        self.movespeed = max((self.endmoveper - self.moveper) // 5, 0.1)
        if randint(0, 100) < self.moveper and (
                (time.time() - self.lastsleeptime) > self.sleeptime):
            self.summonpoint()
            self.lastsleeptime = time.time()
        else:
            self.checkskilled()
        self.smoothmove()

    def smoothmove(self):
        xrest = self.targetx - self.rect.left
        yrest = self.targety - self.rect.top
        changex = xrest // self.movespeed or bool(xrest)
        changey = yrest // self.movespeed or bool(yrest)
        xrest -= changex
        yrest -= changey
        self.move(changex, changey)
        if 3 > abs(changey) and 3 > abs(changex):
            self.moving = False

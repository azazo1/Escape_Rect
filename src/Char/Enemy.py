# coding=utf-8
import math
import random
from random import randint

from src.Basic import Base, Configuration
from src.Char.Character import MyChar


class Enemy(MyChar):
    def __init__(self, targetscreen, width, height, color=(0, 0, 255)):
        super().__init__(targetscreen, width, height, color)
        if randint(0, 1):  # 随机从左上角或右上角出现
            self.rect.right = targetscreen.get_rect()[2]
        self.distanse = (self.target.get_rect().height + self.target.get_rect().width) // 2 \
                        * 0.2  # 随机移动到玩家的最大距离（越大玩家越安全）
        self.movetimes = 0
        self.maxSleepTime = 1000  # 移动最大休息时间
        self.sleeptime = random.randint(0, self.maxSleepTime)
        self.lives = 10  # 生命数
        self.moving = False
        self.lastMoveTime = 0
        self.movingTime = 700  # 移动持续时间
        self.moveArc = (self.rect.center, self.rect.center)  # 移动路径

    def checkSkilled(self):
        player = self.groups()[0].player
        sx, sy = player.skillingposition
        srange = player.skillrange
        x, y = self.rect.center
        square_sum = (sx - x) ** 2 + (sy - y) ** 2
        if square_sum < srange ** 2:  # 在技能范围内
            effect = player.skilleffect
            distance = math.sqrt(square_sum)
            cos = distance / ((x - sx) or 0.001)
            sin = distance / ((y - sy) or 0.001)
            self.smoothTo(effect * cos + x, effect * sin + y)

    def summonPoint(self, hit=None):
        if hit:
            d = 0  # 不会移到玩家以外的地方
        else:
            d = int(self.distanse)
        x, y = self.groups()[0].player.rect.center
        targetx = randint(-d, d) + x
        targety = randint(-d, d) + y
        self.smoothTo(targetx, targety)

    def moveto(self, x, y):
        super(Enemy, self).moveto(x, y)
        a, b, sw, sh = self.target.get_rect()
        # 防止超出边缘
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, sw)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, sh)

    def move(self, x, y):
        super(Enemy, self).move(x, y)
        a, b, sw, sh = self.target.get_rect()
        # 防止超出边缘
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, sw)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, sh)

    def smoothTo(self, x, y):
        self.moving = True
        self.moveArc = self.rect.center, (x, y)
        self.lastMoveTime = Base.getTimeMil()

    def update(self, *args, **kwargs):
        self.movingTime = max(-0.04 * Base.getTimeMil() + 2000,
                              150)  # 随时间增加movingTime越小，最小为500
        super(Enemy, self).update(text=f'{self.sleeptime} {self.movingTime:.0f}' if Configuration.EnemySleepTimeShowing else '')
        if randint(0, 1000) < 30 and (
                (Base.getTimeMil() - self.lastMoveTime) > self.sleeptime) and not self.moving:
            self.summonPoint()
            self.movetimes += 1
        else:
            self.checkSkilled()
        self.smoothmove()

    def smoothmove(self):
        if self.moving:
            nowTime = Base.getTimeMil()
            process = max(((nowTime - self.lastMoveTime) / self.movingTime) ** 0.3, 0.01)  # 冲刺进度
            start, end = self.moveArc
            # 计算坐标
            nowPos = [(e - s) * process + s for s, e in zip(start, end)]
            # 使中点落在目标位置上
            nowPos[0] -= self.rect.width // 2
            nowPos[1] -= self.rect.height // 2
            self.moveto(*nowPos)
            if process >= 1:
                self.moving = False

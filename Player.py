# coding=utf-8
import random

import Base
import pygame

from Character import MyChar


class Particle(MyChar):
    def __init__(self, targetscreen, position, target_position, width=2, height=2, color=(255, 255, 0)):
        super().__init__(targetscreen, width, height, color)
        self.rect.center = position
        self.tp = target_position
        self.living = True
        self.speed = 5  # 越大越慢

    def update(self, *args, **kwargs):
        move_x = int((self.tp[0] - self.rect.centerx) / self.speed)
        move_y = int((self.tp[1] - self.rect.centery) / self.speed)
        self.rect.centerx += move_x
        self.rect.centery += move_y
        super(Particle, self).update()
        if abs(self.rect.centerx - self.tp[0]) <= self.speed and abs(
                self.rect.centery - self.tp[1]) <= self.speed:
            self.living = False


class ParticlesGroup:
    def __init__(self, parts: list = None):
        if not parts:
            parts = []
        self.parts = parts

    def update(self):
        for p in self.parts:
            if not p.living:
                self.parts.remove(p)
                continue
            p.update()

    def add(self, p: Particle):
        self.parts.append(p)


class Player(MyChar):
    def __init__(self, targetscreen, width, height, color=(255, 0, 0)):
        super(Player, self).__init__(targetscreen, width, height, color)
        x, y = self.target.get_rect()[2:]  # 将玩家安放在屏幕中间
        self.moveto(x / 2, y)
        self.changeX, self.changeY = 0, 0
        self.jumpsize = self.target.get_rect()[3] / 2
        self.jumprest = 0
        self.jumping = False
        self.jumpspeed = 3  # 越小越快
        self.jumpmaxtimes = 10  # 空中跳的次数(地面上也有一次)
        self.jumptimes = 0
        self.lives = self.olives = 5  # 生命数
        self.lastHurtTime = 0
        self.undeadabletime = 5000  # 无敌时间
        self.skillSleepingTime = 7000  # 技能CD
        self.lastSkillTime = -self.skillSleepingTime - 1  # 上次技能施放时间（初始值最小为了在开局能释放技能）
        self.skilleffect = 50  # 技能效果
        self.skillcolor = (50, 50, 50)
        self.skilllastedtime = 3000  # 技能持续时间
        self.skillrange = int((self.target.get_rect().width + self.target.get_rect().height) / 2 / 7)  # 技能范围
        self.skillingposition = (-100, -100)  # 技能初始位置
        self.particles = ParticlesGroup()  # 粒子效果
        self.particle_move_length = self.target.get_rect().width / 15  # 粒子移动距离
        self.skill()  # 开局释放技能

    def jump(self):
        if self.jumptimes == 0:
            self.move(0, -20)
        self.jumptimes += 1
        if self.jumptimes <= self.jumpmaxtimes:
            self.jumping = True
            self.jumprest = self.jumpsize
            if self.jumptimes >= 2:  # 显示连跳粒子
                oripos = self.rect.midbottom
                leftpos = oripos[0] - self.particle_move_length, oripos[1]  # 左粒子坐标
                rightpos = oripos[0] + self.particle_move_length, oripos[1]  # 右粒子坐标
                bottompos = oripos[0], oripos[1] + self.particle_move_length  # 下粒子坐标
                size = (self.target.get_rect().width + self.target.get_rect().height) / 2 / 80  # 粒子尺寸
                self.particles.add(Particle(self.target, oripos, leftpos, size, size))
                self.particles.add(Particle(self.target, oripos, rightpos, size, size))
                self.particles.add(Particle(self.target, oripos, bottompos, size, size))

    def move(self, x, y):
        super(Player, self).move(x, y)
        a, b, sw, sh = self.target.get_rect()
        # 着地检测-》重置跳跃次数
        if self.rect.bottom >= sh:
            self.jumptimes = 0
        # 防止超出边缘
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, sw)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, sh)

    def skill(self):  # 技能：保护罩
        nowtime = Base.getTimeMil()
        if nowtime - self.lastSkillTime >= self.skillSleepingTime:  # 时间判定
            self.skillingposition = self.rect.midbottom[0], self.rect.midleft[1]
            self.lastSkillTime = nowtime

    def fall(self, speed):
        if self.jumping:
            up = self.jumprest // self.jumpspeed
            self.jumprest -= up
            self.move(0, -up)
            if self.jumprest < self.jumpspeed:
                self.jumping = False
        else:
            self.move(0, speed)

    def check(self, sprites):
        nowtime = Base.getTimeMil()
        if self.lastSkillTime + self.skilllastedtime <= nowtime:  # 解除保护罩
            self.skillingposition = -self.skillrange, -self.skillrange
        for sprite in sprites:
            nowtime = Base.getTimeMil()
            if sprite.rect.left < self.rect.midtop[0] < sprite.rect.right and \
                    sprite.rect.top < self.rect.midtop[1] < sprite.rect.bottom and \
                    nowtime >= self.lastHurtTime + self.undeadabletime:
                self.lastHurtTime = nowtime
                self.lives -= 1
                return self.lives <= 0

    def update(self, *args, **kwargs):
        super(Player, self).update()
        pygame.draw.circle(self.target, self.skillcolor, self.skillingposition, self.skillrange, random.randint(1, 5))
        self.particles.update()

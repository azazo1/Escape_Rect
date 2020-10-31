# coding=utf-8
import random

from src.Basic import Base, Configuration
import pygame

from src.Char.Character import MyChar


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


# noinspection PyAttributeOutsideInit
class Player(MyChar):

    def __init__(self, targetscreen, width, height, color=(255, 0, 0)):
        super(Player, self).__init__(targetscreen, width, height, color)
        self.initLife()
        self.initMoving()
        self.initFalling()
        self.initJumping()
        self.initRushing()
        self.initParticles()
        self.initSkilling()

    def initLife(self):
        self.lives = self.olives = Configuration.Lives  # 生命数
        self.lastHurtTime = 0
        self.undeadabletime = 500  # 无敌时间

    def initParticles(self):
        self.particles = ParticlesGroup()  # 粒子效果
        self.particle_move_length = self.target.get_rect().width / 15  # 粒子移动距离

    def initRushing(self):
        self.rushing = False
        self.rushingTime = 100  # 冲刺时间
        self.rushSleepTime = 2000  # 冲刺休息时间
        self.lastRushTime = 0  # 上次冲刺时间
        self.rushArc = self.rect.center, self.rect.center

    def initSkilling(self):
        self.skillSleepingTime = 7000  # 技能CD
        self.lastSkillTime = -self.skillSleepingTime - 1  # 上次技能施放时间（初始值最小为了在开局能释放技能）
        self.skilleffect = 50  # 技能效果
        self.skillcolor = (50, 50, 50)
        self.skilllastedtime = 3000  # 技能持续时间
        self.skillrange = int((self.target.get_rect().width + self.target.get_rect().height) / 2 / 7)  # 技能范围
        self.skillingposition = (-100, -100)  # 技能初始位置
        self.skill()  # 开局释放技能

    def initMoving(self):
        x, y = self.target.get_rect()[2:]  # 将玩家安放在屏幕中间
        self.moveto(x // 2 - self.rect.width // 2, y)
        self.moveSpeed = int(self.target.get_rect().width / 1.6)
        self.lastMoveTime = 0

    def initFalling(self):
        self.lastFallTime = 0
        self.fallingSpeed = int(self.target.get_rect().width / (1.4))  # 玩家每秒下降像素

    def initJumping(self):
        self.jumpSize = self.target.get_rect().height // 3
        self.jumprest = 0
        self.jumping = False
        self.jumpspeed = 3  # 越小越快
        self.jumpmaxtimes = 3  # 最大连跳数
        self.jumptimes = 0
        self.lastJumpTime = 0
        self.lastJumpProcess = 0
        self.jumpingSleepTime = 200  # 跳跃时间间隔（防止连跳）
        self.jumpingTime = 300  # 跳跃持续时间

    def rush(self, pos: list):  # 用center位置判断冲刺
        nowTime = Base.getTimeMil()
        if self.lastRushTime + self.rushSleepTime < nowTime or Configuration.NoCD:
            self.jumptimes  = 0
            self.jumping = False
            self.rushing = True
            self.rushArc = self.rect.center, tuple(pos)
            self.lastRushTime = nowTime

    def left(self):
        moveRange = int(self.moveSpeed * Base.getTimeMilPerPage() / 1000)
        self.move(-moveRange, 0)

    def right(self):
        moveRange = int(self.moveSpeed * Base.getTimeMilPerPage() / 1000)
        self.move(moveRange, 0)

    def jump(self):
        if self.lastJumpTime + self.jumpingSleepTime > Base.getTimeMil():
            return
        #if self.jumptimes == 0:
           # self.move(0,-self.target.get_rect().height//5)
        self.jumptimes += 1
        if self.jumptimes <= self.jumpmaxtimes:
            self.lastJumpTime = Base.getTimeMil()
            self.jumping = True
            self.jumprest = self.jumpSize
            if self.jumptimes >= 2:  # 显示连跳粒子
                self.placeParticles()

    def placeParticles(self):
        if not Configuration.ParticlesShowing:
            return
        oripos = self.rect.midbottom
        leftpos = oripos[0] - self.particle_move_length, oripos[1]  # 左粒子坐标
        rightpos = oripos[0] + self.particle_move_length, oripos[1]  # 右粒子坐标
        bottompos = oripos[0], oripos[1] + self.particle_move_length  # 下粒子坐标
        size = (self.target.get_rect().width + self.target.get_rect().height) / 2 / 80  # 粒子尺寸
        self.particles.add(Particle(self.target, oripos, leftpos, size, size))
        self.particles.add(Particle(self.target, oripos, rightpos, size, size))
        self.particles.add(Particle(self.target, oripos, bottompos, size, size))

    def moveto(self, x, y):
        super(Player, self).moveto(x, y)
        a, b, sw, sh = self.target.get_rect()
        # 防止超出边缘
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, sw)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, sh)

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
        if nowtime - self.lastSkillTime >= self.skillSleepingTime or Configuration.NoCD:  # 时间判定
            self.skillingposition = self.rect.center
            self.lastSkillTime = nowtime

    def fall(self):  # 角色位移操作的执行层
        """speed单位为 px/s"""
        nowTime = Base.getTimeMil()
        if self.rushing:
            process = max(((nowTime - self.lastRushTime) / self.rushingTime) ** (1 / 2), 0.1)  # 冲刺进度
            start, end = self.rushArc
            # 计算坐标
            nowPos = [(e - s) * process + s for s, e in zip(start, end)]
            # 使中点落在目标位置上
            nowPos[0] -= self.rect.width // 2
            nowPos[1] -= self.rect.height // 2
            self.moveto(*nowPos)
            self.placeParticles()
            if process >= 1:
                self.rushing = False
        elif self.jumping:
            process = max(((nowTime - self.lastJumpTime) / self.jumpingTime) ** 0.4, 0.1)  # 跳跃进度
            if process < 1:
                up = max(self.jumpSize * (process - self.lastJumpProcess), 1)
                self.move(0, -up)
                self.lastJumpProcess = process
            else:
                self.jumping = False
                self.lastJumpProcess = 0
        else:
            down = int(self.fallingSpeed * (nowTime - self.lastFallTime) / 1000)
            self.move(0, down)
        self.lastFallTime = nowTime

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
                self.lives -= not Configuration.Invincible  # 用了True为1，False为0
                return self.lives <= 0

    def update(self, *args, **kwargs):
        super(Player, self).update()
        pygame.draw.circle(self.target, self.skillcolor, self.skillingposition, self.skillrange,
                           random.randint(1, 5) if Configuration.ParticlesShowing else 1)
        self.particles.update()

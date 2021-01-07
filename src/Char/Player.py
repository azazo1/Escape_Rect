# coding=utf-8
import random
from typing import List, Union

from src.Basic.Base import *
import pygame

from src.Char.Character import MyChar
import src.Char.Enemy as EnemyModule


class Particle(MyChar):
    def __init__(self, targetScreen, position, target_position, width=2, height=2, color=(255, 255, 0)):
        super().__init__(targetScreen, width, height, color)
        self.rect.center = position
        self.tp = target_position
        self.living = True
        self.speed = 5  # 越大越慢
        self.set_alpha(255)

    def update(self, text: str = None):
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
        self.parts: List[Particle] = parts

    def update(self):
        for p in self.parts:
            if not p.living:
                self.parts.remove(p)
                continue
            p.update()

    def flush(self):
        for p in self.parts:
            if not p.living:
                self.parts.remove(p)
                continue
            p.target.blit(p, p.start_pos)

    def add(self, p: Particle):
        self.parts.append(p)


# noinspection PyAttributeOutsideInit
class Player(MyChar):
    """
    TODO 未来的版本不再支持冲刺
    """

    def __init__(self, targetScreen, width, height):
        super(Player, self).__init__(targetScreen, width, height, Con.PlayerColors[0])
        self.initLife()
        self.initMoving()
        self.initFalling()
        self.initJumping()
        # self.initRushing() TODO 新版本不再支持冲刺
        self.initParticles()
        self.initSkilling()
        self.initSound()

    def initSound(self):
        self.rushSound = getSound(Con.RushSound)
        self.jumpSound = getSound(Con.JumpSound)
        self.hurtSound = getSound(Con.HurtSound)
        self.deadSound = getSound(Con.DeadSound)

    def initLife(self):
        self.lives = self.olives = Configuration.Lives  # 生命数
        self.lastHurtTime = 0
        self.invincibleTime = 500  # 无敌时间

    def initParticles(self):
        self.particles = ParticlesGroup()  # 粒子效果
        self.particle_move_length = self.target.get_rect().width / 15  # 粒子移动距离

    # def initRushing(self): TODO 新版本不再支持冲刺
    #     self.rushing = False
    #     self.rushingTime = 100  # 冲刺时间
    #     self.rushSleepTime = 2000  # 冲刺休息时间
    #     self.lastRushTime = 0  # 上次冲刺时间
    #     self.rushArc = self.rect.center, self.rect.center

    def initSkilling(self):
        self.skillSleepingTime = 7000  # 技能CD
        self.lastSkillTime = -self.skillSleepingTime - 1  # 上次技能施放时间（初始值最小为了在开局能释放技能）
        self.skilleffect = 50  # 技能效果
        self.skillcolor = (50, 50, 50)
        self.skilllastedtime = 3000  # 技能持续时间
        self.skillrange = int(sum(self.target.get_size()) / 2 / 7)  # 技能范围
        self.skillPosition = (-100, -100)  # 技能初始位置
        self.skill()  # 开局释放技能

    def initMoving(self):
        x, y = self.target.get_rect()[2:]  # 将玩家安放在屏幕中间
        self.moveto(x // 2, y)
        self.moveSpeed = int(self.target.get_rect().width / 1.6)
        self.lastMoveTime = 0

    def initFalling(self):
        self.lastFallTime = 0
        self.fallingSpeed = int(self.target.get_rect().width / 1.4)  # 玩家每秒下降像素

    def initJumping(self):
        self.jumpSize = self.target.get_rect().height // 3
        self.jumprest = 0
        self.jumping = False
        self.jumpspeed = 3  # 越小越快
        self.jumpmaxtimes = 3  # 最大连跳数
        self.jumpTimes = 0
        self.lastJumpTime = 0
        self.lastJumpProcess = 0
        self.jumpingSleepTime = 200  # 跳跃时间间隔（防止连跳）
        self.jumpingTime = 300  # 跳跃持续时间

    # def rush(self, pos: list):  # 用center位置判断冲刺 TODO 新版本不再支持冲刺
    #     nowTime = getTimeMil()
    #     if self.lastRushTime + self.rushSleepTime < nowTime or Configuration.NoCD:
    #         playSound(self.rushSound)
    #         self.jumpTimes = 0
    #         self.jumping = False
    #         self.rushing = True
    #         self.rushArc = self.rect.center, tuple(pos)
    #         self.lastRushTime = nowTime

    def left(self):
        moveRange = int(self.moveSpeed * getTimeMilPerPage() / 1000)
        self.move(-moveRange, 0)

    def right(self):
        moveRange = int(self.moveSpeed * getTimeMilPerPage() / 1000)
        self.move(moveRange, 0)

    def jump(self):
        if self.lastJumpTime + self.jumpingSleepTime > getTimeMil():
            return
        self.jumpTimes += 1
        if self.jumpTimes <= self.jumpmaxtimes:
            playSound(self.jumpSound)
            self.lastJumpTime = getTimeMil()
            self.jumping = True
            self.jumprest = self.jumpSize
            if self.jumpTimes >= 2:  # 显示连跳粒子
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
            self.jumpTimes = 0
        # 防止超出边缘
        self.rect.left = max(self.rect.left, 0)
        self.rect.right = min(self.rect.right, sw)
        self.rect.top = max(self.rect.top, 0)
        self.rect.bottom = min(self.rect.bottom, sh)

    def skill(self):  # 技能：保护罩
        nowTime = getTimeMil()
        if nowTime - self.lastSkillTime >= self.skillSleepingTime or Configuration.NoCD:  # 时间判定
            self.skillPosition = self.rect.center
            self.lastSkillTime = nowTime

    def calcColor(self):
        per = 1 - (self.lives / self.olives)
        x, y, z = Con.PlayerColors[0]
        a, b, c = Con.PlayerColors[1]
        first = int(x + (a - x) * per)
        second = int(y + (b - y) * per)
        third = int(z + (c - z) * per)
        return first, second, third

    def fall(self):  # 角色位移操作的执行层
        """speed单位为 px/s"""
        nowTime = getTimeMil()
        # if self.rushing: TODO 新版本不再支持冲刺
        #     process = max(((nowTime - self.lastRushTime) / self.rushingTime) ** (1 / 2), 0.1)  # 冲刺进度
        #     start, end = self. rushArc
        #     # 计算坐标
        #     nowPos = [(e - s) * process + s for s, e in zip(start, end)]
        #     # 使中点落在目标位置上
        #     nowPos[0] -= self.rect.width // 2
        #     nowPos[1] -= self.rect.height // 2
        #     self.moveto(*nowPos)
        #     self.placeParticles()
        #     if process >= 1:
        #         self.rushing = False
        if self.jumping:
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

    def checkHurtOrDead(self, enemies: Union[Tuple[EnemyModule.Enemy], List[EnemyModule.Enemy]]):
        """
        检查并处理玩家状态
        :param enemies:
        :return: 返回是否死亡
        """
        nowTime = getTimeMil()
        if self.lastSkillTime + self.skilllastedtime <= nowTime:  # 解除保护罩
            self.skillPosition = -self.skillrange, -self.skillrange
        for enemy in enemies:
            nowTime = getTimeMil()
            if (LCenterInR(self, enemy) and
                    nowTime >= self.lastHurtTime + self.invincibleTime):
                playSound(self.hurtSound)
                self.lastHurtTime = nowTime
                self.lives -= not Configuration.Invincible  # 用了True为1，False为0
                dead = self.lives <= 0
                if dead:
                    playSound(self.deadSound)
                    zombie = EnemyModule.Enemy(self.target, *self.get_size())
                    zombie.moveto(*self.pos)
                    self.group.addEnemy(zombie)
                    super(Player, self).moveto(*self.get_size())
                self.alive = not dead
                return dead

    def update(self, text: str = None):
        self.color = self.calcColor()
        super(Player, self).update(text=f'{self.seq}')
        pygame.draw.circle(self.target, self.skillcolor, self.skillPosition, self.skillrange,
                           random.randint(1, 5) if Configuration.ParticlesShowing else 1)
        self.particles.update()
        self.particles.flush()

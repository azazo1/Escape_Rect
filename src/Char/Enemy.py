# coding=utf-8
import math
from random import randint, choice
from src.Char.Character import MyChar
import src.Char.Player as PlayerModule
from src.Basic.Base import *


class Enemy(MyChar):
    def __init__(self, targetScreen, width, height, color=(0, 0, 255)):
        super().__init__(targetScreen, width, height, color)
        if randint(0, 1):  # 随机从左上角或右上角出现
            self.rect.right = targetScreen.get_rect()[2]
        self.distanse = (sum(self.target.get_size())
                         // 6)  # 随机移动到玩家的最大距离（越大玩家越安全）
        self.movetimes = 0
        self.maxSleepTime = 1000  # 移动最大休息时间
        self.sleepTime = randint(0, self.maxSleepTime)
        self.moving = False
        self.lastMoveTime = 0
        self.movingTime = 700  # 移动持续时间
        self.moveArc = (self.rect.center, self.rect.center)  # 移动路径

    def checkSkilled(self):
        for player in self.playerHandler.getPlayers():
            sx, sy = player.skillPosition
            srange = player.skillrange
            x, y = self.rect.center
            square_sum = (sx - x) ** 2 + (sy - y) ** 2
            if square_sum < srange ** 2:  # 在技能范围内
                effect = player.skilleffect
                distance = math.sqrt(square_sum)
                cos = distance / ((x - sx) or 0.001)
                sin = distance / ((y - sy) or 0.001)
                self.smoothTo(effect * cos + x, effect * sin + y)

    def summonPoint(self, player=None, hit=False):
        """
        为Enemy对象生成一个移动目标
        :param player: 被攻击的玩家为None则随机抽取玩家
        :param hit: 直接攻击玩家
        :return:
        """
        str(player)  # type: PlayerModule.Player
        if not player:
            alivePlayers = list(filter(lambda a: a, self.group.players))
            if not alivePlayers:
                return
            player = choice(alivePlayers)  # 选中顶层管理器里的players
        d = int(self.distanse) if not hit else 0  # 目标位置与玩家的距离，为零则去到玩家位置
        l1, l2 = randint(-d, d), randint(-d, d)
        x, y = player.rect.center
        targetx = l1 + x
        targety = l2 + y
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
        self.lastMoveTime = getTimeMil()

    def update(self, text: str = None):
        """
        更新敌人的状态
        :return:
        """
        self.movingTime = max(-0.04 * getTimeMil() + 2000,
                              150)  # 随时间增加movingTime越小，最小为max中的定者
        if (
                randint(0, 1000) < 15
                and ((getTimeMil() - self.lastMoveTime) > self.sleepTime)
                and not self.moving
        ):
            self.summonPoint()
            self.movetimes += 1
        else:
            self.checkSkilled()
        self.smoothMove()
        super(Enemy, self).update(
            text=f'{self.sleepTime}' if Configuration.EnemySleepTimeShowing else '')

    def smoothMove(self):
        if self.moving:
            nowTime = getTimeMil()
            process = max(((nowTime - self.lastMoveTime) / self.movingTime) ** 0.3, 0.01)  # 冲刺进度
            start, end = self.moveArc
            # 计算坐标
            nowPos = [(e - s) * process + s for s, e in zip(start, end)]
            self.moveto(*nowPos)
            if process >= 1:
                self.moving = False

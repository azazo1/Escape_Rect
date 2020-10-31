# coding=utf-8
import pygame

from src.Basic import Base
from src.Char import Player, Enemy


class GroupManager(pygame.sprite.Group):
    endProcess = 20  # 胜利Process

    def __init__(self, targetscreen):
        super(GroupManager, self).__init__()
        self.lasttime = Base.getTimeMil()
        self.buttons = []
        # noinspection PyTypeChecker
        self.player: Player.Player = None
        self.process = 0  # 初始Process
        self.Processincrease = 0.05  # Process增长速度
        self.winnerProcess = 35  # 胜利MovePer
        self.target: Base.MyFrame = targetscreen

        self.rightkey = [pygame.K_d, pygame.K_RIGHT]
        self.leftkey = [pygame.K_a, pygame.K_LEFT]
        self.downkey = [pygame.K_s, pygame.K_DOWN]
        self.upkey = [pygame.K_w, pygame.K_UP]
        self.jumpkey = [pygame.K_SPACE, pygame.K_w, pygame.K_UP]
        self.playerlastmovetime = Base.getTimeMil()  # 玩家上次移动时间
        self.playermaxstatictime = 5000  # 玩家最大静止时间
        self.playlastposition = (0, 0)

    def setplayer(self, player):
        self.player = player

    def updateCondition(self, *args, **kwargs):
        nowtime = Base.getTimeMil()
        if nowtime - self.lasttime > 1000:  # 增长process
            self.process += self.Processincrease
            self.lasttime = nowtime

        for b in self.buttons:  # Button判定
            b: Base.Button
            c = b.command
            if b.checkPressed():
                (self.player.left, self.player.right, self.player.jump, self.player.skill)[c]()  # 此处顺序按照按钮说明排列

        # 检测键盘
        keys = pygame.key.get_pressed()
        if self.checkkey(keys, self.rightkey):
            self.player.right()
        if self.checkkey(keys, self.leftkey):
            self.player.left()
        if self.checkkey(keys, self.downkey):  # 技能判定
            self.player.skill()
        if self.checkkey(keys, self.jumpkey):  # 跳跃判定
            self.player.jump()
        if pygame.mouse.get_pressed(3)[2]:  # 冲刺判定
            targetPos = [ep - tp for tp, ep in zip(self.target.pos, pygame.mouse.get_pos())]
            self.player.rush(targetPos)

        # 检测玩家是否移动
        if self.playlastposition != self.player.rect.topleft:
            self.playerlastmovetime = nowtime  # 重置静止时间
            self.playlastposition = self.player.rect.topleft

        # 玩家掉落和跳跃的动作
        self.player.fall()

        # 攻击静止玩家
        if nowtime > self.playerlastmovetime + self.playermaxstatictime:
            for sprite in self.sprites():
                sprite: Enemy.Enemy
                if not sprite.moving:
                    sprite.summonPoint(True)
        return self.process, self.process > self.winnerProcess

    def refresh(self):
        # 刷新
        self.player.update()
        super(GroupManager, self).update()

    def checkkey(self, keys, direct):
        for i in direct:
            try:
                if keys[i]:
                    return True
            except Exception:
                pass

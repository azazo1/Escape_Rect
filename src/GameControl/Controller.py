# coding=utf-8
from src.Basic.Base import *
from src.Char import Player, Enemy


class GroupManager(pygame.sprite.Group):
    endProcess = 20  # 胜利Process

    def __init__(self, targetScreen):
        super(GroupManager, self).__init__()
        self.lastTime = getTimeMil()
        self.buttons = []
        # noinspection PyTypeChecker
        self.player: Player.Player = None
        self.process = 0  # 初始Process
        self.processIncrease = 0.05  # Process增长速度
        self.winnerProcess = 35  # 胜利MovePer
        self.target: MyFrame = targetScreen

        self.rightkey = [pygame.K_d, pygame.K_RIGHT]
        self.leftkey = [pygame.K_a, pygame.K_LEFT]
        self.downkey = [pygame.K_s, pygame.K_DOWN]
        self.upkey = [pygame.K_w, pygame.K_UP]
        self.jumpkey = [pygame.K_SPACE, pygame.K_w, pygame.K_UP]
        self.playerlastmovetime = getTimeMil()  # 玩家上次移动时间
        self.playermaxstatictime = 5000  # 玩家最大静止时间
        self.playlastposition = (0, 0)



    def setplayer(self, player):
        self.player = player

    def updateCondition(self, *args, **kwargs):
        nowtime = getTimeMil()
        horizontalWalk = False
        if nowtime - self.lastTime > 1000:  # 增长process
            self.process += self.processIncrease
            self.lastTime = nowtime

        for b in self.buttons:  # Button判定
            b: Button
            c = b.command
            if b.checkPressed():
                (self.player.left, self.player.right, self.player.jump, self.player.skill)[c]()  # 此处顺序按照按钮说明排列
                if c in [0, 1]:
                    horizontalWalk = True


        # 检测键盘
        keys = pygame.key.get_pressed()
        if not horizontalWalk and self.checkKey(keys, self.rightkey):  # 向右走
            self.player.right()
        if not horizontalWalk and self.checkKey(keys, self.leftkey):  # 向左走
            self.player.left()
        if self.checkKey(keys, self.downkey):  # 技能判定
            self.player.skill()
        if self.checkKey(keys, self.jumpkey):  # 跳跃判定
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

    def flush(self):
        # 刷新
        self.player.update()
        super(GroupManager, self).update()

    @staticmethod
    def checkKey(keys, direct):
        for i in direct:
            try:
                if keys[i]:
                    return True
            except Exception:
                pass

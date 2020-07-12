# coding = utf-8
import pygame
import time


class GroupManager(pygame.sprite.Group):
    def __init__(self, targetscreen):
        super(GroupManager, self).__init__()
        self.lasttime = time.time()
        self.player = None
        self.moveper = self.omoveper = 2  # 初始移动概率
        self.moveperincrease = 0.05  # 移动概率增长速度
        self.winnermoveper = 35 # 胜利移动概率
        self.target = targetscreen
        self.g = int(targetscreen.get_rect().height / 30)
        self.x, self.y = self.target.get_rect().size
        self.movespeed = int(self.target.get_rect().width / 70)  # 根据屏幕宽度调整移动速度
        self.rightkey = [pygame.K_d, pygame.K_RIGHT, 1073741903, 54]
        self.leftkey = [pygame.K_a, pygame.K_LEFT, 1073741904, 52]
        self.downkey = [pygame.K_s, pygame.K_DOWN, 1073741905, 56]
        self.upkey = [pygame.K_w, pygame.K_UP, 1073741906, 50]
        self.jumpkey = [pygame.K_SPACE, pygame.K_w, pygame.K_UP, 1073741906, 50]
        self.playerlastmovetime = time.time()  # 玩家上次移动时间
        self.playermaxstatictime = 5  # 玩家最大静止时间
        self.playlastposition = (0, 0)

    def setplayer(self, player):
        self.player = player

    def update(self, events, *args, **kwargs):
        nowtime = time.time()
        if nowtime - self.lasttime > 1:
            self.moveper += self.moveperincrease
            self.lasttime = nowtime
        mouseleft = pygame.mouse.get_pressed()[0]
        sw, sh = self.target.get_rect()[2:]
        for e in events:
            if e.type == pygame.KEYDOWN:
                self.moveper += self.moveperincrease / 2
                if e.key in self.jumpkey:  # 跳跃判定
                    self.player.jump()
            if e.type == pygame.MOUSEMOTION or e.type == pygame.MOUSEBUTTONDOWN:
                self.x, self.y = e.pos

        # 玩家移动
        keys = pygame.key.get_pressed()
        if self.checkkey(keys, self.rightkey):
            self.player.move(self.movespeed, 0)

        if self.checkkey(keys, self.leftkey):
            self.player.move(-self.movespeed, 0)

        if self.checkkey(keys, self.downkey):  # 使用技能
            self.player.skill()

        # 向上移动暂时无用
        # if self.checkkey(keys, self.upkey):
        #     self.player.move(0, -self.movespeed)

        # 检测玩家是否移动
        if self.playlastposition != self.player.rect.topleft:
            self.playerlastmovetime = nowtime  # 重置静止时间
            self.playlastposition = self.player.rect.topleft

        # 玩家掉落和跳跃的动作
        self.player.fall(self.g)

        if nowtime > self.playerlastmovetime + self.playermaxstatictime:
            for sprite in self.sprites():
                x, y = self.player.rect.topleft
                sprite.moveto(int(x), int(y))

        # 刷新
        self.player.update()
        super(GroupManager, self).update()
        return self.moveper, self.moveper > self.winnermoveper

    def checkkey(self, keys, direct):
        for i in direct:
            if keys[i]:
                return True

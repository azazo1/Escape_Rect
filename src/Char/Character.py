# coding=utf-8
from src.Basic.Base import *
import src.GameControl.Controller as Controller


class MyChar(pygame.Surface):
    def __init__(self, targetScreen, width, height, color):
        super(MyChar, self).__init__((int(width), int(height)))
        self.target = targetScreen
        self.color = color
        self.alive = True
        self.seq = 0
        self._rect = self.get_rect()
        self.font = getFont(Con.Font, int(targetScreen.get_size()[0] / Configuration.FontRelation))
        self.belong = None  # type: Controller.CharHandler

    def __bool__(self):
        return self.alive

    @property
    def group(self):
        """
        :return: 最顶层的管理器
        """
        return self.belong.belong  # type: Controller.GroupManager

    @property
    def playerHandler(self):
        """
        :return: 玩家管理器
        """
        return self.group.playerHandler  # type: Controller.PlayerHandler

    @property
    def enemyHandler(self):
        """
        :return: 敌人管理器
        """
        return self.group.enemyHandler  # type: Controller.EnemyHandler

    def get_seq(self):
        """返回自身在管理器中的索引，别用太多次"""
        self.seq = self.belong.index(self)
        return self.seq

    @property
    def pos(self):
        """返回中部坐标"""
        return self.rect.center

    @property
    def start_pos(self):
        """返回左上坐标"""
        return self.rect.topleft

    @property
    def rect(self):
        return self._rect

    @rect.setter
    def rect(self, other):
        self._rect = other

    def moveto(self, x, y):
        """中部坐标"""
        self.rect.center = x, y

    def move(self, x, y):
        self.rect.centerx += x
        self.rect.centery += y

    def update(self, text: str = None):
        self.fill(Con.BackGround)
        pygame.draw.rect(self, self.color, [0, 0, *self.get_size()])
        if text:
            surfaceText = self.font.render(text, True, (255, 255, 255))
            w, h = self.get_size()
            sw, sh = surfaceText.get_size()
            # 适配大小
            if sw > w:
                ratio = w / sw
                size = (int(sw * ratio), int(sh * ratio))
                surfaceText = pygame.transform.scale(surfaceText, size)
            elif sh > h:
                ratio = h / sh
                size = (int(sw * ratio), int(sh * ratio))
                surfaceText = pygame.transform.scale(surfaceText, size)
            self.blit(surfaceText, (0, 0))


class Movable(MyChar):
    """TODO 加速度"""

    def __init__(self, targetScreen, width, height, color):
        super().__init__(targetScreen, width, height, color)
